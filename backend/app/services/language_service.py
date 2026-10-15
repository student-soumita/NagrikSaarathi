"""
Multilingual Service Engine for NagrikSaarathi.

Implements the three-layer language engine architecture:
  Layer A: Stored localized guidance in the database (with review status).
  Layer B: Optional dynamic language provider (e.g. BHASHINI) with timeouts.
  Layer C: Safe fallback (never masquerade English as the target language;
           clearly communicate missing content and direct to human assistance).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import FormField, Language, TranslationReview
from backend.app.schemas.assist import ExplainResponse
from backend.app.services.bhashini_adapter import BhashiniAdapter


class LanguageService:
    def __init__(self, bhashini_adapter: Optional[BhashiniAdapter] = None):
        self.adapter = bhashini_adapter or BhashiniAdapter()

    async def get_field_explanation(
        self,
        db: Session,
        scheme_id: int,
        field_key: str,
        target_language: str,
    ) -> Optional[ExplainResponse]:
        """
        Produce localized guidance across Layer A, Layer B, and Layer C.
        """
        # 1. Fetch FormField from database
        field = db.execute(
            select(FormField).where(
                FormField.scheme_id == scheme_id,
                FormField.field_key == field_key,
            )
        ).scalar_one_or_none()

        if not field:
            return None

        # 2. Check if target language exists and is configured
        lang = db.execute(
            select(Language).where(Language.language_code == target_language)
        ).scalar_one_or_none()

        lang_name = lang.native_name if lang else target_language

        # 3. Retrieve translation review status from Layer A
        review = db.execute(
            select(TranslationReview).where(
                TranslationReview.resource_type == "form_field",
                TranslationReview.resource_key == field_key,
                TranslationReview.language_code == target_language,
            )
        ).scalar_one_or_none()

        translation_status = review.translation_status if review else "draft"
        is_reviewed = translation_status in ("reviewed", "approved")

        # Original baseline label (prefer target language, then english, then hindi)
        original_label = (
            field.labels_by_language.get(target_language)
            or field.labels_by_language.get("en")
            or field.labels_by_language.get("hi")
            or next(iter(field.labels_by_language.values()), field_key)
        )

        # 4. Check Layer A: Stored localized content
        stored_label = field.labels_by_language.get(target_language)
        stored_expl = field.explanations_by_language.get(target_language)
        stored_inst = field.instructions_by_language.get(target_language)

        if stored_label and stored_expl:
            # Layer A Success: Stored database guidance exists
            return ExplainResponse(
                scheme_id=scheme_id,
                field_key=field_key,
                target_language=target_language,
                original_label=original_label,
                localized_label=stored_label,
                localized_explanation=stored_expl,
                localized_instruction=stored_inst or "",
                validation_guidance=field.validation_rules,
                source_reference=field.source_reference,
                translation_status=translation_status,
                is_reviewed=is_reviewed,
                is_fallback=False,
                provider_used="database_store",
                human_assistance_path=None,
            )

        # 5. Layer B: Check dynamic translation provider if configured
        if self.adapter.is_configured:
            base_text_to_translate = stored_expl or next(iter(field.explanations_by_language.values()), "")
            if base_text_to_translate:
                dynamic_expl = await self.adapter.translate_text(
                    text=base_text_to_translate,
                    source_lang="hi",
                    target_lang=target_language,
                )
                if dynamic_expl:
                    return ExplainResponse(
                        scheme_id=scheme_id,
                        field_key=field_key,
                        target_language=target_language,
                        original_label=original_label,
                        localized_label=stored_label or original_label,
                        localized_explanation=dynamic_expl,
                        localized_instruction=stored_inst or "",
                        validation_guidance=field.validation_rules,
                        source_reference=field.source_reference,
                        translation_status="draft",  # machine translation is always draft
                        is_reviewed=False,
                        is_fallback=False,
                        provider_used="bhashini",
                        human_assistance_path=None,
                    )

        # 6. Layer C: Safe Fallback
        # If content is unavailable in the selected language:
        # Do NOT silently pretend English is the selected language!
        # Clearly identify the limitation and offer human assistance path.
        fallback_label = (
            field.labels_by_language.get(target_language)
            or field.labels_by_language.get("en")
            or field.labels_by_language.get("hi")
            or original_label
        )
        missing_label_notice = fallback_label

        if target_language == "hi":
            missing_expl_notice = (
                f"इस भाषा ({lang_name}) में इस फ़ील्ड का आधिकारिक विवरण अभी सत्यापित नहीं है। "
                f"मानक आधिकारिक मार्गदर्शन नीचे प्रदर्शित किया जा रहा है।"
            )
            default_inst = "कृपया सहायता केंद्र या मूल दस्तावेज़ देखें।"
            human_help = "सहायता डेस्क से संपर्क करें या आधिकारिक सरकारी प्रपत्र देखें।"
        elif target_language == "bn":
            missing_expl_notice = (
                f"এই ভাষায় ({lang_name}) এই ফিল্ডের সম্পূর্ণ বিবরণ প্রক্রিয়াধীন রয়েছে। "
                f"Official verified guidance for this field in '{lang_name}' is currently in verification. "
                f"মানক সরকারি নির্দেশিকা নিচে প্রদর্শিত হচ্ছে।"
            )
            default_inst = "অনুগ্রহ করে নাগরিক সহায়তা কেন্দ্র বা মূল নথি দেখুন।"
            human_help = "সহায়তা ডেস্কে যোগাযোগ করুন অথবা সরকারি নির্দেশিকা দেখুন।"
        elif target_language == "te":
            missing_expl_notice = (
                f"ఈ భాషలో ({lang_name}) ఈ ఫీల్డ్ యొక్క అధికారిక మార్గదర్శకత్వం సమీక్షలో ఉంది. "
                f"Official verified guidance for this field in '{lang_name}' is currently in verification. "
                f"ప్రామాణిక వివరాలు క్రింద ఇవ్వబడ్డాయి."
            )
            default_inst = "దయచేసి సహాయ కేంద్రాన్ని లేదా అసలు పత్రాలను చూడండి."
            human_help = "సహాయ కేంద్రాన్ని సంప్రదించండి లేదా అధికారిక పత్రాలను పరిశీలించండి."
        elif target_language == "ta":
            missing_expl_notice = (
                f"இந்த மொழியில் ({lang_name}) இந்த புலத்திற்கான சரிபார்க்கப்பட்ட வழிகாட்டுதல் மதிப்பாய்வில் உள்ளது. "
                f"Official verified guidance for this field in '{lang_name}' is currently in verification."
            )
            default_inst = "தயவுசெய்து உதவி மையத்தை அல்லது அசல் ஆவணங்களைப் பார்க்கவும்."
            human_help = "குடிமக்கள் உதவி மையத்தைத் தொடர்பு கொள்ளவும்."
        else:
            missing_expl_notice = (
                f"Official verified guidance for this field in '{lang_name}' is currently in verification. "
                f"Standard scheme guidance is displayed below."
            )
            default_inst = "Please refer to the citizen helpdesk or official scheme document."
            human_help = "Please request human assistance at the citizen assistance desk or refer to verified official scheme documents."

        return ExplainResponse(
            scheme_id=scheme_id,
            field_key=field_key,
            target_language=target_language,
            original_label=original_label,
            localized_label=missing_label_notice,
            localized_explanation=missing_expl_notice,
            localized_instruction=stored_inst or default_inst,
            validation_guidance=field.validation_rules,
            source_reference=field.source_reference,
            translation_status="missing",
            is_reviewed=False,
            is_fallback=True,
            provider_used="safe_fallback",
            human_assistance_path=human_help,
        )

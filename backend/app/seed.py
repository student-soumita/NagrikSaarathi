"""
NagrikSaarathi — Idempotent Seed Script

Populates:
1. All 22 languages of the Eighth Schedule of the Indian Constitution.
2. A clearly-labelled **fictional** Demo Scholarship Application scheme with
   official verification metadata, URLs, and localized guidance.
3. Structured eligibility requirements with typed criteria and thresholds.
4. Required and conditional document requirements with condition rules.
5. Step-by-step application instructions for guided self-application.
6. Form fields with localized labels, explanations, instructions, examples,
   and validation guidance.
7. Simulated analytics sessions and events (all marked ``is_demo=True``).
8. Translation-review records distinguishing reviewed from draft content.
9. Initial demonstration user accounts for role testing.

⚠  DISCLAIMER
--------------
*  The "Demo Scholarship Application" is **entirely fictional** and does
   not represent any real government scheme.
*  All simulated sessions / events are synthetic test data and must
   **never** be presented as real public-sector statistics.
*  Speech-capability flags reflect realistic availability; languages
   without validated provider support are marked ``False``.

Running
-------
    python -m backend.app.seed          # from project root
    python -m backend.app.seed --reset  # drop + recreate + seed
"""

from __future__ import annotations

import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import inspect, select

from backend.app.config import get_settings
from backend.app.database import get_engine, get_session_factory
from backend.app.models import (
    BARRIER_CATEGORIES,
    EVENT_TYPES,
    AssistedSession,
    Base,
    FormField,
    GovernmentScheme,
    Language,
    SchemeApplicationStep,
    SchemeDocumentRequirement,
    SchemeEligibilityRequirement,
    SessionEvent,
    TranslationReview,
    User,
)
from backend.app.services.auth_service import (
    DEMO_CITIZEN_PASSWORD,
    DEMO_OFFICIAL_PASSWORD,
    hash_password,
)


# ── Language seed data (22 Eighth Schedule languages) ───────────────────

LANGUAGES: list[dict] = [
    {"language_code": "as",  "english_name": "Assamese",        "native_name": "অসমীয়া",         "writing_system": "Eastern Nagari (Assamese)", "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "bn",  "english_name": "Bengali",         "native_name": "বাংলা",           "writing_system": "Eastern Nagari (Bengali)",  "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "brx", "english_name": "Bodo",            "native_name": "बड़ो",             "writing_system": "Devanagari",                "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "doi", "english_name": "Dogri",           "native_name": "डोगरी",            "writing_system": "Devanagari",                "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "gu",  "english_name": "Gujarati",        "native_name": "ગુજરાતી",          "writing_system": "Gujarati",                  "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "hi",  "english_name": "Hindi",           "native_name": "हिन्दी",            "writing_system": "Devanagari",                "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "kn",  "english_name": "Kannada",         "native_name": "ಕನ್ನಡ",            "writing_system": "Kannada",                   "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "ks",  "english_name": "Kashmiri",        "native_name": "कॉशुर / كٲشُر",     "writing_system": "Devanagari / Perso-Arabic", "direction": "rtl", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "kok", "english_name": "Konkani",         "native_name": "कोंकणी",           "writing_system": "Devanagari",                "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "mai", "english_name": "Maithili",        "native_name": "मैथिली",            "writing_system": "Devanagari",                "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "ml",  "english_name": "Malayalam",       "native_name": "മലയാളം",          "writing_system": "Malayalam",                 "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "mni", "english_name": "Manipuri (Meitei)", "native_name": "মৈতৈলোন্",         "writing_system": "Meitei Mayek / Bengali",    "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "mr",  "english_name": "Marathi",         "native_name": "मराठी",            "writing_system": "Devanagari",                "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "ne",  "english_name": "Nepali",          "native_name": "नेपाली",            "writing_system": "Devanagari",                "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "or",  "english_name": "Odia",            "native_name": "ଓଡ଼ିଆ",            "writing_system": "Odia",                      "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "pa",  "english_name": "Punjabi",         "native_name": "ਪੰਜਾਬੀ",           "writing_system": "Gurmukhi",                  "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "sa",  "english_name": "Sanskrit",        "native_name": "संस्कृतम्",          "writing_system": "Devanagari",                "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "sat", "english_name": "Santali",         "native_name": "ᱥᱟᱱᱛᱟᱲᱤ",          "writing_system": "Ol Chiki",                  "direction": "ltr", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "sd",  "english_name": "Sindhi",          "native_name": "سنڌي / सिन्धी",     "writing_system": "Perso-Arabic / Devanagari", "direction": "rtl", "supports_text": True, "supports_speech_recognition": False, "supports_text_to_speech": False},
    {"language_code": "ta",  "english_name": "Tamil",           "native_name": "தமிழ்",            "writing_system": "Tamil",                     "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "te",  "english_name": "Telugu",          "native_name": "తెలుగు",           "writing_system": "Telugu",                    "direction": "ltr", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
    {"language_code": "ur",  "english_name": "Urdu",            "native_name": "اردو",             "writing_system": "Perso-Arabic (Nastaliq)",   "direction": "rtl", "supports_text": True, "supports_speech_recognition": True,  "supports_text_to_speech": True},
]


# ── Demo scheme field content ──────────────────────────────────────────

DEMO_FIELDS: list[dict] = [
    {
        "field_key": "applicant_name",
        "field_type": "text",
        "required": True,
        "sort_order": 1,
        "labels": {
            "en": "Applicant Full Name",
            "hi": "आवेदक का नाम",
            "bn": "আবেদনকারীর নাম",
            "ta": "விண்ணப்பதாரரின் பெயர்",
            "te": "దరఖాస్తుదారు పేరు",
            "mr": "अर्जदाराचे नाव",
            "gu": "અરજદારનું નામ",
            "kn": "ಅರ್ಜಿದಾರರ ಹೆಸರು",
            "ml": "അപേക്ഷകന്റെ പേര്",
            "pa": "ਅਰਜ਼ੀਕਰਤਾ ਦਾ ਨਾਮ",
            "or": "ଆବେଦନକାରୀଙ୍କ ନାମ",
            "ur": "درخواست دہندہ کا نام",
            "as": "আবেদনকাৰীৰ নাম",
            "ne": "आवेदकको नाम",
            "kok": "अर्जदाराचें नांव",
            "sd": "درخواست ڏيندڙ جو نالو",
            "ks": "درخواست گزار ناو",
            "mai": "आवेदकक नाम",
            "doi": "अर्जीदार दा नां",
            "brx": "बिनानथि खालामनायनि मुं",
            "mni": "অনুরোধকারীর নাম",
            "sa": "आवेदकस्य नाम",
            "sat": "ᱟᱨᱡᱤᱛ ᱨᱮᱱ ᱧᱩᱛᱩᱢ",
        },
        "explanations": {
            "en": "Enter your full name exactly as it appears on official government identity documents.",
            "hi": "अपना पूरा नाम जैसा कि आधिकारिक दस्तावेज़ों में है, दर्ज करें।",
            "bn": "সরকারি নথিতে যেমন আছে তেমন পুরো নাম লিখুন।",
            "ta": "உங்கள் அரசு ஆவணங்களில் உள்ள முழுப் பெயரை உள்ளிடவும்.",
            "te": "మీ అధికారిక పత్రాలలో ఉన్న పూర్తి పేరు నమోదు చేయండి.",
            "mr": "अधिकृत कागदपत्रांमध्ये जसे आहे तसे पूर्ण नाव लिहा.",
        },
        "instructions": {
            "en": "Please provide both first name and last name.",
            "hi": "कृपया पहला नाम और अंतिम नाम दोनों लिखें।",
            "bn": "দয়া করে প্রথম নাম ও শেষ নাম দুটোই লিখুন।",
            "ta": "தயவுசெய்து முதல் பெயர் மற்றும் கடைசி பெயர் இரண்டையும் எழுதுங்கள்.",
            "te": "దయచేసి మొదటి పేరు మరియు చివరి పేరు రెండూ రాయండి.",
            "mr": "कृपया पहिले नाव आणि आडनाव दोन्ही लिहा.",
        },
        "examples": {
            "en": "e.g. Ramesh Kumar Sharma",
            "hi": "उदा. रमेश कुमार शर्मा",
            "bn": "যেমন: রমেশ কুমার শর্মা",
        },
        "validation_guidance": {
            "en": "Must be between 2 and 200 characters containing letters, spaces, dots, or hyphens.",
            "hi": "न्यूनतम 2 और अधिकतम 200 अक्षर; केवल वैध नाम वर्ण स्वीकार्य हैं।",
        },
        "validation_rules": {"min_length": 2, "max_length": 200, "pattern": "^[\\p{L}\\s.'-]+$"},
    },
    {
        "field_key": "institution_name",
        "field_type": "text",
        "required": True,
        "sort_order": 2,
        "labels": {
            "en": "Institution / College Name",
            "hi": "संस्था का नाम",
            "bn": "প্রতিষ্ঠানের নাম",
            "ta": "நிறுவனத்தின் பெயர்",
            "te": "సంస్థ పేరు",
            "mr": "संस्थेचे नाव",
            "gu": "સંસ્થાનું નામ",
            "kn": "ಸಂಸ್ಥೆಯ ಹೆಸರು",
            "ml": "സ്ഥാപനത്തിന്റെ പേര്",
            "pa": "ਸੰਸਥਾ ਦਾ ਨਾਮ",
            "or": "ଅନୁଷ୍ଠାନର ନାମ",
            "ur": "ادارے کا نام",
            "as": "অনুষ্ঠানৰ নাম",
            "ne": "संस्थाको नाम",
            "kok": "संस्थेचें नांव",
            "sd": "اداري جو نالو",
            "ks": "ادارٕ ناو",
            "mai": "संस्थाक नाम",
            "doi": "संस्था दा नां",
            "brx": "लोगोफोरनि मुं",
            "mni": "প্রতিষ্ঠানের নাম",
            "sa": "संस्थायाः नाम",
            "sat": "ᱥᱟᱶᱥᱛᱷᱟ ᱨᱮᱱ ᱧᱩᱛᱩᱢ",
        },
        "explanations": {
            "en": "The registered name of the school or college you are currently studying in.",
            "hi": "वह स्कूल या कॉलेज जहां आप अभी पढ़ रहे हैं।",
            "bn": "আপনি বর্তমানে যে স্কুল বা কলেজে পড়ছেন।",
            "ta": "நீங்கள் தற்போது படிக்கும் பள்ளி அல்லது கல்லூரி.",
            "te": "మీరు ప్రస్తుతం చదువుతున్న పాఠశాల లేదా కళాశాల.",
            "mr": "तुम्ही सध्या ज्या शाळा किंवा महाविद्यालयात शिकत आहात.",
        },
        "instructions": {
            "en": "Provide the full institution name without abbreviations.",
            "hi": "पूरा संस्था नाम भरें, संक्षिप्त नाम नहीं।",
            "bn": "সম্পূর্ণ প্রতিষ্ঠানের নাম লিখুন, সংক্ষিপ্ত নাম নয়।",
            "ta": "முழுமையான நிறுவனப் பெயரை எழுதுங்கள், சுருக்கம் வேண்டாம்.",
        },
        "examples": {
            "en": "e.g. Government Engineering College, Pune",
            "hi": "उदा. राजकीय इंजीनियरिंग कॉलेज, पुणे",
        },
        "validation_guidance": {
            "en": "Between 2 and 300 characters representing the full recognized institution name.",
            "hi": "मान्यता प्राप्त कॉलेज अथवा स्कूल का पूरा आधिकारिक नाम।",
        },
        "validation_rules": {"min_length": 2, "max_length": 300},
    },
    {
        "field_key": "annual_family_income",
        "field_type": "number",
        "required": True,
        "sort_order": 3,
        "labels": {
            "en": "Annual Family Income (INR)",
            "hi": "वार्षिक पारिवारिक आय (₹)",
            "bn": "বার্ষিক পারিবারিক আয় (₹)",
            "ta": "ஆண்டு குடும்ப வருமானம் (₹)",
            "te": "వార్షిక కుటుంబ ఆదాయం (₹)",
            "mr": "वार्षिक कौटुंबिक उत्पन्न (₹)",
            "gu": "વાર્ષિક કુટુંબ આવક (₹)",
            "kn": "ವಾರ್ಷಿಕ ಕುಟುಂಬ ಆದಾಯ (₹)",
            "ml": "വാർഷിക കുടുംബ വരുമാനം (₹)",
            "pa": "ਸਲਾਨਾ ਪਰਿਵਾਰਕ ਆਮਦਨ (₹)",
            "or": "ବାର୍ଷିକ ପାରିବାରିକ ଆୟ (₹)",
            "ur": "سالانہ خاندانی آمدنی (₹)",
            "as": "বাৰ্ষিক পৰিয়ালৰ আয় (₹)",
            "ne": "वार्षिक पारिवारिक आय (₹)",
            "kok": "वर्सुकी कुटुंब उत्पन्न (₹)",
            "sd": "سالياني خانداني آمدني (₹)",
            "ks": "سالانٕ خاندانی آمدٕنی (₹)",
            "mai": "वार्षिक पारिवारिक आय (₹)",
            "doi": "सालाना परिवारिक आमदनी (₹)",
            "brx": "बोसोरारि हानजानि जागायनाय (₹)",
            "mni": "ইয়ুংগী পরিবারগী থাবক (₹)",
            "sa": "वार्षिकं पारिवारिकम् आयः (₹)",
            "sat": "ᱥᱮᱨᱢᱟ ᱜᱤᱫᱨᱟᱹ ᱟᱹᱨᱡᱟᱹᱣ (₹)",
        },
        "explanations": {
            "en": "Gross total annual earnings of your entire household in Rupees.",
            "hi": "आपके पूरे परिवार की कुल वार्षिक आय रुपयों में।",
            "bn": "রুপিতে আপনার পরিবারের মোট বার্ষিক আয়।",
            "ta": "ரூபாய்களில் உங்கள் குடும்பத்தின் மொத்த ஆண்டு வருமானம்.",
            "te": "మీ కుటుంబం యొక్క మొత్తం వార్షిక ఆదాయం రూపాయలలో.",
            "mr": "तुमच्या कुटुंबाचे एकूण वार्षिक उत्पन्न रुपयांत.",
        },
        "instructions": {
            "en": "Please enter numbers only without currency symbols or commas.",
            "hi": "कृपया केवल अंक दर्ज करें, रुपये का चिह्न न लगाएं।",
            "bn": "দয়া করে শুধুমাত্র संख्या লিখুন, টাকার চিহ্ন দেবেন না।",
            "ta": "எண்களை மட்டும் உள்ளிடவும், ₹ குறியீடு வேண்டாம்.",
        },
        "examples": {
            "en": "e.g. 180000",
            "hi": "उदा. 180000",
        },
        "validation_guidance": {
            "en": "Must be an integer between 0 and 10,00,00,000 matching your income certificate.",
            "hi": "0 से 10 करोड़ के मध्य पूर्णांक; आय प्रमाणपत्र के अनुसार होना चाहिए।",
        },
        "validation_rules": {"min": 0, "max": 100000000, "type": "integer"},
    },
    {
        "field_key": "has_income_certificate",
        "field_type": "boolean",
        "required": True,
        "sort_order": 4,
        "labels": {
            "en": "Do you possess an Income Certificate?",
            "hi": "क्या आपके पास आय प्रमाणपत्र है?",
            "bn": "আপনার কি আয় প্রমাণপত্র আছে?",
            "ta": "உங்களிடம் வருமானச் சான்றிதழ் உள்ளதா?",
            "te": "మీ వద్ద ఆదాయ ధృవీకరణ పత్రం ఉందా?",
            "mr": "तुमच्याकडे उत्पन्नाचा दाखला आहे का?",
            "gu": "શું તમારી પાસે આવકનું પ્રમાણપત્ર છે?",
            "kn": "ನಿಮ್ಮ ಬಳಿ ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ ಇದೆಯೇ?",
            "ml": "നിങ്ങളുടെ കയ്യിൽ വരുമാന സർട്ടിഫിക്കറ്റ് ഉണ്ടോ?",
            "pa": "ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਆਮਦਨ ਪ੍ਰਮਾਣ-ਪੱਤਰ ਹੈ?",
            "or": "ଆପଣଙ୍କ ପାଖରେ ଆୟ ପ୍ରମାଣପତ୍ର ଅଛି କି?",
            "ur": "کیا آپ کے پاس آمدنی کا سرٹیفکیٹ ہے؟",
            "as": "আপোনাৰ আয়ৰ প্ৰমাণপত্ৰ আছে নে?",
            "ne": "तपाईंसँग आय प्रमाणपत्र छ?",
            "kok": "तुमच्या कडेन उत्पन्नाचो दाखलो आसा?",
            "sd": "ڇا توهان وٽ آمدني جو سرٽيفڪيٽ آهي؟",
            "ks": "کیا تُہنز ہَتھ آمدنی سَنَد ہے؟",
            "mai": "की अहाँ लग आय प्रमाणपत्र अछि?",
            "doi": "की तुंदे कोल आमदनी दा प्रमाणपत्र ऐ?",
            "brx": "नोंथांनो आय प्रमाणपत्र दं ना?",
            "mni": "নহাক্কী ইনকম সার্টিফিকেট লৈবা?",
            "sa": "किं भवतः समीपे आय-प्रमाणपत्रम् अस्ति?",
            "sat": "ᱟᱢᱟᱜ ᱥᱮᱨᱢᱟ ᱯᱨᱚᱢᱟᱱ ᱯᱟᱴᱟ ᱢᱮᱱᱟᱜ-ᱟ?",
        },
        "explanations": {
            "en": "Income certificate issued by a Tehsildar, Revenue Officer, or competent authority.",
            "hi": "तहसीलदार या अधिकृत अधिकारी द्वारा जारी आय प्रमाणपत्र।",
            "bn": "তহসিলদার বা অনুমোদিত কর্মকর্তা দ্বারা প্রদত্ত আয় প্রমাণপত্র।",
            "ta": "தாசில்தார் அல்லது அங்கீகரிக்கப்பட்ட அதிகாரியால் வழங்கப்பட்ட வருமானச் சான்றிதழ்.",
            "te": "తహసీల్దార్ లేదా అధీకృత అధికారి ద్వారా జారీ చేయబడిన ఆదాయ ధృవీకరణ పత్రం.",
            "mr": "तहसीलदार किंवा अधिकृत अधिकाऱ्याने दिलेला उत्पन्नाचा दाखला.",
        },
        "instructions": {
            "en": "Select Yes or No. If No, guidance will be provided to help you obtain one.",
            "hi": "हाँ या नहीं चुनें। यदि नहीं है, तो आवेदन में मदद के लिए निर्देश दिए जाएंगे।",
            "bn": "হ্যাঁ বা না নির্বাচন করুন। না থাকলে, সংগ্রহের নির্দেশনা দেওয়া হবে।",
            "ta": "ஆம் அல்லது இல்லை தேர்ந்தெடுக்கவும். இல்லையென்றால் வழிகாட்டுதல் வழங்கப்படும்.",
        },
        "examples": {
            "en": "Yes / No",
            "hi": "हाँ / नहीं",
        },
        "validation_guidance": {
            "en": "A valid boolean confirmation is required.",
            "hi": "हाँ या नहीं में से एक विकल्प चुनना अनिवार्य है।",
        },
        "validation_rules": {"type": "boolean"},
    },
]


# ── Structured Eligibility Requirements ────────────────────────────────

DEMO_ELIGIBILITY_REQUIREMENTS: list[dict] = [
    {
        "criterion_key": "annual_income_ceiling",
        "criterion_type": "annual_income",
        "operator": "lte",
        "threshold_value": {"max_income_inr": 250000, "currency": "INR"},
        "is_mandatory": True,
        "sort_order": 1,
        "titles_by_language": {
            "en": "Annual Family Income Ceiling (Max ₹2,50,000)",
            "hi": "पारिवारिक वार्षिक आय सीमा (अधिकतम ₹2.5 लाख)",
            "bn": "পারিবারিক বার্ষিক আয় সীমা (সর্বোচ্চ ₹২.৫ লাখ)",
            "ta": "குடும்ப ஆண்டு வருமான உச்சவரம்பு (அதிகபட்சம் ₹2.5 லட்சம்)",
            "te": "కుటుంబ వార్షిక ఆదాయ పరిమితి (గరిష్టంగా ₹2.5 లక్షలు)",
            "mr": "कौटुंबिक वार्षिक उत्पन्न मर्यादा (कमाल ₹२.५ लाख)",
        },
        "descriptions_by_language": {
            "en": "Gross total family income from all sources combined must not exceed Rs. 2,50,000 per annum.",
            "hi": "सभी स्रोतों से परिवार की कुल वार्षिक आय ₹2,50,000 से अधिक नहीं होनी चाहिए।",
            "bn": "সমস্ত উৎস মিলিয়ে মোট পারিবারিক বার্ষিক আয় ₹২,৫০,০০০-এর বেশি হওয়া চলবে না।",
            "ta": "அனைத்து வழிகளிலிருந்தும் பெறப்படும் மொத்த குடும்ப வருமானம் ஆண்டுக்கு ₹2,50,000-க்கு மேல் இருக்கக்கூடாது.",
            "te": "అన్ని మార్గాల ద్వారా లభించే కుటుంబ మొత్తం వార్షిక ఆదాయం ₹2,50,000 మించరాదు.",
            "mr": "सर्व मार्गांनी मिळणारे कुटुंबाचे एकूण वार्षिक उत्पन्न ₹२,५०,००० पेक्षा जास्त नसावे.",
        },
        "official_source_reference": "MHRD Demo Scheme Guidelines Section 4.1",
        "verification_status": "pending_review",
    },
    {
        "criterion_key": "minimum_qualifying_marks",
        "criterion_type": "academic_qualification",
        "operator": "gte",
        "threshold_value": {"min_percentage": 50.0},
        "is_mandatory": True,
        "sort_order": 2,
        "titles_by_language": {
            "en": "Minimum Qualifying Academic Score (50%)",
            "hi": "न्यूनतम अर्हक शैक्षणिक अंक (50%)",
            "bn": "ন্যূনতম শিক্ষাগত নম্বর (৫০%)",
            "ta": "குறைந்தபட்ச கல்வித் தகுதி மதிப்பெண் (50%)",
            "te": "కనీస అర్హత మార్కులు (50%)",
            "mr": "किमान शैक्षणिक गुण (५०%)",
        },
        "descriptions_by_language": {
            "en": "Candidate must have secured at least 50% marks in the last qualifying examination.",
            "hi": "अभ्यर्थी ने पिछली अर्हक परीक्षा में न्यूनतम 50% अंक प्राप्त किए होने चाहिए।",
            "bn": "আবেদনকারীকে শেষ পরীক্ষায় কমপক্ষে ৫০% নম্বর পেতে হবে।",
            "ta": "விண்ணப்பதாரர் கடைசி தகுதித் தேர்வில் குறைந்தது 50% மதிப்பெண்கள் பெற்றிருக்க வேண்டும்.",
            "te": "అభ్యర్థి చివరి అర్హత పరీక్షలో కనీసం 50% మార్కులు సాధించి ఉండాలి.",
            "mr": "उमेदवाराने मागील परीक्षेत किमान ५०% गुण मिळवलेले असावेत.",
        },
        "official_source_reference": "MHRD Demo Scheme Guidelines Section 4.2",
        "verification_status": "pending_review",
    },
    {
        "criterion_key": "regular_full_time_enrollment",
        "criterion_type": "institutional_enrollment",
        "operator": "eq",
        "threshold_value": {"enrollment_mode": "regular_full_time"},
        "is_mandatory": True,
        "sort_order": 3,
        "titles_by_language": {
            "en": "Regular Full-Time Institution Enrollment",
            "hi": "नियमित (पूर्णकालिक) उच्च शिक्षण संस्थान में नामांकन",
            "bn": "নিয়মিত পূর্ণকালীন উচ্চশিক্ষায় ভর্তি",
            "ta": "வழக்கமான முழுநேர உயர் கல்வி சேர்க்கை",
            "te": "రెగ్యులర్ పూర్తి సమయ విద్యా ప్రవేశం",
            "mr": "नियमित पूर्णवेळ उच्च शिक्षण प्रवेश",
        },
        "descriptions_by_language": {
            "en": "Applicant must be enrolled as a regular full-time student in an approved college or university.",
            "hi": "मान्यता प्राप्त कॉलेज अथवा विश्वविद्यालय में नियमित छात्र के रूप में अध्ययनरत होना अनिवार्य।",
            "bn": "স্বীকৃত কলেজ বা বিশ্ববিদ্যালয়ে নিয়মিত পূর্ণকালীন শিক্ষার্থী হিসেবে অধ্যয়নরত থাকা বাধ্যতামূলক।",
            "ta": "அங்கீகரிக்கப்பட்ட கல்லூரியில் வழக்கமான முழுநேர மாணவராகப் பயில வேண்டும்.",
            "te": "గుర్తింపు పొందిన విద్యాసంస్థలో రెగ్యులర్ విద్యార్థిగా చదువుతూ ఉండాలి.",
            "mr": "मान्यताप्राप्त संस्थेत नियमित पूर्णवेळ विद्यार्थी म्हणून शिकत असणे आवश्यक.",
        },
        "official_source_reference": "MHRD Demo Scheme Guidelines Section 4.3",
        "verification_status": "pending_review",
    },
]


# ── Structured Document Requirements ───────────────────────────────────

DEMO_DOCUMENT_REQUIREMENTS: list[dict] = [
    {
        "document_code": "income_certificate",
        "requirement_type": "always_required",
        "condition_rule": None,
        "is_mandatory": True,
        "sort_order": 1,
        "titles_by_language": {
            "en": "Competent Authority Income Certificate",
            "hi": "सक्षम प्राधिकारी द्वारा जारी आय प्रमाणपत्र",
            "bn": "সক্ষম কর্তৃপক্ষ দ্বারা প্রদত্ত আয় প্রমাণপত্র",
            "ta": "அதிகாரப்பூர்வ வருமானச் சான்றிதழ்",
            "te": "ఆదాయ ధృవీకరణ పత్రం",
            "mr": "सक्षम प्राधिकाऱ्याने दिलेला उत्पन्नाचा दाखला",
        },
        "descriptions_by_language": {
            "en": "Valid certificate showing gross annual family income, issued by Tehsildar, SDM, or Revenue Officer.",
            "hi": "तहसीलदार, एसडीएम या अधिकृत राजस्व अधिकारी द्वारा जारी वैध आय प्रमाणपत्र।",
            "bn": "তহসিলদার বা রাজস্ব কর্মকর্তা দ্বারা প্রদত্ত পারিবারিক আয়ের প্রমাণপত্র।",
            "ta": "தாசில்தார் அல்லது வருவாய் அதிகாரியால் வழங்கப்பட்ட வருமானச் சான்றிதழ்.",
            "te": "తహసీల్దార్ లేదా రెవెన్యూ అధికారి జారీ చేసిన ఆదాయ ధృవీకరణ పత్రం.",
            "mr": "तहसीलदार किंवा महसूल अधिकाऱ्याने दिलेला अधिकृत उत्पन्नाचा दाखला.",
        },
        "issuing_authority": "Tehsildar / Sub-Divisional Magistrate / Revenue Officer",
        "validity_period_info": "Current Financial Year (issued within last 12 months)",
        "official_source_url": "https://scholarships.gov.in/guidelines/income_cert",
        "source_reference": "MHRD Annexure II (Document Standards)",
        "verification_status": "pending_review",
    },
    {
        "document_code": "institution_enrollment_letter",
        "requirement_type": "always_required",
        "condition_rule": None,
        "is_mandatory": True,
        "sort_order": 2,
        "titles_by_language": {
            "en": "Institution Bonafide / Enrollment Letter",
            "hi": "संस्थान बोनाफाइड / नामांकन प्रमाणपत्र",
            "bn": "শিক্ষা প্রতিষ্ঠানের ভর্তির প্রমাণপত্র",
            "ta": "கல்வி நிறுவனச் சேர்க்கைச் சான்றிதழ்",
            "te": "విద్యాసంస్థ బోనఫైడ్ సర్టిఫికెట్",
            "mr": "संस्थेचे बोनाफाईड / प्रवेश प्रमाणपत्र",
        },
        "descriptions_by_language": {
            "en": "Current academic year bonafide certificate duly signed and stamped by the Head of Institution / Principal.",
            "hi": "वर्तमान सत्र का बोनाफाइड प्रमाणपत्र, जिस पर संस्था प्रमुख अथवा प्राचार्य के हस्ताक्षर व मुहर हों।",
            "bn": "বর্তমান শিক্ষাবর্ষের প্রতিষ্ঠান প্রধান বা অধ্যক্ষ স্বাক্ষরিত শংসাপত্র।",
            "ta": "கல்லூரி முதல்வர் அல்லது துறைத் தலைவரால் சான்றளிக்கப்பட்ட நடப்பு ஆண்டின் சான்றிதழ்.",
            "te": "కళాశాల ప్రిన్సిపాల్ సంతకం మరియు స్టాంప్ చేసిన ప్రస్తుత విద్యాసంవత్సర ధృవీకరణ పత్రం.",
            "mr": "संस्थाप्रमुख किंवा प्राचार्यांची स्वाक्षरी असलेले चालू शैक्षणिक वर्षाचे प्रमाणपत्र.",
        },
        "issuing_authority": "Head of Educational Institution / Principal / Registrar",
        "validity_period_info": "Current Academic Session",
        "official_source_url": "https://scholarships.gov.in/guidelines/bonafide_letter",
        "source_reference": "MHRD Annexure III (Institution Verification)",
        "verification_status": "pending_review",
    },
    {
        "document_code": "caste_category_certificate",
        "requirement_type": "conditional",
        "condition_rule": {
            "trigger_field": "social_category",
            "operator": "in",
            "values": ["SC", "ST", "OBC", "EWS"],
            "explanation": "Required only when applying under reserved categories. Not required for General category.",
        },
        "is_mandatory": False,
        "sort_order": 3,
        "titles_by_language": {
            "en": "Caste / Category Certificate (Conditional)",
            "hi": "जाति / श्रेणी प्रमाणपत्र (शर्त अनुसार)",
            "bn": "জাতি / শ্রেণী শংসাপত্র (শর্তসাপেক্ষ)",
            "ta": "சாதி / சமூகப் பிரிவுச் சான்றிதழ் (நிபந்தனைக்குட்பட்டது)",
            "te": "కుల ధృవీకరణ పత్రం (వర్తించే చోట)",
            "mr": "जात / प्रवर्ग प्रमाणपत्र (अटीनुसार)",
        },
        "descriptions_by_language": {
            "en": "Mandatory only for applicants claiming reservation (SC/ST/OBC/EWS). Not required for General candidates.",
            "hi": "केवल आरक्षित श्रेणी (एससी/एसटी/ओबीसी/ईडब्ल्यूएस) में छूट का दावा करने वाले आवेदकों के लिए अनिवार्य।",
            "bn": "সংরক্ষণ দাবি করা প্রার্থীদের জন্য বাধ্যতামূলক। সাধারণ প্রার্থীদের জন্য প্রযোজ্য নয়।",
            "ta": "இடஒதுக்கீடு கோரும் விண்ணப்பதாரர்களுக்கு மட்டுமே இது கட்டாயமாகும்.",
            "te": "రిజర్వేషన్ కోరే అభ్యర్థులకు మాత్రమే ఇది అవసరం. జనరల్ అభ్యర్థులకు అవసరం లేదు.",
            "mr": "केवळ आरक्षित प्रवर्गातील उमेदवारांसाठी आवश्यक. खुल्या प्रवर्गासाठी आवश्यक नाही.",
        },
        "issuing_authority": "Competent District Revenue Authority / Tehsildar",
        "validity_period_info": "Permanent (or non-creamy layer as per state rules)",
        "official_source_url": "https://scholarships.gov.in/guidelines/caste_cert",
        "source_reference": "MHRD Annexure IV (Reservation Guidelines)",
        "verification_status": "pending_review",
    },
    {
        "document_code": "bank_account_passbook",
        "requirement_type": "always_required",
        "condition_rule": None,
        "is_mandatory": True,
        "sort_order": 4,
        "titles_by_language": {
            "en": "Bank Account Passbook / Statement Copy",
            "hi": "बैंक खाता पासबुक / स्टेटमेंट प्रति",
            "bn": "ব্যাংক পাসবুক বা স্টেটমেন্ট কপি",
            "ta": "வங்கி கணக்கு புத்தக நகல்",
            "te": "బ్యాంకు ఖాతా పాస్‌బుక్ కాపీ",
            "mr": "बँक खाते पासबुक प्रत",
        },
        "descriptions_by_language": {
            "en": "Copy of the first page of active bank passbook showing student name, account number, and IFSC.",
            "hi": "सक्रिय बचत खाते की पासबुक का पहला पृष्ठ, जिसमें विद्यार्थी का नाम, खाता संख्या और IFSC स्पष्ट हो।",
            "bn": "ব্যাংক পাসবইয়ের প্রথম পৃষ্ঠার কপি যেখানে নাম, অ্যাকাউন্ট নম্বর এবং IFSC স্পষ্ট দেখা যায়।",
            "ta": "மாணவர் பெயர், கணக்கு எண் மற்றும் IFSC குறியீடு தெளிவாகத் தெரியும் வங்கிப் புத்தகத்தின் முதல் பக்கம்.",
            "te": "విద్యార్థి పేరు, ఖాతా సంఖ్య మరియు IFSC స్పష్టంగా ఉండే బ్యాంక్ పాస్‌బుక్ మొదటి పేజీ కాపీ.",
            "mr": "विद्यार्थ्याचे नाव, खाते क्रमांक आणि IFSC स्पष्ट दिसणारे बँक पासबुकचे पहिले पान.",
        },
        "issuing_authority": "Scheduled Commercial Bank / India Post Payments Bank",
        "validity_period_info": "Active individual account in applicant's name",
        "official_source_url": "https://scholarships.gov.in/guidelines/dbt_bank",
        "source_reference": "MHRD Annexure V (Direct Benefit Transfer)",
        "verification_status": "pending_review",
    },
]


# ── Step-by-Step Application Instructions ──────────────────────────────

DEMO_APPLICATION_STEPS: list[dict] = [
    {
        "step_number": 1,
        "step_key": "check_eligibility",
        "titles_by_language": {
            "en": "1. Verify Eligibility & Rules",
            "hi": "1. अपनी पात्रता और नियम समझें",
            "bn": "১. যোগ্যতা ও নিয়মাবলী যাচাই করুন",
            "ta": "1. தகுதி மற்றும் விதிகளை சரிபார்க்கவும்",
            "te": "1. అర్హత మరియు నిబంధనలను తనిఖీ చేయండి",
            "mr": "१. पात्रता व नियमांची खात्री करा",
        },
        "instructions_by_language": {
            "en": "Review annual income threshold, institution affiliation, and minimum qualifying marks before starting.",
            "hi": "आवेदन पूर्व वार्षिक आय सीमा, संस्थान की मान्यता तथा न्यूनतम शैक्षणिक अंकों की शर्तें अच्छी तरह समझें।",
            "bn": "আবেদন শুরু করার আগে বার্ষিক আয়ের সীমা, প্রতিষ্ঠানের অনুমোদন এবং ন্যূনতম নম্বর যাচাই করে নিন।",
            "ta": "தொடங்குவதற்கு முன் ஆண்டு வருமான வரம்பு, கல்வி நிறுவன ஏற்பு மற்றும் குறைந்தபட்ச மதிப்பெண்களை மதிப்பாய்வு செய்யவும்.",
            "te": "ప్రారంభించే ముందు వార్షిక ఆదాయ పరిమితి, విద్యాసంస్థ గుర్తింపు మరియు కనీస అర్హత మార్కులను పరిశీలించండి.",
            "mr": "सुरुवात करण्यापूर्वी वार्षिक उत्पन्न मर्यादा, संस्थेची मान्यता आणि किमान गुणांची खात्री करून घ्या.",
        },
        "official_action_url": "https://scholarships.gov.in/guidelines",
        "source_reference": "Step Guidance 1.0",
        "verification_status": "pending_review",
    },
    {
        "step_number": 2,
        "step_key": "gather_documents",
        "titles_by_language": {
            "en": "2. Assemble Required Supporting Documents",
            "hi": "2. आवश्यक दस्तावेज एकत्र करें",
            "bn": "২. প্রয়োজনীয় কাগজপত্র সংগ্রহ করুন",
            "ta": "2. தேவையான ஆவணங்களைச் சேகரிக்கவும்",
            "te": "2. అవసరమైన పత్రాలను సిద్ధం చేసుకోండి",
            "mr": "२. आवश्यक कागदपत्रे गोळा करा",
        },
        "instructions_by_language": {
            "en": "Keep income certificate, institutional bonafide letter, category certificate (if applicable), and bank passbook handy.",
            "hi": "अपना वैध आय प्रमाणपत्र, कॉलेज बोनाफाइड पत्र, श्रेणी प्रमाणपत्र (यदि लागू हो) और बैंक पासबुक तैयार रखें।",
            "bn": "আপনার আয় প্রমাণপত্র, কলেজের প্রশংসাপত্র, জাতি শংসাপত্র (প্রযোজ্য ক্ষেত্রে) এবং ব্যাংক পাসবুক প্রস্তুত রাখুন।",
            "ta": "வருமானச் சான்றிதழ், கல்லூரி சேர்க்கைச் சான்று, சாதிச் சான்றிதழ் மற்றும் வங்கி கணக்குப் புத்தகத்தைத் தயார் நிலையில் வைக்கவும்.",
            "te": "ఆదాయ ధృవీకరణ పత్రం, కాలేజీ బోనఫైడ్ లేఖ, కుల ధృవీకరణ పత్రం మరియు బ్యాంక్ పాస్‌బుక్ సిద్ధంగా ఉంచుకోండి.",
            "mr": "उत्पन्नाचा दाखला, कॉलेजचे बोनाफाईड, प्रवर्ग प्रमाणपत्र (लागू असल्यास) आणि बँक पासबुक तयार ठेवा.",
        },
        "official_action_url": "https://scholarships.gov.in/checklist",
        "source_reference": "Step Guidance 2.0",
        "verification_status": "pending_review",
    },
    {
        "step_number": 3,
        "step_key": "online_registration",
        "titles_by_language": {
            "en": "3. One-Time Registration (OTR) on Official Portal",
            "hi": "3. आधिकारिक पोर्टल पर वन-टाइम रजिस्ट्रेशन (OTR)",
            "bn": "৩. অফিসিয়াল পোর্টালে ওয়ান-টাইম রেজিস্ট্রেশন (OTR)",
            "ta": "3. அதிகாரப்பூர்வ தளத்தில் ஒருமுறை பதிவு (OTR)",
            "te": "3. అధికారిక పోర్టల్‌లో వన్-టైమ్ రిజిస్ట్రేషన్ (OTR)",
            "mr": "३. अधिकृत पोर्टलवर वन-टाईम रजिस्ट्रेशन (OTR)",
        },
        "instructions_by_language": {
            "en": "Visit scholarships.gov.in and complete One-Time Registration using your mobile number and Aadhaar/ID.",
            "hi": "scholarships.gov.in पर जाकर अपने सक्रिय मोबाइल नंबर एवं पहचान पत्र द्वारा वन-टाइम रजिस्ट्रेशन पूर्ण करें।",
            "bn": "scholarships.gov.in-এ যান এবং আপনার মোবাইল নম্বর দিয়ে ওয়ান-টাইম রেজিস্ট্রেশন সম্পন্ন করুন।",
            "ta": "scholarships.gov.in இணையதளத்திற்குச் சென்று உங்கள் கைபேசி எண் மூலம் ஒருமுறை பதிவு செய்யவும்.",
            "te": "scholarships.gov.in సైట్‌కి వెళ్లి మీ మొబైల్ నంబర్‌తో వన్-టైమ్ రిజిస్ట్రేషన్ పూర్తి చేయండి.",
            "mr": "scholarships.gov.in वर जाऊन आपल्या मोबाईल क्रमांकाद्वारे वन-टाईम रजिस्ट्रेशन पूर्ण करा.",
        },
        "official_action_url": "https://scholarships.gov.in/otr",
        "source_reference": "Step Guidance 3.0",
        "verification_status": "pending_review",
    },
    {
        "step_number": 4,
        "step_key": "guided_practice_and_preparation",
        "titles_by_language": {
            "en": "4. Understand & Practice with NagrikSaarathi Guidance",
            "hi": "4. नागरिक सारथी से अपनी भाषा में फॉर्म का पूर्वाभ्यास",
            "bn": "৪. নাগরিক সারথির সহায়তায় আপনার ভাষায় প্রস্তুতি",
            "ta": "4. உங்கள் தாய்மொழியில் படிவத்தைப் புரிந்துகொண்டு பயிற்சி செய்யுங்கள்",
            "te": "4. మీ భాషలో ఫారమ్‌ను అర్థం చేసుకుని సాధన చేయండి",
            "mr": "४. नागरिक सारथीच्या मदतीने मातृभाषेत सराव करा",
        },
        "instructions_by_language": {
            "en": "Use NagrikSaarathi to understand every technical question and rule in your mother tongue. No private data is saved on the server.",
            "hi": "नागरिक सारथी की सहायता से अपनी मातृभाषा में सभी जटिल शर्तों को समझें। आपका कोई भी व्यक्तिगत डेटा सर्वर पर नहीं भेजा जाता।",
            "bn": "নাগরিক সারথি ব্যবহার করে আপনার মাতৃভাষায় জটিল নিয়মগুলো বুঝে নিন। কোনো ব্যক্তিগত ডেটা সার্ভারে সংরক্ষণ করা হয় না।",
            "ta": "உங்கள் தாய்மொழியில் அனைத்து விதிமுறைகளையும் எளிதாகப் புரிந்து கொள்ளுங்கள். எந்தவொரு தனிப்பட்ட விவரமும் சேமிக்கப்படாது.",
            "te": "నాగరిక్ సారథి ద్వారా మీ మాతృభాషలో కఠినమైన నిబంధనలను సులభంగా అర్థం చేసుకోండి.",
            "mr": "नागरिक सारथीच्या मदतीने सर्व तांत्रिक अटी मातृभाषेत समजून घ्या. कोणताही वैयक्तिक डेटा सर्व्हरवर सेव्ह केला जात नाही.",
        },
        "official_action_url": None,
        "source_reference": "Step Guidance 4.0",
        "verification_status": "pending_review",
    },
    {
        "step_number": 5,
        "step_key": "submit_and_record_acknowledgment",
        "titles_by_language": {
            "en": "5. Final Submission & Acknowledgment Tracking",
            "hi": "5. आधिकारिक पोर्टल पर अंतिम प्रविष्टि एवं पावती रसीद",
            "bn": "৫. চূড়ান্ত জমা এবং প্রাপ্তিস্বীকার পত্র সংরক্ষণ",
            "ta": "5. அதிகாரப்பூர்வ தளத்தில் சமர்ப்பித்தல் மற்றும் கண்காணிப்பு",
            "te": "5. తుది సమర్పణ మరియు రసీదు ట్రాకింగ్",
            "mr": "५. अधिकृत पोर्टलवर अंतिम अर्ज सादर करणे व पावती जतन करणे",
        },
        "instructions_by_language": {
            "en": "Submit the finalized form on the official government portal, download the acknowledgment slip, and note down your Application ID for institutional verification.",
            "hi": "आधिकारिक सरकारी पोर्टल पर फॉर्म सबमिट करें, पावती पर्ची डाउनलोड करें और संस्थान सत्यापन हेतु अपनी आवेदन आईडी सुरक्षित रखें।",
            "bn": "অফিসিয়াল সরকারি পোর্টালে ফর্ম জমা দিন, প্রাপ্তিস্বীকার রশিদ ডাউনলোড করুন এবং আবেদন আইডি সংরক্ষণ করুন।",
            "ta": "அதிகாரப்பூர்வ அரசு தளத்தில் படிவத்தைச் சமர்ப்பித்து, ஒப்புகைச் சீட்டைப் பதிவிறக்கி விண்ணப்ப எண்ணைப் பாதுகாப்பாக வைக்கவும்.",
            "te": "అధికారిక ప్రభుత్వ పోర్టల్‌లో ఫారమ్‌ను సమర్పించి, రసీదును డౌన్‌లోడ్ చేసుకుని అప్లికేషన్ ఐడీని భద్రపరుచుకోండి.",
            "mr": "अधिकृत पोर्टलवर अर्ज सादर करा, पावती डाउनलोड करा आणि संस्था पडताळणीसाठी अर्ज क्रमांक सुरक्षित ठेवा.",
        },
        "official_action_url": "https://scholarships.gov.in/login",
        "source_reference": "Step Guidance 5.0",
        "verification_status": "pending_review",
    },
]


# Languages with reviewed-quality demo labels
REVIEWED_LANGUAGES = {"hi", "bn", "ta", "te", "mr"}

_RNG = random.Random(42)  # deterministic for reproducibility


def _demo_sessions_and_events(
    scheme_id: int,
    language_codes: list[str],
    n_sessions: int,
    n_events_per_session: int,
) -> tuple[list[AssistedSession], list[SessionEvent]]:
    """Build synthetic session + event objects (all ``is_demo=True``)."""
    sessions: list[AssistedSession] = []
    events: list[SessionEvent] = []
    base_time = datetime(2026, 9, 1, 8, 0, 0, tzinfo=timezone.utc)

    statuses = ["completed", "abandoned", "needs_human_help", "in_progress"]
    field_keys = [f["field_key"] for f in DEMO_FIELDS]
    usable_event_types = [
        "help_requested", "voice_used", "validation_failed",
        "field_completed", "issue_resolved", "issue_unresolved",
    ]
    barrier_cats = list(BARRIER_CATEGORIES)
    resolution_opts = ["resolved", "unresolved", "escalated", None]

    for i in range(n_sessions):
        lang = _RNG.choice(language_codes)
        status = _RNG.choice(statuses)
        started = base_time + timedelta(hours=i * 3, minutes=_RNG.randint(0, 59))
        ended = started + timedelta(minutes=_RNG.randint(5, 90)) if status != "in_progress" else None

        sess = AssistedSession(
            id=str(uuid.UUID(int=_RNG.getrandbits(128), version=4)),
            scheme_id=scheme_id,
            selected_language=lang,
            channel=_RNG.choice(["web", "assisted_desk"]),
            status=status,
            analytics_consent=True,  # demo sessions simulate consented analytics
            is_demo=True,
            started_at=started,
            ended_at=ended,
        )
        sessions.append(sess)

        for j in range(n_events_per_session):
            et = _RNG.choice(usable_event_types)
            ev = SessionEvent(
                session_id=sess.id,
                field_key=_RNG.choice(field_keys) if et != "help_requested" else None,
                event_type=et,
                barrier_category=_RNG.choice(barrier_cats) if et == "validation_failed" else None,
                resolution_status=_RNG.choice(resolution_opts) if et in ("issue_resolved", "issue_unresolved") else None,
                language_code=lang,
                created_at=started + timedelta(minutes=j + 1),
            )
            events.append(ev)

    return sessions, events


# ── Main seed function ──────────────────────────────────────────────────

def seed(*, reset: bool = False) -> None:
    """Populate the database idempotently. Pass ``reset=True`` to
    drop and recreate all tables first."""
    settings = get_settings()
    engine = get_engine(settings)
    SessionFactory = get_session_factory(settings)

    if reset:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)

    with SessionFactory() as session:
        # 1. Languages (exact 22 Eighth Schedule languages) ─────────────
        existing_codes = {
            row[0]
            for row in session.execute(select(Language.language_code)).all()
        }
        for lang_data in LANGUAGES:
            if lang_data["language_code"] not in existing_codes:
                session.add(Language(enabled=True, **lang_data))
        session.flush()

        # 2. Government Scheme ─────────────────────────────────────────
        demo_slug = "demo-scholarship-application"
        scheme = session.execute(
            select(GovernmentScheme).where(GovernmentScheme.slug == demo_slug)
        ).scalar_one_or_none()

        scheme_descriptions = {
            "en": "Central financial assistance scheme for students pursuing recognized higher education. Provides scholarship guidance in 22 Eighth Schedule languages. (Synthetic Demo Scheme)",
            "hi": "उच्च शिक्षा प्राप्त कर रहे विद्यार्थियों के लिए केंद्रीय वित्तीय सहायता योजना। 22 आधिकारिक भाषाओं में मार्गदर्शित सहायता। (डेमो नागरिक सहायता तंत्र)",
            "bn": "স্বীকৃত উচ্চশিক্ষার শিক্ষার্থীদের জন্য কেন্দ্রীয় আর্থিক সহায়তা পরিকল্পনা। (সিন্থেটিক ডেমো স্কিম)",
            "ta": "உயர் கல்வி பயிலும் மாணவர்களுக்கான மத்திய அரசு நிதி உதவித் திட்டம். (செயற்கை மாதிரி திட்டம்)",
            "te": "గుర్తింపు పొందిన ఉన్నత విద్యా విద్యార్థుల కోసం కేంద్ర ఆర్థిక సహాయ పథకం. (నమూనా పథకం)",
            "mr": "मान्यताप्राप्त उच्च शिक्षण घेणाऱ्या विद्यार्थ्यांसाठी केंद्रीय आर्थिक सहाय्य योजना. (डेमो योजना)",
        }
        scheme_instructions = {
            "en": "Review eligibility rules, gather verified income and enrollment documents, practice filling the form, and submit on scholarships.gov.in.",
            "hi": "अपनी पात्रता जांचें, आवश्यक आय व नामांकन दस्तावेज तैयार रखें, फॉर्म का पूर्वाभ्यास करें और आधिकारिक पोर्टल पर आवेदन करें।",
            "bn": "যোগ্যতা যাচাই করুন, প্রয়োজনীয় নথি সংগ্রহ করুন এবং সরকারি পোর্টালে জমা দিন।",
            "ta": "தகுதியை சரிபார்த்து, தேவையான ஆவணங்களுடன் அதிகாரப்பூர்வ தளத்தில் சமர்ப்பிக்கவும்.",
            "te": "అర్హతలను తనిఖీ చేసి, అవసరమైన పత్రాలతో అధికారిక పోర్టల్‌లో దరఖాస్తు చేసుకోండి.",
            "mr": "पात्रता तपासून, आवश्यक कागदपत्रांसह अधिकृत पोर्टलवर अर्ज सादर करा.",
        }

        if scheme is None:
            scheme = GovernmentScheme(
                slug=demo_slug,
                display_name="राष्ट्रीय छात्रवृत्ति कार्यक्रम (National Scholarship Programme)",
                description=(
                    "उच्च शिक्षा प्राप्त कर रहे विद्यार्थियों के लिए केंद्रीय वित्तीय सहायता योजना। "
                    "पात्रता: किसी भी मान्यता प्राप्त उच्च शिक्षण संस्थान में अध्ययनरत विद्यार्थी। "
                    "(Demo Civic Assistance Architecture)"
                ),
                department_name="उच्च शिक्षा विभाग, शिक्षा मंत्रालय (Department of Higher Education)",
                official_source_url="https://scholarships.gov.in",
                source_document_reference="MHRD/HE/SCH/2026/SYNTHETIC-DEMO",
                official_application_url="https://scholarships.gov.in/freshApplication",
                last_verified_at=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
                verification_status="pending_review",
                verification_source_reference="National Public Services Sandbox (Fictional Scheme for Guided Self-Application)",
                descriptions_by_language=scheme_descriptions,
                application_instructions_by_language=scheme_instructions,
                is_demo=True,
                is_active=True,
            )
            session.add(scheme)
            session.flush()
        else:
            scheme.display_name = "राष्ट्रीय छात्रवृत्ति कार्यक्रम (National Scholarship Programme)"
            scheme.description = (
                "उच्च शिक्षा प्राप्त कर रहे विद्यार्थियों के लिए केंद्रीय वित्तीय सहायता योजना। "
                "पात्रता: किसी भी मान्यता प्राप्त उच्च शिक्षण संस्थान में अध्ययनरत विद्यार्थी। "
                "(Demo Civic Assistance Architecture)"
            )
            scheme.department_name = "उच्च शिक्षा विभाग, शिक्षा मंत्रालय (Department of Higher Education)"
            scheme.official_source_url = "https://scholarships.gov.in"
            scheme.source_document_reference = "MHRD/HE/SCH/2026/SYNTHETIC-DEMO"
            scheme.official_application_url = "https://scholarships.gov.in/freshApplication"
            scheme.last_verified_at = datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc)
            scheme.verification_status = "pending_review"
            scheme.verification_source_reference = "National Public Services Sandbox (Fictional Scheme for Guided Self-Application)"
            scheme.descriptions_by_language = scheme_descriptions
            scheme.application_instructions_by_language = scheme_instructions
            scheme.is_demo = True
            session.flush()

        # 3. Form fields for primary scheme ─────────────────────────
        existing_field_keys = {
            row[0]
            for row in session.execute(
                select(FormField.field_key).where(FormField.scheme_id == scheme.id)
            ).all()
        }
        for fd in DEMO_FIELDS:
            if fd["field_key"] not in existing_field_keys:
                session.add(FormField(
                    scheme_id=scheme.id,
                    field_key=fd["field_key"],
                    field_type=fd["field_type"],
                    required=fd["required"],
                    sort_order=fd["sort_order"],
                    labels_by_language=fd["labels"],
                    explanations_by_language=fd.get("explanations", {}),
                    instructions_by_language=fd.get("instructions", {}),
                    examples_by_language=fd.get("examples", {}),
                    validation_guidance_by_language=fd.get("validation_guidance", {}),
                    validation_rules=fd.get("validation_rules", {}),
                    verification_status="pending_review",
                    last_verified_at=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
                ))
            else:
                # Update existing field with examples and validation guidance
                existing_f = session.execute(
                    select(FormField).where(
                        FormField.scheme_id == scheme.id,
                        FormField.field_key == fd["field_key"]
                    )
                ).scalar_one()
                existing_f.examples_by_language = fd.get("examples", {})
                existing_f.validation_guidance_by_language = fd.get("validation_guidance", {})
                existing_f.verification_status = "pending_review"
                existing_f.last_verified_at = datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc)
        session.flush()

        # 4. Structured Eligibility Requirements ─────────────────────
        existing_criteria = {
            row[0]
            for row in session.execute(
                select(SchemeEligibilityRequirement.criterion_key).where(
                    SchemeEligibilityRequirement.scheme_id == scheme.id
                )
            ).all()
        }
        for req in DEMO_ELIGIBILITY_REQUIREMENTS:
            if req["criterion_key"] not in existing_criteria:
                session.add(SchemeEligibilityRequirement(
                    scheme_id=scheme.id,
                    criterion_key=req["criterion_key"],
                    criterion_type=req["criterion_type"],
                    operator=req["operator"],
                    threshold_value=req["threshold_value"],
                    is_mandatory=req["is_mandatory"],
                    sort_order=req["sort_order"],
                    titles_by_language=req["titles_by_language"],
                    descriptions_by_language=req["descriptions_by_language"],
                    official_source_reference=req["official_source_reference"],
                    verification_status=req["verification_status"],
                    last_verified_at=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
                ))
        session.flush()

        # 5. Structured Document Requirements ─────────────────────────
        existing_docs = {
            row[0]
            for row in session.execute(
                select(SchemeDocumentRequirement.document_code).where(
                    SchemeDocumentRequirement.scheme_id == scheme.id
                )
            ).all()
        }
        for doc in DEMO_DOCUMENT_REQUIREMENTS:
            if doc["document_code"] not in existing_docs:
                session.add(SchemeDocumentRequirement(
                    scheme_id=scheme.id,
                    document_code=doc["document_code"],
                    requirement_type=doc["requirement_type"],
                    condition_rule=doc["condition_rule"],
                    is_mandatory=doc["is_mandatory"],
                    sort_order=doc["sort_order"],
                    titles_by_language=doc["titles_by_language"],
                    descriptions_by_language=doc["descriptions_by_language"],
                    issuing_authority=doc["issuing_authority"],
                    validity_period_info=doc["validity_period_info"],
                    official_source_url=doc["official_source_url"],
                    source_reference=doc["source_reference"],
                    verification_status=doc["verification_status"],
                    last_verified_at=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
                ))
        session.flush()

        # 6. Step-by-Step Application Instructions ───────────────────
        existing_steps = {
            row[0]
            for row in session.execute(
                select(SchemeApplicationStep.step_number).where(
                    SchemeApplicationStep.scheme_id == scheme.id
                )
            ).all()
        }
        for st in DEMO_APPLICATION_STEPS:
            if st["step_number"] not in existing_steps:
                session.add(SchemeApplicationStep(
                    scheme_id=scheme.id,
                    step_number=st["step_number"],
                    step_key=st["step_key"],
                    titles_by_language=st["titles_by_language"],
                    instructions_by_language=st["instructions_by_language"],
                    official_action_url=st["official_action_url"],
                    source_reference=st["source_reference"],
                    verification_status=st["verification_status"],
                    last_verified_at=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
                ))
        session.flush()

        # 7. Translation reviews ─────────────────────────────────────
        existing_reviews = {
            (r[0], r[1], r[2])
            for r in session.execute(
                select(
                    TranslationReview.resource_type,
                    TranslationReview.resource_key,
                    TranslationReview.language_code,
                )
            ).all()
        }
        for fd in DEMO_FIELDS:
            for lang_code in fd["labels"]:
                key = ("form_field", fd["field_key"], lang_code)
                if key not in existing_reviews:
                    session.add(TranslationReview(
                        resource_type="form_field",
                        resource_key=fd["field_key"],
                        language_code=lang_code,
                        translation_status=(
                            "approved" if lang_code in REVIEWED_LANGUAGES else "draft"
                        ),
                        reviewer_note=(
                            "Reviewed by native speaker"
                            if lang_code in REVIEWED_LANGUAGES
                            else "Machine-generated or unverified — needs review"
                        ),
                    ))

        for req in DEMO_ELIGIBILITY_REQUIREMENTS:
            for lang_code in req["titles_by_language"]:
                key = ("eligibility_criterion", req["criterion_key"], lang_code)
                if key not in existing_reviews:
                    session.add(TranslationReview(
                        resource_type="eligibility_criterion",
                        resource_key=req["criterion_key"],
                        language_code=lang_code,
                        translation_status=(
                            "approved" if lang_code in REVIEWED_LANGUAGES else "draft"
                        ),
                        reviewer_note="Demonstration eligibility guidance verification",
                    ))

        for doc in DEMO_DOCUMENT_REQUIREMENTS:
            for lang_code in doc["titles_by_language"]:
                key = ("document_requirement", doc["document_code"], lang_code)
                if key not in existing_reviews:
                    session.add(TranslationReview(
                        resource_type="document_requirement",
                        resource_key=doc["document_code"],
                        language_code=lang_code,
                        translation_status=(
                            "approved" if lang_code in REVIEWED_LANGUAGES else "draft"
                        ),
                        reviewer_note="Demonstration document guidance verification",
                    ))
        session.flush()

        # 8. Demo sessions + events ──────────────────────────────────
        existing_demo = session.execute(
            select(AssistedSession.id).where(AssistedSession.is_demo == True)  # noqa: E712
        ).all()
        if not existing_demo:
            all_codes = [ld["language_code"] for ld in LANGUAGES]
            sessions, events = _demo_sessions_and_events(
                scheme_id=scheme.id,
                language_codes=all_codes,
                n_sessions=settings.seed_demo_sessions,
                n_events_per_session=settings.seed_demo_events_per_session,
            )
            session.add_all(sessions)
            session.flush()
            session.add_all(events)

        # 9. Demo Users ──────────────────────────────────────────────
        existing_users = {
            u[0] for u in session.execute(select(User.identifier)).all()
        }
        if "9876543210" not in existing_users:
            session.add(User(
                identifier="9876543210",
                email="citizen@nagrik.gov.in",
                mobile="9876543210",
                hashed_password=hash_password(DEMO_CITIZEN_PASSWORD),
                role="citizen",
                full_name="नागरिक उपयोगकर्ता (Demo Citizen)",
                is_active=True,
                is_demo=True,
            ))
        if "officer@dept.gov.in" not in existing_users:
            session.add(User(
                identifier="officer@dept.gov.in",
                email="officer@dept.gov.in",
                mobile=None,
                hashed_password=hash_password(DEMO_OFFICIAL_PASSWORD),
                role="official",
                full_name="विभागीय नोडल अधिकारी (Department Officer)",
                department="उच्च शिक्षा विभाग, शिक्षा मंत्रालय",
                is_active=True,
                is_demo=True,
            ))

        session.commit()
        print("[OK] Seed completed successfully.")


# ── CLI entry-point ────────────────────────────────────────────────────

if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    seed(reset=reset_flag)

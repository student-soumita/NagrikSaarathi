"""
Deterministic Field Validation Service for NagrikSaarathi.

Evaluates safe, deterministic field rules (presence, formats, numerical ranges, string lengths).
Never invents government eligibility rules or legal conditions.
Directs citizens to the official source document for any legal eligibility queries.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import FormField, GovernmentScheme
from backend.app.schemas.assist import ValidateResponse


def _msg(error_code: str, lang: str, **kwargs) -> str:
    lang = (lang or "en").lower()
    messages = {
        "REQUIRED_FIELD_EMPTY": {
            "en": "This field is required. Please enter a value.",
            "hi": "यह फ़ील्ड अनिवार्य है। कृपया मान दर्ज करें।",
        },
        "INVALID_INTEGER": {
            "en": "Please enter a valid whole number (integer).",
            "hi": "कृपया केवल पूर्णांक (पूर्ण संख्या) दर्ज करें।",
        },
        "INVALID_NUMBER": {
            "en": "Please enter a valid number.",
            "hi": "कृपया केवल वैध संख्या दर्ज करें।",
        },
        "INVALID_BOOLEAN": {
            "en": "Please select Yes or No.",
            "hi": "कृपया हाँ या नहीं चुनें।",
        },
        "PATTERN_MISMATCH": {
            "en": "Input format is invalid. Please match the requested format.",
            "hi": "प्रारूप अमान्य है। कृपया दिए गए प्रारूप के अनुसार भरें।",
        },
    }

    if error_code == "NUMERIC_MIN_VIOLATION":
        m = kwargs.get("min", "")
        return f"Value must be at least {m}." if lang == "en" else f"मान कम से कम {m} होना चाहिए।"
    if error_code == "NUMERIC_MAX_VIOLATION":
        m = kwargs.get("max", "")
        return f"Value must not exceed {m}." if lang == "en" else f"मान अधिकतम {m} हो सकता है।"
    if error_code == "MIN_LENGTH_VIOLATION":
        m = kwargs.get("min_length", "")
        return f"Must be at least {m} characters." if lang == "en" else f"कम से कम {m} अक्षर होने चाहिए।"
    if error_code == "MAX_LENGTH_VIOLATION":
        m = kwargs.get("max_length", "")
        return f"Must not exceed {m} characters." if lang == "en" else f"अधिकतम {m} अक्षर हो सकते हैं।"

    entry = messages.get(error_code, {})
    return entry.get(lang) or entry.get("en") or "Validation error."


class ValidationService:
    @staticmethod
    def validate_field_value(
        db: Session,
        scheme_id: int,
        field_key: str,
        value: Any,
        target_language: str = "hi",
    ) -> Optional[ValidateResponse]:
        """
        Evaluate deterministic form validation rules without inventing legal criteria.
        """
        # Fetch field and scheme
        field = db.execute(
            select(FormField).where(
                FormField.scheme_id == scheme_id,
                FormField.field_key == field_key,
            )
        ).scalar_one_or_none()

        if not field:
            return None

        scheme = db.execute(
            select(GovernmentScheme).where(GovernmentScheme.id == scheme_id)
        ).scalar_one_or_none()
        official_url = scheme.official_source_url if scheme else None

        rules: Dict[str, Any] = field.validation_rules or {}

        # 1. Check Required Rule
        is_empty = value is None or (isinstance(value, str) and value.strip() == "")
        if field.required and is_empty:
            return ValidateResponse(
                is_valid=False,
                field_key=field_key,
                target_language=target_language,
                error_code="REQUIRED_FIELD_EMPTY",
                error_message=_msg("REQUIRED_FIELD_EMPTY", target_language),
                applied_rule={"required": True},
                official_source_url=official_url,
            )

        # If value is empty and not required, it is valid
        if is_empty:
            return ValidateResponse(
                is_valid=True,
                field_key=field_key,
                target_language=target_language,
                error_code=None,
                error_message=None,
                applied_rule=rules,
                official_source_url=official_url,
            )

        # 2. Type Checking
        field_type = field.field_type.lower()
        if field_type == "number" or rules.get("type") in ("integer", "number"):
            try:
                num_val = float(value)
                if rules.get("type") == "integer" and not float(value).is_integer():
                    return ValidateResponse(
                        is_valid=False,
                        field_key=field_key,
                        target_language=target_language,
                        error_code="INVALID_INTEGER",
                        error_message=_msg("INVALID_INTEGER", target_language),
                        applied_rule={"type": "integer"},
                        official_source_url=official_url,
                    )
            except (ValueError, TypeError):
                return ValidateResponse(
                    is_valid=False,
                    field_key=field_key,
                    target_language=target_language,
                    error_code="INVALID_NUMBER",
                    error_message=_msg("INVALID_NUMBER", target_language),
                    applied_rule={"type": "number"},
                    official_source_url=official_url,
                )

            # Check min and max
            if "min" in rules and num_val < rules["min"]:
                return ValidateResponse(
                    is_valid=False,
                    field_key=field_key,
                    target_language=target_language,
                    error_code="NUMERIC_MIN_VIOLATION",
                    error_message=_msg("NUMERIC_MIN_VIOLATION", target_language, min=rules["min"]),
                    applied_rule={"min": rules["min"]},
                    official_source_url=official_url,
                )

            if "max" in rules and num_val > rules["max"]:
                return ValidateResponse(
                    is_valid=False,
                    field_key=field_key,
                    target_language=target_language,
                    error_code="NUMERIC_MAX_VIOLATION",
                    error_message=_msg("NUMERIC_MAX_VIOLATION", target_language, max=rules["max"]),
                    applied_rule={"max": rules["max"]},
                    official_source_url=official_url,
                )

        elif field_type == "boolean" or rules.get("type") == "boolean":
            if not isinstance(value, bool) and str(value).lower() not in ("true", "false", "0", "1"):
                return ValidateResponse(
                    is_valid=False,
                    field_key=field_key,
                    target_language=target_language,
                    error_code="INVALID_BOOLEAN",
                    error_message=_msg("INVALID_BOOLEAN", target_language),
                    applied_rule={"type": "boolean"},
                    official_source_url=official_url,
                )

        # 3. String Length Rules
        if isinstance(value, str):
            val_len = len(value.strip())
            if "min_length" in rules and val_len < rules["min_length"]:
                return ValidateResponse(
                    is_valid=False,
                    field_key=field_key,
                    target_language=target_language,
                    error_code="MIN_LENGTH_VIOLATION",
                    error_message=_msg("MIN_LENGTH_VIOLATION", target_language, min_length=rules["min_length"]),
                    applied_rule={"min_length": rules["min_length"]},
                    official_source_url=official_url,
                )

            if "max_length" in rules and val_len > rules["max_length"]:
                return ValidateResponse(
                    is_valid=False,
                    field_key=field_key,
                    target_language=target_language,
                    error_code="MAX_LENGTH_VIOLATION",
                    error_message=_msg("MAX_LENGTH_VIOLATION", target_language, max_length=rules["max_length"]),
                    applied_rule={"max_length": rules["max_length"]},
                    official_source_url=official_url,
                )

            # 4. Pattern / Regex Rule
            pattern_str = rules.get("pattern")
            if pattern_str:
                try:
                    # In Python standard re, \p{L} is not built-in without regex module;
                    # simplify or translate \p{L} to word character unicode range if present
                    safe_pattern = pattern_str.replace("\\p{L}", r"\w")
                    if not re.search(safe_pattern, value.strip(), re.UNICODE):
                        return ValidateResponse(
                            is_valid=False,
                            field_key=field_key,
                            target_language=target_language,
                            error_code="PATTERN_MISMATCH",
                            error_message=_msg("PATTERN_MISMATCH", target_language),
                            applied_rule={"pattern": pattern_str},
                            official_source_url=official_url,
                        )
                except re.error:
                    pass

        # All deterministic rules passed
        return ValidateResponse(
            is_valid=True,
            field_key=field_key,
            target_language=target_language,
            error_code=None,
            error_message=None,
            applied_rule=rules,
            official_source_url=official_url,
        )

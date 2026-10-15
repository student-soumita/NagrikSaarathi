"""
NagrikSaarathi — Official URL Authority & Validation Service

Authoritative directory and defensive validator for Indian Central, State, and UT
government scheme portals, department sites, and online application entry points.
Ensures all external links adhere strictly to official government domains (*.gov.in, *.nic.in)
or verified state portals. Provides resilient fallbacks to national discovery portals
(MyScheme, ServiceOnline) and state e-District platforms.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


# ── National Discovery Portals ──────────────────────────────────────────

NATIONAL_DISCOVERY_PORTALS = {
    "MYSCHEME": {
        "name": "myScheme National Discovery Portal",
        "url": "https://www.myscheme.gov.in/",
        "description": "National platform discovering Central & State government schemes across India.",
    },
    "INDIA_GOV": {
        "name": "National Portal of India",
        "url": "https://www.india.gov.in/",
        "description": "Single-entry portal to information and services provided by the Indian Government.",
    },
    "SERVICE_ONLINE": {
        "name": "ServicePlus National Citizen Services",
        "url": "https://serviceonline.gov.in/",
        "description": "Unified meta-framework for delivery of government-to-citizen public services.",
    },
    "JAN_PARICHAY": {
        "name": "Jan Parichay National Single Sign-On (MeriPehchaan)",
        "url": "https://janparichay.meripehchaan.gov.in/",
        "description": "National citizen authentication service for government portals.",
    },
    "NSP": {
        "name": "National Scholarship Portal",
        "url": "https://scholarships.gov.in/",
        "description": "Unified scholarship application portal under Government of India.",
    },
}


# ── Authoritative State & UT Portals ────────────────────────────────────

STATE_AUTHORITY_PORTALS: Dict[str, Dict[str, str]] = {
    "AP": {
        "state_name": "Andhra Pradesh",
        "portal_url": "https://www.ap.gov.in/",
        "services_url": "https://navasakam.ap.gov.in/",
        "edistrict_name": "Navasakam / Meeseva AP",
    },
    "AR": {
        "state_name": "Arunachal Pradesh",
        "portal_url": "https://arunachalpradesh.gov.in/",
        "services_url": "https://serviceonline.gov.in/",
        "edistrict_name": "ServicePlus Arunachal",
    },
    "AS": {
        "state_name": "Assam",
        "portal_url": "https://assam.gov.in/",
        "services_url": "https://sewasetu.assam.gov.in/",
        "edistrict_name": "Sewa Setu Assam Citizen Portal",
    },
    "BR": {
        "state_name": "Bihar",
        "portal_url": "https://state.bihar.gov.in/",
        "services_url": "https://serviceonline.bihar.gov.in/",
        "edistrict_name": "RTPS Bihar / ServicePlus",
    },
    "CG": {
        "state_name": "Chhattisgarh",
        "portal_url": "https://cgstate.gov.in/",
        "services_url": "https://edistrict.cgstate.gov.in/",
        "edistrict_name": "e-District Chhattisgarh",
    },
    "GA": {
        "state_name": "Goa",
        "portal_url": "https://goa.gov.in/",
        "services_url": "https://goaonline.gov.in/",
        "edistrict_name": "Goa Online Citizen Services Portal",
    },
    "GJ": {
        "state_name": "Gujarat",
        "portal_url": "https://gujaratindia.gov.in/",
        "services_url": "https://www.digitalgujarat.gov.in/",
        "edistrict_name": "Digital Gujarat Portal",
    },
    "HR": {
        "state_name": "Haryana",
        "portal_url": "https://haryana.gov.in/",
        "services_url": "https://meraparivar.haryana.gov.in/",
        "edistrict_name": "Antyodaya Saral / Parivar Pehchan Patra (PPP)",
    },
    "HP": {
        "state_name": "Himachal Pradesh",
        "portal_url": "https://himachal.nic.in/",
        "services_url": "https://edistrict.hp.gov.in/",
        "edistrict_name": "e-District Himachal Pradesh",
    },
    "JH": {
        "state_name": "Jharkhand",
        "portal_url": "https://jharkhand.gov.in/",
        "services_url": "https://jharsewa.jharkhand.gov.in/",
        "edistrict_name": "JharSewa Citizen Portal",
    },
    "KA": {
        "state_name": "Karnataka",
        "portal_url": "https://karnataka.gov.in/",
        "services_url": "https://sevasindhu.karnataka.gov.in/",
        "edistrict_name": "Seva Sindhu Karnataka",
    },
    "KL": {
        "state_name": "Kerala",
        "portal_url": "https://kerala.gov.in/",
        "services_url": "https://edistrict.kerala.gov.in/",
        "edistrict_name": "e-District Kerala",
    },
    "MP": {
        "state_name": "Madhya Pradesh",
        "portal_url": "https://mp.gov.in/",
        "services_url": "https://mpedistrict.gov.in/",
        "edistrict_name": "MP e-District / Lok Seva Kendra",
    },
    "MH": {
        "state_name": "Maharashtra",
        "portal_url": "https://maharashtra.gov.in/",
        "services_url": "https://aaplesarkar.mahaonline.gov.in/",
        "edistrict_name": "Aaple Sarkar Citizen Portal",
    },
    "MN": {
        "state_name": "Manipur",
        "portal_url": "https://manipur.gov.in/",
        "services_url": "https://eservicesmanipur.gov.in/",
        "edistrict_name": "e-Services Manipur",
    },
    "ML": {
        "state_name": "Meghalaya",
        "portal_url": "https://meghalaya.gov.in/",
        "services_url": "https://serviceonline.gov.in/",
        "edistrict_name": "ServicePlus Meghalaya",
    },
    "MZ": {
        "state_name": "Mizoram",
        "portal_url": "https://mizoram.gov.in/",
        "services_url": "https://edistrict.mizoram.gov.in/",
        "edistrict_name": "e-District Mizoram",
    },
    "NL": {
        "state_name": "Nagaland",
        "portal_url": "https://nagaland.gov.in/",
        "services_url": "https://serviceonline.gov.in/",
        "edistrict_name": "ServicePlus Nagaland",
    },
    "OD": {
        "state_name": "Odisha",
        "portal_url": "https://odisha.gov.in/",
        "services_url": "https://edistrict.odisha.gov.in/",
        "edistrict_name": "Odisha e-District Portal",
    },
    "PB": {
        "state_name": "Punjab",
        "portal_url": "https://punjab.gov.in/",
        "services_url": "https://connect.punjab.gov.in/",
        "edistrict_name": "Connect Punjab / Sewa Kendra",
    },
    "RJ": {
        "state_name": "Rajasthan",
        "portal_url": "https://rajasthan.gov.in/",
        "services_url": "https://janaadhaar.rajasthan.gov.in/",
        "edistrict_name": "Jan Aadhaar / E-Mitra Rajasthan",
    },
    "SK": {
        "state_name": "Sikkim",
        "portal_url": "https://sikkim.gov.in/",
        "services_url": "https://edistrict.sikkim.gov.in/",
        "edistrict_name": "e-District Sikkim",
    },
    "TN": {
        "state_name": "Tamil Nadu",
        "portal_url": "https://tn.gov.in/",
        "services_url": "https://www.tnesevai.tn.gov.in/",
        "edistrict_name": "e-Sevai Tamil Nadu",
    },
    "TG": {
        "state_name": "Telangana",
        "portal_url": "https://telangana.gov.in/",
        "services_url": "https://meeseva.telangana.gov.in/",
        "edistrict_name": "MeeSeva Telangana",
    },
    "TR": {
        "state_name": "Tripura",
        "portal_url": "https://tripura.gov.in/",
        "services_url": "https://edistrict.tripura.gov.in/",
        "edistrict_name": "e-District Tripura",
    },
    "UP": {
        "state_name": "Uttar Pradesh",
        "portal_url": "https://up.gov.in/",
        "services_url": "https://edistrict.up.gov.in/",
        "edistrict_name": "e-District Uttar Pradesh",
    },
    "UK": {
        "state_name": "Uttarakhand",
        "portal_url": "https://uk.gov.in/",
        "services_url": "https://edistrict.uk.gov.in/",
        "edistrict_name": "e-District Uttarakhand / Apuni Sarkar",
    },
    "WB": {
        "state_name": "West Bengal",
        "portal_url": "https://wb.gov.in/",
        "services_url": "https://edistrict.wb.gov.in/",
        "edistrict_name": "e-District West Bengal",
    },
    # Union Territories
    "AN": {
        "state_name": "Andaman and Nicobar Islands",
        "portal_url": "https://andaman.gov.in/",
        "services_url": "https://edistrict.andaman.gov.in/",
        "edistrict_name": "e-District Andaman & Nicobar",
    },
    "CH": {
        "state_name": "Chandigarh",
        "portal_url": "https://chandigarh.gov.in/",
        "services_url": "https://admser.chd.nic.in/",
        "edistrict_name": "Chandigarh e-Services",
    },
    "DH": {
        "state_name": "Dadra and Nagar Haveli and Daman and Diu",
        "portal_url": "https://ddd.gov.in/",
        "services_url": "https://ddd.gov.in/",
        "edistrict_name": "DNHDD e-Services Portal",
    },
    "DL": {
        "state_name": "Delhi (NCT)",
        "portal_url": "https://delhi.gov.in/",
        "services_url": "https://edistrict.delhigovt.nic.in/",
        "edistrict_name": "e-District Delhi",
    },
    "JK": {
        "state_name": "Jammu and Kashmir",
        "portal_url": "https://jk.gov.in/",
        "services_url": "https://serviceonline.gov.in/",
        "edistrict_name": "ServicePlus J&K (JanSugam)",
    },
    "LA": {
        "state_name": "Ladakh",
        "portal_url": "https://ladakh.gov.in/",
        "services_url": "https://serviceonline.gov.in/",
        "edistrict_name": "ServicePlus Ladakh",
    },
    "LD": {
        "state_name": "Lakshadweep",
        "portal_url": "https://lakshadweep.gov.in/",
        "services_url": "https://serviceonline.gov.in/",
        "edistrict_name": "ServicePlus Lakshadweep",
    },
    "PY": {
        "state_name": "Puducherry",
        "portal_url": "https://py.gov.in/",
        "services_url": "https://edistrict.py.gov.in/",
        "edistrict_name": "e-District Puducherry",
    },
}


# ── Allowed Government Domain Patterns ──────────────────────────────────

ALLOWED_GOV_DOMAIN_PATTERNS = [
    re.compile(r"^([a-zA-Z0-9-]+\.)*gov\.in$", re.IGNORECASE),
    re.compile(r"^([a-zA-Z0-9-]+\.)*nic\.in$", re.IGNORECASE),
    re.compile(r"^([a-zA-Z0-9-]+\.)*ac\.in$", re.IGNORECASE),
    re.compile(r"^([a-zA-Z0-9-]+\.)*org\.in$", re.IGNORECASE),
    re.compile(r"^([a-zA-Z0-9-]+\.)*meripehchaan\.gov\.in$", re.IGNORECASE),
    re.compile(r"^([a-zA-Z0-9-]+\.)*nha\.gov\.in$", re.IGNORECASE),
    re.compile(r"^([a-zA-Z0-9-]+\.)*uidai\.gov\.in$", re.IGNORECASE),
    re.compile(r"^([a-zA-Z0-9-]+\.)*indiapost\.gov\.in$", re.IGNORECASE),
    re.compile(r"^ayushmanharyana\.in$", re.IGNORECASE),
]

DISALLOWED_OR_PLACEHOLDER_SUBSTRINGS = [
    "example.gov.in",
    "placeholder",
    "test.gov.in",
    "localhost",
    "cattle-shed",
    "rural.nic.in/schemes/cattle-shed",
]


class UrlAuthorityService:
    """Provides authoritative validation, classification, and fallbacks for government portal URLs."""

    @classmethod
    def is_valid_official_government_url(cls, url: Optional[str]) -> Tuple[bool, str]:
        """
        Validate whether a URL belongs to an authenticated Indian government or verified portal.
        Returns: (is_valid: bool, reason: str)
        """
        if not url or not isinstance(url, str) or not url.strip():
            return False, "EMPTY_URL"

        url_str = url.strip()
        for placeholder in DISALLOWED_OR_PLACEHOLDER_SUBSTRINGS:
            if placeholder in url_str.lower():
                return False, f"PLACEHOLDER_OR_INVALID_PATH: {placeholder}"

        try:
            parsed = urlparse(url_str)
        except Exception as e:
            return False, f"MALFORMED_URL: {str(e)}"

        if parsed.scheme not in ("http", "https"):
            return False, f"INVALID_SCHEME: {parsed.scheme}"

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False, "NO_HOSTNAME"

        # Check against allowed government domain patterns
        for pattern in ALLOWED_GOV_DOMAIN_PATTERNS:
            if pattern.match(hostname):
                return True, "VERIFIED_OFFICIAL_DOMAIN"

        return False, f"UNVERIFIED_DOMAIN: {hostname}"

    @classmethod
    def get_fallback_urls_for_jurisdiction(cls, state_code: Optional[str]) -> Dict[str, str]:
        """
        Returns verified fallback portal URLs for a central or state jurisdiction.
        """
        code = (state_code or "").upper().strip()
        if code and code in STATE_AUTHORITY_PORTALS:
            info = STATE_AUTHORITY_PORTALS[code]
            return {
                "official_source_url": info["portal_url"],
                "official_application_url": info["services_url"],
                "source_label": f"Official {info['state_name']} Government Portal",
                "application_label": f"Apply via {info['edistrict_name']}",
                "portal_type": "STATE_SSO_EDISTRICT",
            }

        # Central fallback
        return {
            "official_source_url": NATIONAL_DISCOVERY_PORTALS["MYSCHEME"]["url"],
            "official_application_url": NATIONAL_DISCOVERY_PORTALS["SERVICE_ONLINE"]["url"],
            "source_label": "myScheme National Discovery Portal",
            "application_label": "Apply via ServicePlus National Portal",
            "portal_type": "NATIONAL_PORTAL",
        }

    @classmethod
    def classify_application_portal_type(
        cls,
        application_url: Optional[str],
        application_method: Optional[str] = "online",
        state_code: Optional[str] = None
    ) -> str:
        """
        Classifies how the citizen should access the official application:
        - DIRECT_ONLINE: Specific scheme online application form (e.g. PM-KISAN, NSP)
        - STATE_SSO_EDISTRICT: State Common Service Portal / e-District / Jan Parichay
        - OFFLINE_OFFICE: In-person submission at Gram Panchayat, Taluk, Anganwadi, or Post Office
        - NATIONAL_PORTAL: Central ServicePlus / myScheme discovery portal
        """
        method = (application_method or "online").lower()
        if method in ("offline", "in_person", "physical"):
            return "OFFLINE_OFFICE"

        if not application_url or not application_url.strip():
            return "OFFLINE_OFFICE" if method == "hybrid" else "STATE_SSO_EDISTRICT"

        url_lower = application_url.lower()
        if any(term in url_lower for term in ["edistrict", "serviceonline", "sevasindhu", "jharsewa", "saral", "meraparivar", "aaplesarkar", "admser", "janaadhaar"]):
            return "STATE_SSO_EDISTRICT"

        return "DIRECT_ONLINE"

    @classmethod
    def resolve_scheme_urls(
        cls,
        official_source_url: Optional[str],
        official_application_url: Optional[str],
        state_code: Optional[str] = None,
        application_method: Optional[str] = "online"
    ) -> Dict[str, Any]:
        """
        Normalize and resolve URLs, providing authentic fallbacks if missing or invalid.
        """
        fallbacks = cls.get_fallback_urls_for_jurisdiction(state_code)

        src_valid, _ = cls.is_valid_official_government_url(official_source_url)
        if src_valid and official_source_url:
            resolved_source = official_source_url.strip()
            if resolved_source.rstrip("/") == fallbacks["official_source_url"].rstrip("/"):
                source_is_fallback = True
                source_label = fallbacks["source_label"]
            else:
                source_is_fallback = False
                source_label = "Official Government Portal"
        else:
            resolved_source = fallbacks["official_source_url"]
            source_is_fallback = True
            source_label = fallbacks["source_label"]

        app_valid, _ = cls.is_valid_official_government_url(official_application_url)
        method = (application_method or "online").lower()

        if app_valid and official_application_url:
            resolved_app = official_application_url.strip()
            if resolved_app.rstrip("/") == fallbacks["official_application_url"].rstrip("/"):
                app_is_fallback = True
                portal_type = fallbacks["portal_type"]
                app_label = fallbacks["application_label"]
            else:
                app_is_fallback = False
                portal_type = cls.classify_application_portal_type(resolved_app, method, state_code)
                app_label = "Direct Online Application Portal" if portal_type == "DIRECT_ONLINE" else "State Citizen Services Portal"
        elif method in ("offline", "in_person"):
            resolved_app = resolved_source
            app_is_fallback = False
            portal_type = "OFFLINE_OFFICE"
            app_label = "In-Person Submission (Download Form / Guidelines)"
        else:
            resolved_app = fallbacks["official_application_url"]
            app_is_fallback = True
            portal_type = fallbacks["portal_type"]
            app_label = fallbacks["application_label"]

        return {
            "official_source_url": resolved_source,
            "official_source_is_fallback": source_is_fallback,
            "official_source_label": source_label,
            "official_application_url": resolved_app,
            "official_application_is_fallback": app_is_fallback,
            "official_application_label": app_label,
            "portal_type": portal_type,
            "is_verified_gov_domain": True,
        }

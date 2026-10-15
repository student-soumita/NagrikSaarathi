"""
NagrikSaarathi — Scheme Benefit Enrichment Service
Provides verified, authoritative benefit details for central and state schemes.
Strictly avoids inventing cash amounts or unverified figures.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


# Verified official benefit registries for national flagship schemes
VERIFIED_BENEFITS: Dict[str, Dict[str, Any]] = {
    "pm-kisan": {
        "assistance_type": "Financial Assistance (Direct Income Support)",
        "benefit_amount": "₹6,000 per year",
        "frequency_or_duration": "Three equal instalments of ₹2,000 every four months",
        "benefits_provided": "Direct income support transferred straight into Aadhaar-seeded bank accounts of landholding farmer families.",
        "conditions_limitations": "Beneficiary must be a landholder family. Institutional landholders, high-income taxpayers, and constitutional post holders are excluded.",
        "is_verified": True,
    },
    "ayushman-bharat-pmjay": {
        "assistance_type": "Healthcare Coverage (Cashless Hospitalisation)",
        "benefit_amount": "Up to ₹5,00,000 per family per year",
        "frequency_or_duration": "Annual renewable health cover",
        "benefits_provided": "Cashless secondary and tertiary hospitalisation care across all empanelled public and private hospitals across India.",
        "conditions_limitations": "Covers families identified under SECC 2011 deprivation and occupational criteria. No restriction on family size, age, or gender.",
        "is_verified": True,
    },
    "pm-awas-yojana-gramin": {
        "assistance_type": "Housing Assistance (Construction Grant)",
        "benefit_amount": "₹1,20,000 (Plains) / ₹1,30,000 (Hilly/Difficult areas)",
        "frequency_or_duration": "Paid in instalments linked to construction stages (plinth, roof, completion)",
        "benefits_provided": "Financial grant for construction of pucca house with basic amenities including clean cooking fuel, electricity, and water connection.",
        "conditions_limitations": "Must not own a pucca house anywhere in India. House size minimum 25 sq. metres including hygienic cooking space.",
        "is_verified": True,
    },
    "post-matric-scholarship-sc": {
        "assistance_type": "Education Scholarship (Tuition Fee & Maintenance Allowance)",
        "benefit_amount": "Full non-refundable compulsory course fee + maintenance allowance as per group",
        "frequency_or_duration": "Annual course duration via DBT",
        "benefits_provided": "Financial assistance covering compulsory non-refundable fees and monthly maintenance allowances for post-matriculation studies.",
        "conditions_limitations": "Annual family income from all sources must not exceed ₹2,50,000. Applicable for recognised post-matric/post-secondary courses.",
        "is_verified": True,
    },
    "atal-pension-yojana": {
        "assistance_type": "Social Security Pension",
        "benefit_amount": "Guaranteed monthly pension of ₹1,000, ₹2,000, ₹3,000, ₹4,000, or ₹5,000",
        "frequency_or_duration": "Lifelong monthly pension starting at age 60",
        "benefits_provided": "Guaranteed minimum monthly pension to the subscriber with spouse pension and nominee corpus return upon death.",
        "conditions_limitations": "Entry age 18 to 40 years. Must have savings bank account. Income taxpayers cannot join since Oct 2022.",
        "is_verified": True,
    },
    "pm-svanidhi": {
        "assistance_type": "Micro-Credit / Working Capital Loan",
        "benefit_amount": "1st tranche: ₹10,000, 2nd tranche: ₹20,000, 3rd tranche: ₹50,000",
        "frequency_or_duration": "Collateral-free working capital loan with 7% interest subsidy on timely repayment",
        "benefits_provided": "Affordable working capital credit to street vendors to resume livelihoods, plus cashback incentives on digital transactions.",
        "conditions_limitations": "Vendor must possess Certificate of Vending / ID card issued by Urban Local Body or recommendation letter.",
        "is_verified": True,
    },
    "pm-matru-vandana-yojana": {
        "assistance_type": "Maternity Benefit (Cash Incentive via DBT)",
        "benefit_amount": "₹5,000 for 1st child (2 instalments); ₹6,000 for 2nd child (girl child only)",
        "frequency_or_duration": "Paid in instalments upon pregnancy registration and institutional birth",
        "benefits_provided": "Cash incentive for wage compensation during childbirth and to encourage institutional delivery and child immunisation.",
        "conditions_limitations": "Pregnant and lactating mothers who are not in regular government employment.",
        "is_verified": True,
    },
}


class SchemeBenefitService:
    @staticmethod
    def resolve_benefit_details(scheme: Any) -> Dict[str, Any]:
        """
        Produce authoritative, verified benefit information for a scheme.
        If verified official gazette info exists in DB or verified registry, use it.
        Otherwise, provide factual non-fabricated summary with 'Benefit details not yet verified'.
        """
        # If already populated in DB and verified
        db_details = getattr(scheme, "benefit_details", None)
        if isinstance(db_details, dict) and db_details.get("is_verified") and db_details.get("benefits_provided"):
            return db_details

        slug = getattr(scheme, "slug", "")
        # Check against canonical verified registry
        for key, verified in VERIFIED_BENEFITS.items():
            if key in slug:
                res = dict(verified)
                res["intended_beneficiaries"] = getattr(scheme, "beneficiary_groups", []) or ["Eligible citizens"]
                res["official_source_url"] = getattr(scheme, "official_source_url", "")
                res["last_verified_at"] = getattr(scheme, "last_verified_at", None)
                res["verification_status"] = getattr(scheme, "verification_status", "verified")
                return res

        # Derive safe category-based assistance type without inventing numerical amounts
        category = (getattr(scheme, "category", "") or "other").lower()
        cat_assistance_map = {
            "agriculture": "Agricultural Subsidy & Farming Support",
            "education": "Educational Scholarship / Tuition Assistance",
            "health": "Medical Care & Healthcare Assistance",
            "housing": "Housing Construction & Shelter Assistance",
            "social_welfare": "Social Security & Welfare Assistance",
            "women_child": "Women & Child Nutrition / Welfare Support",
            "employment": "Skill Development & Livelihood Support",
            "finance": "Financial Credit & Subsidy Support",
        }
        assistance_type = cat_assistance_map.get(category, "Government Public Welfare Service")

        # Factual, un-fabricated default with unverified banner
        return {
            "assistance_type": assistance_type,
            "benefit_amount": None,  # Strictly None: never fabricate
            "frequency_or_duration": None,
            "benefits_provided": getattr(scheme, "description", "") or "Official citizen welfare scheme assistance.",
            "intended_beneficiaries": getattr(scheme, "beneficiary_groups", []) or ["Eligible citizens meeting criteria"],
            "conditions_limitations": "Subject to fulfilment of official eligibility and document requirements published by the nodal authority.",
            "is_verified": False,
            "verification_status": getattr(scheme, "verification_status", "pending_review"),
            "official_source_url": getattr(scheme, "official_source_url", ""),
            "last_verified_at": getattr(scheme, "last_verified_at", None),
            "unverified_notice": "Benefit details not yet verified from official gazette notification.",
        }

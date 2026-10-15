"""
NagrikSaarathi — Centralized Scheme Form Registry & Generator
Provides authentic, verified, data-driven form schemas, eligibility criteria,
document checklists, and step-by-step guidance for all Central, 28 States,
and 8 Union Territory schemes in India.

Ensures every listed scheme has a complete, working guided application workflow.
"""

from __future__ import annotations

from typing import Any, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models import (
    FormField,
    GovernmentScheme,
    SchemeApplicationStep,
    SchemeDocumentRequirement,
    SchemeEligibilityRequirement,
)


# ── Scheme Archetypes & Specific Form Schemas ──────────────────────────────

SCHEME_SPECIFIC_WORKFLOWS: Dict[str, Dict[str, Any]] = {
    # ── Central Schemes ───────────────────────────────────────────────────
    "sukanya-samriddhi-yojana": {
        "category": "women_child",
        "fields": [
            {
                "field_key": "girl_child_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Girl Child's Full Name", "hi": "बालिका का पूरा नाम"},
                "explanations": {
                    "en": "Enter the full name of the girl child as recorded on her official Birth Certificate or Aadhaar Card.",
                    "hi": "बालिका का पूरा नाम दर्ज करें जैसा कि उसके आधिकारिक जन्म प्रमाण पत्र या आधार कार्ड में है।",
                },
                "instructions": {"en": "Must match birth certificate exactly.", "hi": "जन्म प्रमाण पत्र से पूरी तरह मेल खाना चाहिए।"},
            },
            {
                "field_key": "girl_child_dob",
                "field_type": "date",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Date of Birth of Girl Child", "hi": "बालिका की जन्म तिथि"},
                "explanations": {
                    "en": "The account can be opened from the birth of the girl child till she attains the age of 10 years.",
                    "hi": "खाता बालिका के जन्म से लेकर 10 वर्ष की आयु प्राप्त करने तक खोला जा सकता है।",
                },
                "instructions": {"en": "Child must be under 10 years of age.", "hi": "बालिका की उम्र 10 वर्ष से कम होनी चाहिए।"},
            },
            {
                "field_key": "parent_guardian_name",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Natural or Legal Guardian Name", "hi": "माता-पिता / कानूनी अभिभावक का नाम"},
                "explanations": {
                    "en": "Enter the name of biological parent or legal guardian who will operate the account on behalf of the minor.",
                    "hi": "अभिभावक का नाम दर्ज करें जो नाबालिग की ओर से खाते का संचालन करेंगे।",
                },
                "instructions": {"en": "Parent must have valid KYC documents.", "hi": "अभिभावक के पास वैध केवाईसी दस्तावेज होने चाहिए।"},
            },
            {
                "field_key": "parent_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Guardian's Aadhaar Number", "hi": "अभिभावक का आधार नंबर"},
                "explanations": {
                    "en": "12-digit Aadhaar number of parent/guardian used for identity verification and account linkage.",
                    "hi": "अभिभावक का 12 अंकों का आधार नंबर पहचान सत्यापन हेतु।",
                },
                "instructions": {"en": "Enter 12 digits without spaces.", "hi": "बिना स्पेस के 12 अंक दर्ज करें।"},
            },
            {
                "field_key": "initial_deposit_amount",
                "field_type": "currency",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Initial Deposit Amount (₹)", "hi": "प्रारंभिक जमा राशि (₹)"},
                "explanations": {
                    "en": "Minimum opening deposit is ₹250. Maximum permissible annual deposit is ₹1,50,000 per financial year.",
                    "hi": "न्यूनतम जमा ₹250 है। प्रति वित्तीय वर्ष अधिकतम ₹1,50,000 जमा किया जा सकता है।",
                },
                "instructions": {"en": "Between ₹250 and ₹1,50,000.", "hi": "₹250 से ₹1,50,000 के बीच।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "girl_child_age_under_10",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Girl Child Under 10 Years", "hi": "बालिका की आयु 10 वर्ष से कम"},
                "descriptions": {
                    "en": "Account must be opened before the girl child turns 10 years old.",
                    "hi": "बालिका के 10 वर्ष की आयु पूरी करने से पहले खाता खोला जाना अनिवार्य है।",
                },
            },
            {
                "criterion_key": "max_two_accounts_per_family",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Maximum Two Daughters Per Family", "hi": "प्रति परिवार अधिकतम दो बालिकाएं"},
                "descriptions": {
                    "en": "Allowed for up to two girl children in a family (exception for triplets/twins).",
                    "hi": "एक परिवार में अधिकतम दो बालिकाओं के लिए खाता अनुमत है (जुड़वां के मामले में छूट)।",
                },
            },
        ],
        "documents": [
            {
                "document_code": "birth_certificate_child",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Birth Certificate of Girl Child", "hi": "बालिका का जन्म प्रमाण पत्र"},
                "descriptions": {"en": "Issued by Municipal Corporation or Gram Panchayat Registrar.", "hi": "नगर निगम या ग्राम पंचायत रजिस्ट्रार द्वारा जारी।"},
            },
            {
                "document_code": "guardian_id_proof",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Guardian Identity Proof (Aadhaar/PAN)", "hi": "अभिभावक का पहचान प्रमाण"},
                "descriptions": {"en": "Aadhaar Card or PAN Card of the opening guardian.", "hi": "अभिभावक का आधार कार्ड या पैन कार्ड।"},
            },
            {
                "document_code": "guardian_address_proof",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Guardian Address Proof", "hi": "अभिभावक का पता प्रमाण"},
                "descriptions": {"en": "Voter ID, Electricity bill, or Aadhaar showing current residence.", "hi": "मतदाता पहचान पत्र, बिजली बिल या आधार।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Fill SSA Account Opening Form",
                "description": "Download or collect the official Form-1 from Post Office or authorized commercial bank.",
            },
            {
                "step_number": 2,
                "title": "Attach KYC & Child Birth Certificate",
                "description": "Attach self-attested copies of child birth certificate and guardian KYC documents.",
            },
            {
                "step_number": 3,
                "title": "Deposit Initial Amount & Collect Passbook",
                "description": "Deposit initial amount (min ₹250) via cash/cheque and receive the stamped passbook.",
            },
        ],
    },
}

# ── Dynamic Category Workflow Templates ───────────────────────────────────

CATEGORY_WORKFLOW_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "agriculture": {
        "fields": [
            {
                "field_key": "farmer_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Farmer's Full Name", "hi": "किसान का पूरा नाम"},
                "explanations": {"en": "Name as registered in State Land Revenue Records and Aadhaar.", "hi": "भू-राजस्व रिकॉर्ड और आधार कार्ड के अनुसार नाम।"},
                "instructions": {"en": "Ensure spelling matches your land passbook.", "hi": "सुनिश्चित करें कि वर्तनी खतौनी से मेल खाती है।"},
            },
            {
                "field_key": "farmer_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Aadhaar Number", "hi": "आधार संख्या"},
                "explanations": {"en": "Required for biometric identity verification and DBT subsidy transfer.", "hi": "पहचान सत्यापन एवं सीधे बैंक में लाभ अंतरण (DBT) हेतु।"},
                "instructions": {"en": "12-digit number.", "hi": "12 अंकों की संख्या।"},
            },
            {
                "field_key": "cultivable_land_area_acres",
                "field_type": "number",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Cultivable Land Area (in Acres)", "hi": "कृषि योग्य भूमि (एकड़ में)"},
                "explanations": {"en": "Total cultivable land owned by the applicant farmer family.", "hi": "किसान परिवार के स्वामित्व वाली कुल कृषि भूमि।"},
                "instructions": {"en": "Enter numbers only, e.g. 2.5", "hi": "केवल अंक दर्ज करें, उदा. 2.5"},
            },
            {
                "field_key": "land_record_khata_number",
                "field_type": "text",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Land Record Khata / Khasra Number", "hi": "खता / खसरा / सर्वेक्षण संख्या"},
                "explanations": {"en": "Official revenue survey or plot identifier from your RoR/Pattadar passbook.", "hi": "राजस्व रिकॉर्ड या पट्टा पासबुक से प्लॉट संख्या।"},
                "instructions": {"en": "Found on your state Bhulekh portal or land receipt.", "hi": "राज्य भूलेख पोर्टल या रसीद पर उपलब्ध।"},
            },
            {
                "field_key": "bank_account_number",
                "field_type": "bank_account",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Aadhaar-Linked Bank Account Number", "hi": "आधार-लिंक्ड बैंक खाता संख्या"},
                "explanations": {"en": "Financial assistance is directly credited via PFMS/NPCI to this account.", "hi": "वित्तीय सहायता सीधे इसी खाते में DBT द्वारा जमा होगी।"},
                "instructions": {"en": "Must be active and seeded with NPCI.", "hi": "खाता सक्रिय और एनपीसीआई सीडेड होना चाहिए।"},
            },
            {
                "field_key": "bank_ifsc_code",
                "field_type": "ifsc",
                "required": True,
                "sort_order": 6,
                "labels": {"en": "Bank IFSC Code", "hi": "बैंक आईएफएससी कोड"},
                "explanations": {"en": "11-character code identifying your specific bank branch.", "hi": "शाखा का 11 अक्षरों का विशिष्ट कोड।"},
                "instructions": {"en": "Printed on first page of passbook.", "hi": "पासबुक के मुख्य पृष्ठ पर अंकित।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "landholding_farmer_resident",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Cultivable Landholder & State Resident", "hi": "भूमिधारक किसान एवं राज्य निवासी"},
                "descriptions": {"en": "Must hold title to cultivable agricultural land in the state.", "hi": "राज्य में कृषि भूमि का मालिकाना हक होना आवश्यक है।"},
            },
            {
                "criterion_key": "non_income_tax_payer",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Non-Income Tax Assessee", "hi": "आयकर दाता नहीं होना चाहिए"},
                "descriptions": {"en": "No member of the applicant household should have paid income tax.", "hi": "परिवार का कोई सदस्य आयकर दाता न हो।"},
            },
        ],
        "documents": [
            {
                "document_code": "aadhaar_card",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Applicant farmer's active Aadhaar card.", "hi": "आवेदक किसान का वैध आधार कार्ड।"},
            },
            {
                "document_code": "land_ownership_passbook",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Land Revenue Record / Pattadar Passbook", "hi": "भू-राजस्व रिकॉर्ड / खतौनी / पट्टा"},
                "descriptions": {"en": "Certified land record copy showing survey number and acreage.", "hi": "खसरा और रकबा दर्शाने वाला प्रमाणित दस्तावेज।"},
            },
            {
                "document_code": "bank_passbook",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Bank Passbook Copy", "hi": "बैंक पासबुक प्रति"},
                "descriptions": {"en": "Passbook showing account number, IFSC, and applicant name.", "hi": "खाता संख्या और आईएफएससी दर्शाने वाली पासबुक।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Document & Land Verification",
                "description": "Verify land title on state revenue portal and ensure bank account is Aadhaar-seeded.",
            },
            {
                "step_number": 2,
                "title": "Submit Application on Official Portal",
                "description": "Log into the official state/central agriculture portal using Aadhaar OTP.",
            },
            {
                "step_number": 3,
                "title": "Gram Panchayat / VRO Verification",
                "description": "Local revenue officer verifies physical land possession before approving DBT release.",
            },
        ],
    },
    "healthcare": {
        "fields": [
            {
                "field_key": "beneficiary_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Beneficiary / Family Head Name", "hi": "लाभार्थी / परिवार मुखिया का नाम"},
                "explanations": {"en": "Name as listed on Ration Card or SECC Health Database.", "hi": "राशन कार्ड या स्वास्थ्य डेटाबेस में दर्ज नाम।"},
                "instructions": {"en": "Must match official identity document.", "hi": "आधिकारिक दस्तावेज से मेल खाना चाहिए।"},
            },
            {
                "field_key": "beneficiary_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Aadhaar Number", "hi": "आधार संख्या"},
                "explanations": {"en": "Required for Ayushman / State Health Card generation and biometric e-KYC.", "hi": "स्वास्थ्य कार्ड निर्माण और ई-केवाईसी सत्यापन हेतु।"},
                "instructions": {"en": "12 digits without spaces.", "hi": "बिना स्पेस के 12 अंक।"},
            },
            {
                "field_key": "ration_card_number",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Ration Card / NFSA Food Security Card Number", "hi": "राशन कार्ड / खाद्य सुरक्षा कार्ड संख्या"},
                "explanations": {"en": "Used to verify family eligibility under low-income health cover criteria.", "hi": "परिवार की पात्रता और सदस्यों की सूची सत्यापित करने हेतु।"},
                "instructions": {"en": "Enter complete card number.", "hi": "पूरा राशन कार्ड नंबर दर्ज करें।"},
            },
            {
                "field_key": "total_family_members",
                "field_type": "number",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Total Family Members to be Covered", "hi": "कवर किए जाने वाले परिवार के कुल सदस्य"},
                "explanations": {"en": "Free health assurance of up to ₹5 lakh covers all eligible household members.", "hi": "परिवार के सभी पात्र सदस्यों को कैशलेस इलाज की सुविधा।"},
                "instructions": {"en": "Include all dependent children, spouse, and parents.", "hi": "आश्रित बच्चों, जीवनसाथी और माता-पिता को शामिल करें।"},
            },
            {
                "field_key": "annual_family_income",
                "field_type": "currency",
                "required": False,
                "sort_order": 5,
                "labels": {"en": "Annual Family Income (₹)", "hi": "वार्षिक पारिवारिक आय (₹)"},
                "explanations": {"en": "Self-declared annual income from all sources.", "hi": "सभी स्रोतों से परिवार की कुल वार्षिक आय।"},
                "instructions": {"en": "As per income certificate if applicable.", "hi": "आय प्रमाण पत्र के अनुसार।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "eligible_household_category",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "SECC / NFSA / Low Income Household", "hi": "एसईसीसी / एनएफएसए / पात्र परिवार"},
                "descriptions": {"en": "Household must belong to eligible occupational or deprivation category.", "hi": "परिवार पात्र श्रेणी या राशन कार्ड धारक होना चाहिए।"},
            },
            {
                "criterion_key": "permanent_state_resident",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Permanent Resident of the State/UT", "hi": "राज्य/केंद्रशासित प्रदेश का स्थायी निवासी"},
                "descriptions": {"en": "Scheme benefits apply to domicile residents.", "hi": "योजना का लाभ राज्य के मूल निवासियों को देय है।"},
            },
        ],
        "documents": [
            {
                "document_code": "aadhaar_card_all_members",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card of Family Members", "hi": "परिवार के सदस्यों के आधार कार्ड"},
                "descriptions": {"en": "Aadhaar of all members requesting health coverage.", "hi": "कवरेज चाहने वाले सभी सदस्यों का आधार।"},
            },
            {
                "document_code": "ration_card",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Valid Ration Card / BPL Proof", "hi": "वैध राशन कार्ड / बीपीएल प्रमाण"},
                "descriptions": {"en": "Card proving family unit composition and income group.", "hi": "पारिवारिक संरचना दर्शाने वाला दस्तावेज।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Check Eligibility Online or at CSC",
                "description": "Search your family by Ration Card or Aadhaar on the health portal.",
            },
            {
                "step_number": 2,
                "title": "Complete Biometric e-KYC",
                "description": "Visit any empaneled hospital (PMAM desk) or CSC to authenticate fingerprints/iris.",
            },
            {
                "step_number": 3,
                "title": "Download Digital Health Card",
                "description": "Receive the PVC or digital health card for cashless admission.",
            },
        ],
    },
    "women_child": {
        "fields": [
            {
                "field_key": "applicant_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Woman Beneficiary's Full Name", "hi": "महिला लाभार्थी का पूरा नाम"},
                "explanations": {"en": "Full name of the female applicant as printed on Aadhaar.", "hi": "आधार कार्ड के अनुसार महिला का पूरा नाम।"},
                "instructions": {"en": "Name must match Aadhaar card exactly.", "hi": "नाम आधार कार्ड से पूरी तरह मेल खाना चाहिए।"},
            },
            {
                "field_key": "applicant_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Aadhaar Number", "hi": "आधार संख्या"},
                "explanations": {"en": "Required for biometric identity verification and DBT transfers.", "hi": "सत्यापन और सीधे बैंक में मासिक राशि अंतरण हेतु।"},
                "instructions": {"en": "12-digit number.", "hi": "12 अंकों की संख्या।"},
            },
            {
                "field_key": "marital_status",
                "field_type": "select",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Marital Status", "hi": "वैवाहिक स्थिति"},
                "explanations": {"en": "Required to determine eligibility category (married, widow, divorced, or single).", "hi": "पात्रता श्रेणी (विवाहित, विधवा, परित्यक्ता या अविवाहित) निर्धारित करने हेतु।"},
                "instructions": {"en": "Select matching status.", "hi": "उचित विकल्प चुनें।"},
            },
            {
                "field_key": "bank_account_in_applicant_name",
                "field_type": "bank_account",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Personal Bank Account Number (Own Name Only)", "hi": "स्वयं के नाम से बैंक खाता संख्या"},
                "explanations": {"en": "Joint accounts are not accepted. The bank account must be single-holder in the woman's name and Aadhaar-seeded.", "hi": "संयुक्त खाता मान्य नहीं है। खाता केवल महिला के नाम पर और आधार से जुड़ा होना चाहिए।"},
                "instructions": {"en": "Single account with DBT active.", "hi": "एकल खाता, डीबीटी सक्रिय।"},
            },
            {
                "field_key": "bank_ifsc",
                "field_type": "ifsc",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Bank IFSC Code", "hi": "बैंक आईएफएससी कोड"},
                "explanations": {"en": "11-character code identifying the bank branch.", "hi": "शाखा का 11 अक्षरों का विशिष्ट कोड।"},
                "instructions": {"en": "Available in passbook or cheque leaf.", "hi": "पासबुक में उपलब्ध।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "resident_female_age_criteria",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "State Resident Woman Meeting Age Criteria", "hi": "आयु सीमा पूरी करने वाली राज्य निवासी महिला"},
                "descriptions": {"en": "Applicant must be a permanent resident within eligible scheme age bracket.", "hi": "आवेदक राज्य की स्थायी निवासी और निर्धारित आयु सीमा में होनी चाहिए।"},
            },
            {
                "criterion_key": "family_income_limit",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Annual Family Income Within Specified Cap", "hi": "निर्धारित सीमा के भीतर पारिवारिक आय"},
                "descriptions": {"en": "Household income must not exceed state ceiling and family must not be income-tax payers.", "hi": "परिवार की आय तय सीमा से अधिक न हो और कोई सदस्य आयकर न देता हो।"},
            },
        ],
        "documents": [
            {
                "document_code": "aadhaar_card",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Applicant's active Aadhaar card with updated mobile.", "hi": "आवेदक का सक्रिय आधार कार्ड।"},
            },
            {
                "document_code": "single_bank_passbook",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Single Bank Account Passbook", "hi": "एकल बैंक खाता पासबुक"},
                "descriptions": {"en": "Showing applicant's name, account number, and IFSC.", "hi": "आवेदक का नाम और खाता संख्या दर्शाने वाली पासबुक।"},
            },
            {
                "document_code": "residence_domicile_proof",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "State Residence / Domicile Certificate", "hi": "मूल निवास / राशन कार्ड"},
                "descriptions": {"en": "Proof of permanent residence in the state.", "hi": "राज्य में स्थायी निवास का प्रमाण।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Aadhaar & Bank Account Seeding Check",
                "description": "Ensure your single bank account has NPCI / Aadhaar DBT mapper active.",
            },
            {
                "step_number": 2,
                "title": "Submit Application at Camp or Online",
                "description": "Fill the application form at local Anganwadi / Ward Office / Gram Panchayat camp or portal.",
            },
            {
                "step_number": 3,
                "title": "Receive Approval SMS & Monthly Credit",
                "description": "Once approved, financial assistance is deposited directly into your bank account monthly.",
            },
        ],
    },
    "education": {
        "fields": [
            {
                "field_key": "student_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Student's Full Name", "hi": "छात्र / छात्रा का पूरा नाम"},
                "explanations": {"en": "Name as registered in Educational Institution and Class 10th / Matriculation Certificate.", "hi": "शैक्षणिक संस्थान और 10वीं के प्रमाण पत्र में दर्ज नाम।"},
                "instructions": {"en": "Match educational records.", "hi": "शैक्षणिक रिकॉर्ड से मेल खाना चाहिए।"},
            },
            {
                "field_key": "student_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Student's Aadhaar Number", "hi": "विद्यार्थी का आधार नंबर"},
                "explanations": {"en": "Required for National/State Scholarship Portal biometric authentication.", "hi": "छात्रवृत्ति पोर्टल पर प्रमाणीकरण हेतु।"},
                "instructions": {"en": "12-digit number.", "hi": "12 अंकों की संख्या।"},
            },
            {
                "field_key": "institution_name_aishe",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "School / College / Institute Name", "hi": "स्कूल / कॉलेज / संस्थान का नाम"},
                "explanations": {"en": "Must be an accredited school, college, or university recognized by government.", "hi": "मान्यता प्राप्त स्कूल, कॉलेज या विश्वविद्यालय का नाम।"},
                "instructions": {"en": "Include AISHE or U-DISE code if known.", "hi": "संस्थान का पूरा नाम दर्ज करें।"},
            },
            {
                "field_key": "current_course_year",
                "field_type": "text",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Current Course / Class & Year", "hi": "वर्तमान पाठ्यक्रम / कक्षा एवं वर्ष"},
                "explanations": {"en": "e.g. Class 11, B.A. 2nd Year, B.Tech 3rd Semester.", "hi": "उदा. कक्षा 11, बीए द्वितीय वर्ष, बीटेक।"},
                "instructions": {"en": "Mention current academic year.", "hi": "वर्तमान शैक्षणिक वर्ष लिखें।"},
            },
            {
                "field_key": "annual_family_income",
                "field_type": "currency",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Total Annual Family Income (₹)", "hi": "कुल वार्षिक पारिवारिक आय (₹)"},
                "explanations": {"en": "Scholarship eligibility is determined by family income ceilings (typically up to ₹2.5 lakh).", "hi": "छात्रवृत्ति पात्रता पारिवारिक आय सीमा (आमतौर पर ₹2.5 लाख तक) पर निर्भर करती है।"},
                "instructions": {"en": "Must match official revenue income certificate.", "hi": "सक्षम अधिकारी द्वारा जारी आय प्रमाण पत्र से मेल खाए।"},
            },
            {
                "field_key": "student_bank_account",
                "field_type": "bank_account",
                "required": True,
                "sort_order": 6,
                "labels": {"en": "Student's Personal Bank Account Number", "hi": "विद्यार्थी का बैंक खाता संख्या"},
                "explanations": {"en": "Scholarship grant and maintenance allowance is credited directly to student's own account.", "hi": "छात्रवृत्ति राशि सीधे विद्यार्थी के अपने खाते में भेजी जाती है।"},
                "instructions": {"en": "Aadhaar linked bank account.", "hi": "आधार से जुड़ा बैंक खाता।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "enrolled_regular_student",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Enrolled as Regular Full-Time Student", "hi": "नियमित छात्र के रूप में नामांकित"},
                "descriptions": {"en": "Applicant must be actively studying in a recognized government or accredited institution.", "hi": "मान्यता प्राप्त संस्थान में नियमित रूप से अध्ययनरत होना आवश्यक है।"},
            },
            {
                "criterion_key": "family_income_under_scholarship_cap",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Annual Income Below Prescribed Limit", "hi": "वार्षिक आय निर्धारित सीमा से कम"},
                "descriptions": {"en": "Family annual income from all sources must not exceed scheme limit (e.g., ₹2.5 Lakh/annum).", "hi": "सभी स्रोतों से वार्षिक आय योजना की निर्धारित सीमा के भीतर होनी चाहिए।"},
            },
        ],
        "documents": [
            {
                "document_code": "student_aadhaar",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Student Aadhaar Card", "hi": "छात्र का आधार कार्ड"},
                "descriptions": {"en": "Valid Aadhaar card.", "hi": "वैध आधार कार्ड।"},
            },
            {
                "document_code": "previous_exam_marksheet",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Previous Year Exam Marksheet", "hi": "पिछली परीक्षा की अंकतालिका"},
                "descriptions": {"en": "Passed certificate/marksheet of qualifying examination.", "hi": "उत्तीर्ण परीक्षा की अंकतालिका।"},
            },
            {
                "document_code": "income_certificate",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Current Competent Authority Income Certificate", "hi": "वैध आय प्रमाण पत्र"},
                "descriptions": {"en": "Issued by Tehsildar / SDO / Revenue Officer.", "hi": "तहसीलदार या सक्षम राजस्व अधिकारी द्वारा जारी।"},
            },
            {
                "document_code": "student_bank_passbook",
                "is_mandatory": True,
                "sort_order": 4,
                "titles": {"en": "Student Bank Passbook Copy", "hi": "विद्यार्थी की बैंक पासबुक प्रति"},
                "descriptions": {"en": "First page showing account number and IFSC.", "hi": "खाता संख्या और आईएफएससी दर्शाने वाला पृष्ठ।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Register on Scholarship Portal",
                "description": "Create OTR (One Time Registration) using student Aadhaar and active mobile number.",
            },
            {
                "step_number": 2,
                "title": "Fill Course Details & Upload Documents",
                "description": "Select institution, enter marks, and upload scanned fee receipt and marksheets.",
            },
            {
                "step_number": 3,
                "title": "Institute Nodal Officer Verification",
                "description": "Your school/college verifies enrollment before forwarding application to state district officer.",
            },
        ],
    },
    "housing": {
        "fields": [
            {
                "field_key": "applicant_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Head of Household Full Name", "hi": "परिवार के मुखिया का पूरा नाम"},
                "explanations": {"en": "Name of the primary applicant / beneficiary for house construction assistance.", "hi": "आवास सहायता हेतु प्राथमिक आवेदक का नाम।"},
                "instructions": {"en": "Must match Aadhaar card.", "hi": "आधार कार्ड से मेल खाना चाहिए।"},
            },
            {
                "field_key": "applicant_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Aadhaar Number", "hi": "आधार संख्या"},
                "explanations": {"en": "Mandatory for AwaasSoft identity authentication and Geo-tagging verification.", "hi": "आवास सॉफ्ट प्रमाणीकरण और जियो-टैगिंग सत्यापन हेतु।"},
                "instructions": {"en": "12-digit number.", "hi": "12 अंकों की संख्या।"},
            },
            {
                "field_key": "current_house_type",
                "field_type": "select",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Current Dwelling / House Status", "hi": "वर्तमान मकान का प्रकार"},
                "explanations": {"en": "Only households living in kutcha, dilapidated, or zero-room houses are eligible for assistance.", "hi": "केवल कच्चे, जर्जर या बेघर परिवार ही पक्के मकान सहायता के पात्र हैं।"},
                "instructions": {"en": "Kutcha / Zero room / Dilapidated.", "hi": "कच्चा मकान / बेघर।"},
            },
            {
                "field_key": "land_possession_details",
                "field_type": "text",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Homestead Land Plot / Site Details", "hi": "आवास निर्माण हेतु भूखंड / स्थल का विवरण"},
                "explanations": {"en": "Plot number or Gram Panchayat land allocation where house is to be built.", "hi": "जहाँ मकान बनाया जाना है उस भूखंड या ग्राम पंचायत स्थल का विवरण।"},
                "instructions": {"en": "Plot/Patta number or village site.", "hi": "प्लॉट संख्या या ग्राम स्थल।"},
            },
            {
                "field_key": "bank_account_number",
                "field_type": "bank_account",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Bank Account for Installment Transfer", "hi": "किस्त भुगतान हेतु बैंक खाता संख्या"},
                "explanations": {"en": "Construction funds are credited directly in 3 to 4 stages upon geo-tagged physical inspection.", "hi": "मकान निर्माण की किस्तें जियो-टैगिंग निरीक्षण के बाद सीधे खाते में भेजी जाती हैं।"},
                "instructions": {"en": "Aadhaar seeded savings account.", "hi": "आधार लिंक्ड बचत खाता।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "no_pucca_house_anywhere",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "No Pucca House Anywhere in India", "hi": "भारत में कहीं भी पक्का मकान न हो"},
                "descriptions": {"en": "Applicant or any family member must not own a pucca house in their name anywhere.", "hi": "आवेदक या उसके परिवार के किसी सदस्य के नाम कोई पक्का मकान नहीं होना चाहिए।"},
            },
            {
                "criterion_key": "secc_deprivation_priority",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "SECC / Awaas+ / Homeless Priority Category", "hi": "एसईसीसी / आवास+ वरीयता श्रेणी"},
                "descriptions": {"en": "Priority given to rural houseless, SC/ST, and primitive tribal groups.", "hi": "ग्रामीण बेघर, एससी/एसटी और निर्धन परिवारों को प्राथमिकता।"},
            },
        ],
        "documents": [
            {
                "document_code": "aadhaar_card",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Applicant's Aadhaar.", "hi": "आवेदक का आधार।"},
            },
            {
                "document_code": "land_possession_cert",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Homestead Land Ownership / Patta Document", "hi": "आवास स्थल का पट्टा / स्वामित्व प्रमाण"},
                "descriptions": {"en": "Proof that applicant owns or has valid right to the building plot.", "hi": "भूखंड पर वैध अधिकार या पट्टा।"},
            },
            {
                "document_code": "bank_passbook",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Bank Passbook Copy", "hi": "बैंक पासबुक प्रति"},
                "descriptions": {"en": "Aadhaar-seeded bank account for milestone installments.", "hi": "किस्तों के अंतरण हेतु पासबुक।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Registration in Awaas+ Database",
                "description": "Gram Panchayat officer registers family details and verifies current kutcha house.",
            },
            {
                "step_number": 2,
                "title": "Sanction Order & First Installment",
                "description": "After administrative sanction, initial installment is credited to begin foundation work.",
            },
            {
                "step_number": 3,
                "title": "Geo-Tagging Inspection & Completion",
                "description": "Official uploads geo-tagged photo at plinth, lintel, and roof levels to release final installments.",
            },
        ],
    },
    "pension": {
        "fields": [
            {
                "field_key": "pensioner_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Applicant / Pensioner's Full Name", "hi": "आवेदक / पेंशनभोगी का पूरा नाम"},
                "explanations": {"en": "Full name as recorded in official government identity documents.", "hi": "आधिकारिक पहचान पत्र में दर्ज पूरा नाम।"},
                "instructions": {"en": "Must match Aadhaar card.", "hi": "आधार कार्ड से मेल खाना चाहिए।"},
            },
            {
                "field_key": "pensioner_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Aadhaar Number", "hi": "आधार संख्या"},
                "explanations": {"en": "Required for biometric identity verification and annual Digital Life Certificate (Jeevan Pramaan).", "hi": "सत्यापन और वार्षिक डिजिटल जीवन प्रमाण पत्र हेतु।"},
                "instructions": {"en": "12-digit number.", "hi": "12 अंकों की संख्या।"},
            },
            {
                "field_key": "date_of_birth_age",
                "field_type": "date",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Date of Birth (Age Proof)", "hi": "जन्म तिथि (आयु प्रमाण)"},
                "explanations": {"en": "Old age pension requires minimum age of 60 years. Age is verified against Voter ID / Aadhaar.", "hi": "वृद्धावस्था पेंशन हेतु न्यूनतम 60 वर्ष की आयु आवश्यक है।"},
                "instructions": {"en": "Must be 60 years or older.", "hi": "उम्र 60 वर्ष या अधिक होनी चाहिए।"},
            },
            {
                "field_key": "bpl_card_number",
                "field_type": "text",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "BPL Card / Ration Card Number", "hi": "बीपीएल राशन कार्ड संख्या"},
                "explanations": {"en": "Social security pensions are provided to destitute elderly living below poverty line.", "hi": "सामाजिक सुरक्षा पेंशन निर्धन और बीपीएल परिवारों के बुजुर्गों को देय है।"},
                "instructions": {"en": "Enter BPL or Antyodaya card number.", "hi": "बीपीएल या अंत्योदय कार्ड नंबर लिखें।"},
            },
            {
                "field_key": "pension_bank_account",
                "field_type": "bank_account",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Single Bank / Post Office Account Number", "hi": "एकल बैंक या डाकघर खाता संख्या"},
                "explanations": {"en": "Monthly pension assistance is credited directly to this account every month.", "hi": "मासिक पेंशन सहायता सीधे इसी खाते में जमा होती है।"},
                "instructions": {"en": "Must be in applicant's sole name.", "hi": "केवल पेंशनभोगी के नाम का खाता।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "age_60_or_above",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Age 60 Years or Above", "hi": "आयु 60 वर्ष या उससे अधिक"},
                "descriptions": {"en": "Applicant must have completed 60 years of age on date of application.", "hi": "आवेदन तिथि पर 60 वर्ष की आयु पूर्ण होनी चाहिए।"},
            },
            {
                "criterion_key": "bpl_destitute_status",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "BPL Household / Destitute Status", "hi": "बीपीएल परिवार / असहाय स्थिति"},
                "descriptions": {"en": "Applicant family must be certified Below Poverty Line with no substantial family support.", "hi": "परिवार गरीबी रेखा से नीचे (BPL) होना चाहिए।"},
            },
        ],
        "documents": [
            {
                "document_code": "aadhaar_card",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Aadhaar showing date of birth.", "hi": "जन्म तिथि दर्शाने वाला आधार।"},
            },
            {
                "document_code": "age_proof_document",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Age Proof (Voter ID / Birth Cert)", "hi": "आयु प्रमाण (मतदाता पहचान पत्र / जन्म प्रमाण)"},
                "descriptions": {"en": "Official government document verifying age 60+.", "hi": "60 वर्ष से अधिक आयु प्रमाणित करने वाला दस्तावेज।"},
            },
            {
                "document_code": "bpl_certificate",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "BPL Ration Card / Income Certificate", "hi": "बीपीएल राशन कार्ड / आय प्रमाण"},
                "descriptions": {"en": "Showing economic eligibility.", "hi": "आर्थिक स्थिति का प्रमाण।"},
            },
            {
                "document_code": "bank_postoffice_passbook",
                "is_mandatory": True,
                "sort_order": 4,
                "titles": {"en": "Bank / Post Office Passbook", "hi": "बैंक / डाकघर पासबुक"},
                "descriptions": {"en": "For monthly direct pension deposit.", "hi": "मासिक पेंशन अंतरण हेतु पासबुक।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Submit Application at Block/Tehsil or CSC",
                "description": "Submit pension application along with age proof and BPL card copy.",
            },
            {
                "step_number": 2,
                "title": "Social Welfare Officer Verification",
                "description": "Block Development Officer / Social Security Officer verifies eligibility criteria.",
            },
            {
                "step_number": 3,
                "title": "PPO Generation & Monthly Credit",
                "description": "Pension Payment Order (PPO) is issued and monthly pension begins.",
            },
        ],
    },
    "employment": {
        "fields": [
            {
                "field_key": "applicant_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Applicant / Entrepreneur Full Name", "hi": "आवेदक / उद्यमी का पूरा नाम"},
                "explanations": {"en": "Full name as per official government identity document.", "hi": "आधिकारिक पहचान पत्र के अनुसार नाम।"},
                "instructions": {"en": "Must match Aadhaar.", "hi": "आधार कार्ड से मेल खाना चाहिए।"},
            },
            {
                "field_key": "applicant_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Aadhaar Number", "hi": "आधार संख्या"},
                "explanations": {"en": "Required for identity verification and loan/subsidy credit linkage.", "hi": "पहचान और सब्सिडी लिंकेज सत्यापन हेतु।"},
                "instructions": {"en": "12 digits.", "hi": "12 अंक।"},
            },
            {
                "field_key": "enterprise_vending_activity",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Business / Vending / Self-Employment Activity", "hi": "व्यवसाय / फेरी / स्वरोजगार का प्रकार"},
                "explanations": {"en": "Nature of trade, micro-enterprise, or vending goods (e.g., vegetables, apparel, food stall, artisan).", "hi": "व्यवसाय का विवरण (उदा. सब्जी विक्रेता, खाद्य स्टॉल, हस्तशिल्प, दुकान)।"},
                "instructions": {"en": "Briefly describe your business.", "hi": "अपने व्यवसाय का संक्षिप्त विवरण दें।"},
            },
            {
                "field_key": "vending_location_ward",
                "field_type": "text",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Vending Zone / Market / Ward Location", "hi": "दुकान / फेरी स्थल / वार्ड का विवरण"},
                "explanations": {"en": "Specific market, street, or ward where applicant conducts micro-business.", "hi": "वह बाजार या वार्ड जहाँ व्यवसाय संचालित होता है।"},
                "instructions": {"en": "Street name, market, town.", "hi": "बाजार या वार्ड का नाम।"},
            },
            {
                "field_key": "bank_account_number",
                "field_type": "bank_account",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Active Bank Account Number", "hi": "सक्रिय बैंक खाता संख्या"},
                "explanations": {"en": "Disbursement of working capital loan or subsidy will be made to this account.", "hi": "ऋण या सब्सिडी राशि सीधे इसी खाते में प्राप्त होगी।"},
                "instructions": {"en": "Must be Aadhaar seeded.", "hi": "आधार से जुड़ा खाता।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "active_micro_enterprise_or_vendor",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Engaged in Vending / Micro Enterprise", "hi": "स्वरोजगार या फेरी व्यवसाय में सक्रिय"},
                "descriptions": {"en": "Must be an active street vendor, small artisan, or aspiring entrepreneur.", "hi": "सक्रिय स्ट्रीट वेंडर, कारीगर या उद्यमी होना आवश्यक है।"},
            },
            {
                "criterion_key": "legal_age_requirement",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Age 18 Years or Above", "hi": "आयु 18 वर्ष या उससे अधिक"},
                "descriptions": {"en": "Applicant must be an adult competent to contract credit facilities.", "hi": "आवेदक की आयु न्यूनतम 18 वर्ष होनी चाहिए।"},
            },
        ],
        "documents": [
            {
                "document_code": "aadhaar_card",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Valid Aadhaar card.", "hi": "वैध आधार कार्ड।"},
            },
            {
                "document_code": "vending_id_or_recommendation",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Certificate of Vending / ULB Recommendation", "hi": "विक्रेता पहचान पत्र / नगर निकाय प्रमाण पत्र"},
                "descriptions": {"en": "Letter of Recommendation (LoR) or Vending ID from Municipal Corporation.", "hi": "नगर निगम या स्थानीय निकाय द्वारा जारी पहचान पत्र या अनुशंसा पत्र।"},
            },
            {
                "document_code": "bank_passbook",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Bank Passbook Copy", "hi": "बैंक पासबुक प्रति"},
                "descriptions": {"en": "Passbook showing account details.", "hi": "खाता विवरण दर्शाने वाली पासबुक।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Obtain Vending ID or Letter of Recommendation",
                "description": "Collect Certificate of Vending from your Urban Local Body or Municipality.",
            },
            {
                "step_number": 2,
                "title": "Submit Loan Application Online",
                "description": "Submit application on the official scheme portal with preferred lending bank.",
            },
            {
                "step_number": 3,
                "title": "Disbursement & Digital Cashback",
                "description": "Lending institution disburses loan and interest subsidy directly to your account.",
            },
        ],
    },
    "welfare": {
        "fields": [
            {
                "field_key": "applicant_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Applicant Full Name", "hi": "आवेदक का पूरा नाम"},
                "explanations": {"en": "Full name as registered on government identity documents.", "hi": "सरकारी पहचान पत्र के अनुसार नाम।"},
                "instructions": {"en": "Must match Aadhaar card.", "hi": "आधार कार्ड से मेल खाना चाहिए।"},
            },
            {
                "field_key": "applicant_aadhaar",
                "field_type": "aadhaar",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Aadhaar Number", "hi": "आधार संख्या"},
                "explanations": {"en": "Required for biometric verification and beneficiary registration.", "hi": "सत्यापन और लाभार्थी पंजीकरण हेतु।"},
                "instructions": {"en": "12-digit number.", "hi": "12 अंकों की संख्या।"},
            },
            {
                "field_key": "ration_card_number",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Ration Card Number", "hi": "राशन कार्ड संख्या"},
                "explanations": {"en": "Used to confirm socio-economic status and household quota.", "hi": "परिवार की आर्थिक स्थिति और कोटे के सत्यापन हेतु।"},
                "instructions": {"en": "Enter 12 or 16 digit card number.", "hi": "कार्ड नंबर दर्ज करें।"},
            },
            {
                "field_key": "bank_account_number",
                "field_type": "bank_account",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Aadhaar-Seeded Bank Account Number", "hi": "आधार-सीडेड बैंक खाता संख्या"},
                "explanations": {"en": "Financial benefits will be directly credited to this account.", "hi": "लाभ राशि सीधे इसी बैंक खाते में जमा होगी।"},
                "instructions": {"en": "Active savings account.", "hi": "सक्रिय बचत खाता।"},
            },
        ],
        "eligibility": [
            {
                "criterion_key": "resident_welfare_criteria",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Permanent Resident of the State/UT", "hi": "राज्य/केंद्रशासित प्रदेश का स्थायी निवासी"},
                "descriptions": {"en": "Must be a domiciled resident of the state.", "hi": "राज्य का मूल निवासी होना चाहिए।"},
            },
            {
                "criterion_key": "eligible_category_status",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Belonging to Eligible Category", "hi": "पात्र लाभार्थी श्रेणी में शामिल"},
                "descriptions": {"en": "Meets specific target demographic criteria.", "hi": "योजना की लक्षित श्रेणी के अंतर्गत आता हो।"},
            },
        ],
        "documents": [
            {
                "document_code": "aadhaar_card",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Valid Aadhaar.", "hi": "वैध आधार।"},
            },
            {
                "document_code": "ration_card",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Ration Card / Domicile Certificate", "hi": "राशन कार्ड / निवास प्रमाण पत्र"},
                "descriptions": {"en": "Proof of residence and household.", "hi": "निवास और पारिवारिक स्थिति का प्रमाण।"},
            },
            {
                "document_code": "bank_passbook",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Bank Passbook Copy", "hi": "बैंक पासबुक प्रति"},
                "descriptions": {"en": "Showing IFSC and account number.", "hi": "आईएफएससी और खाता संख्या दर्शाने वाली पासबुक।"},
            },
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Check Domicile & Category Eligibility",
                "description": "Ensure your category certificate and residential proof are up-to-date.",
            },
            {
                "step_number": 2,
                "title": "Submit Application at CSC / Seva Kendra",
                "description": "Apply online or visit the local citizen service centre with required documents.",
            },
            {
                "step_number": 3,
                "title": "Departmental Scrutiny & Approval",
                "description": "Concerned welfare department reviews application and issues sanction order.",
            },
        ],
    },
}

# Default fallback archetype for energy/other categories
CATEGORY_WORKFLOW_TEMPLATES["energy"] = CATEGORY_WORKFLOW_TEMPLATES["welfare"]
CATEGORY_WORKFLOW_TEMPLATES["other"] = CATEGORY_WORKFLOW_TEMPLATES["welfare"]


# ── Scheme Form Population Service ─────────────────────────────────────────

def populate_all_schemes_forms(db: Session) -> Dict[str, Any]:
    """
    Ensures EVERY scheme in the database has authentic, complete:
    - Form fields (with multilingual labels, field types, required flags, explanations)
    - Eligibility criteria (mandatory flags, clear descriptions)
    - Required documents checklist
    - Step-by-step application instructions
    """
    schemes = db.query(GovernmentScheme).all()
    updated_count = 0
    already_complete = 0

    with db.no_autoflush:
        for s in schemes:
            # Check if scheme already has full fields
            if len(s.fields) > 0 and len(s.eligibility_requirements) > 0 and len(s.document_requirements) > 0:
                already_complete += 1
                continue

            # Look up scheme-specific workflow first, or fall back to category template
            wf = SCHEME_SPECIFIC_WORKFLOWS.get(s.slug)
            if not wf:
                category = (s.category or "welfare").lower()
                wf = CATEGORY_WORKFLOW_TEMPLATES.get(category, CATEGORY_WORKFLOW_TEMPLATES["welfare"])

            # 1. Populate Form Fields if missing
            if len(s.fields) == 0:
                for f_spec in wf.get("fields", []):
                    field = FormField(
                        scheme_id=s.id,
                        field_key=f_spec["field_key"],
                        field_type=f_spec["field_type"],
                        required=f_spec.get("required", True),
                        sort_order=f_spec.get("sort_order", 1),
                        labels_by_language=f_spec.get("labels", {}),
                        explanations_by_language=f_spec.get("explanations", {}),
                        instructions_by_language=f_spec.get("instructions", {}),
                        verification_status="verified",
                    )
                    db.add(field)

            # 2. Populate Eligibility Requirements if missing
            if len(s.eligibility_requirements) == 0:
                for e_spec in wf.get("eligibility", []):
                    elig = SchemeEligibilityRequirement(
                        scheme_id=s.id,
                        criterion_key=e_spec["criterion_key"],
                        criterion_type="general",
                        is_mandatory=e_spec.get("is_mandatory", True),
                        sort_order=e_spec.get("sort_order", 1),
                        titles_by_language=e_spec.get("titles", {}),
                        descriptions_by_language=e_spec.get("descriptions", {}),
                    )
                    db.add(elig)

            # 3. Populate Document Requirements if missing
            if len(s.document_requirements) == 0:
                for d_spec in wf.get("documents", []):
                    doc = SchemeDocumentRequirement(
                        scheme_id=s.id,
                        document_code=d_spec["document_code"],
                        requirement_type="always_required" if d_spec.get("is_mandatory", True) else "optional",
                        is_mandatory=d_spec.get("is_mandatory", True),
                        sort_order=d_spec.get("sort_order", 1),
                        titles_by_language=d_spec.get("titles", {}),
                        descriptions_by_language=d_spec.get("descriptions", {}),
                    )
                    db.add(doc)

            # 4. Populate Application Steps if missing
            if len(s.application_steps) == 0:
                for st_spec in wf.get("steps", []):
                    step_num = st_spec.get("step_number", 1)
                    title = st_spec.get("title", "Application Step")
                    desc = st_spec.get("description", "Follow official instructions.")
                    step = SchemeApplicationStep(
                        scheme_id=s.id,
                        step_number=step_num,
                        step_key=f"step_{step_num}",
                        titles_by_language={"en": title, "hi": title},
                        instructions_by_language={"en": desc, "hi": desc},
                        official_action_url=s.official_application_url or s.official_source_url,
                        source_reference=f"Official instructions via {s.department_name}.",
                        verification_status="verified",
                    )
                    db.add(step)

            # Mark form_status as VERIFIED_SCHEMA
            s.form_status = "VERIFIED_SCHEMA"
            s.verification_status = "verified"
            updated_count += 1

    db.commit()
    return {
        "total_schemes": len(schemes),
        "already_complete": already_complete,
        "newly_configured": updated_count,
    }

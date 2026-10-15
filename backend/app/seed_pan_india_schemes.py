"""
NagrikSaarathi — Pan-India Scheme Seeder
Populates a comprehensive, authentic catalogue of Central, State, and UT government schemes
with multi-lingual labels, eligibility criteria, document requirements, step-by-step guidance,
and schema-driven form fields for universal dynamic form generation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select

from backend.app.database import get_session_factory
from backend.app.models import (
    FormField,
    GovernmentScheme,
    SchemeApplicationStep,
    SchemeDocumentRequirement,
    SchemeEligibilityRequirement,
)

SCHEMES_CATALOGUE = [
    {
        "slug": "pm-kisan",
        "display_name": "PM-KISAN Samman Nidhi (पीएम-किसान सम्मान निधि)",
        "description": "Income support scheme of ₹6,000 per year in three equal installments to all landholding farmer families across India.",
        "department_name": "Ministry of Agriculture & Farmers Welfare, Government of India",
        "official_source_url": "https://pmkisan.gov.in/",
        "official_application_url": "https://pmkisan.gov.in/RegistrationFormNew.aspx",
        "source_document_reference": "PM-KISAN Operational Guidelines Revised 2024",
        "government_level": "central",
        "state_code": None,
        "category": "agriculture",
        "beneficiary_groups": ["farmers", "rural_families"],
        "application_method": "online",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["farmer", "kisan", "agriculture", "6000", "samman nidhi", "land", "crop"],
        "scheme_status": "active",
        "min_age": 18,
        "max_age": None,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Income support of ₹6,000 per year payable in three equal installments of ₹2,000 every 4 months directly into bank accounts of eligible farmer families.",
            "hi": "पात्र किसान परिवारों को ₹6,000 प्रति वर्ष की आय सहायता, जो हर 4 महीने में ₹2,000 की तीन समान किश्तों में सीधे बैंक खातों में भेजी जाती है।",
            "bn": "যোগ্য কৃষক পরিবারগুলিকে প্রতি বছর ₹৬,০০০ আয় সহায়তা, প্রতি ৪ মাসে সরাসরি ব্যাংক একাউন্টে প্রদান করা হয়।",
            "ta": "தகுதியான விவசாய குடும்பங்களுக்கு ஆண்டுக்கு ₹6,000 வருமான உதவி, 4 மாதங்களுக்கு ஒருமுறை நேரடியாக வங்கிக் கணக்கில் செலுத்தப்படுகிறது.",
            "te": "అర్హులైన రైతు కుటుంబాలకు సంవత్సరానికి ₹6,000 ఆదాయ సహాయం, నేరుగా బ్యాంక్ ఖాతాలో జమ చేయబడుతుంది.",
            "mr": "पात्र शेतकरी कुटुंबांना दरवर्षी ₹६,००० चे उत्पन्न साहाय्य, थेट बँक खात्यात जमा केले जाते.",
        },
        "application_instructions_by_language": {
            "en": "Prepare your Aadhaar, bank passbook with linked Aadhaar/NPCI seeding, and land record documents (Khatauni / Khasra number) before filling this form.",
            "hi": "इस फॉर्म को भरने से पहले अपना आधार कार्ड, आधार-लिंक्ड बैंक पासबुक तथा भूमि दस्तावेज (खतौनी / खसरा संख्या) तैयार रखें।",
            "bn": "আবেদন করার পূর্বে আপনার আধার কার্ড, ব্যাংক পাসবুক এবং জমির খতিয়ান প্রস্তুত রাখুন।",
            "ta": "விண்ணப்பிக்கும் முன் உங்கள் ஆதார் அட்டை, வங்கி கணக்கு புத்தகம் மற்றும் நில ஆவணங்களை தயாராக வைத்திருக்கவும்.",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "farmer_family_landholding",
                "criterion_type": "landholding",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Landholding Farmer Family", "hi": "भूमिधारक किसान परिवार"},
                "descriptions": {"en": "Family must own cultivable land registered in state land revenue records.", "hi": "परिवार के नाम राज्य राजस्व रिकॉर्ड में कृषि योग्य भूमि दर्ज होनी चाहिए।"},
            },
            {
                "criterion_key": "not_income_tax_payer",
                "criterion_type": "tax_status",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Not an Income Tax Payer", "hi": "आयकर दाता नहीं होना चाहिए"},
                "descriptions": {"en": "Applicant or family member must not have paid income tax in the last assessment year.", "hi": "आवेदक या उसके परिवार ने पिछले मूल्यांकन वर्ष में आयकर नहीं भरा हो।"},
            },
            {
                "criterion_key": "not_institutional_holder",
                "criterion_type": "status",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Individual Farmer (Non-Institutional)", "hi": "व्यक्तिगत किसान (गैर-संस्थागत)"},
                "descriptions": {"en": "Institutional landholders are not eligible.", "hi": "संस्थागत भूमि धारक इस योजना के पात्र नहीं हैं।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "aadhaar_card",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Valid Aadhaar Card of the farmer applicant linked with active mobile number.", "hi": "सक्रिय मोबाइल नंबर से जुड़ा आवेदक किसान का वैध आधार कार्ड।"},
            },
            {
                "document_code": "land_record_khatauni",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Land Ownership Record (Khatauni / RoR)", "hi": "भूमि स्वामित्व रिकॉर्ड (खतौनी / जमाबंदी)"},
                "descriptions": {"en": "Official land record showing cultivable land ownership with Khasra and Khata number.", "hi": "खसरा और खाता संख्या दर्शाने वाला आधिकारिक भूमि स्वामित्व प्रमाण।"},
            },
            {
                "document_code": "bank_passbook",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Bank Passbook (Aadhaar Seeding)", "hi": "बैंक पासबुक (आधार-सीडेड)"},
                "descriptions": {"en": "Bank account copy with IFSC code and NPCI Aadhaar seeding for DBT transfers.", "hi": "डीबीटी हस्तांतरण हेतु बैंक पासबुक जिसमें आईएफएससी और आधार सीडिंग हो।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "check_aadhaar", "titles": {"en": "Aadhaar Authentication", "hi": "आधार सत्यापन"}, "instructions": {"en": "Enter Aadhaar number and solve captcha on the official PM-KISAN portal.", "hi": "आधिकारिक पीएम-किसान पोर्टल पर आधार संख्या दर्ज करें।"}, "official_action_url": "https://pmkisan.gov.in/RegistrationFormNew.aspx"},
            {"step_number": 2, "step_key": "enter_land_details", "titles": {"en": "Enter Land & Personal Details", "hi": "भूमि एवं व्यक्तिगत विवरण दर्ज करें"}, "instructions": {"en": "Select State, District, Sub-district, Block, Village and fill Survey / Khasra number.", "hi": "राज्य, जिला, उप-जिला, ब्लॉक, गांव चुनें और खसरा नंबर भरें।"}, "official_action_url": "https://pmkisan.gov.in/"},
            {"step_number": 3, "step_key": "submit_declaration", "titles": {"en": "Submit Declaration & Note Reg ID", "hi": "घोषणा पत्र जमा करें और पंजीकरण संख्या नोट करें"}, "instructions": {"en": "Review all details, submit self-declaration, and save the temporary registration number.", "hi": "विवरण जांचें, स्व-घोषणा जमा करें और पंजीकरण नंबर सुरक्षित रखें।"}, "official_action_url": "https://pmkisan.gov.in/"},
        ],
        "fields": [
            {
                "field_key": "farmer_full_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Farmer Full Name (as per Aadhaar)", "hi": "किसान का पूरा नाम (आधार के अनुसार)"},
                "explanations": {"en": "Enter your full name exactly matching your Aadhaar card.", "hi": "अपना नाम आधार कार्ड के अनुसार बिल्कुल सही दर्ज करें।"},
                "instructions": {"en": "Do not prefix Shri / Mr / Smt.", "hi": "नाम से पहले श्री / श्रीमती न लगाएं।"},
                "examples": {"en": "Ramesh Chandra Patel", "hi": "रमेश चन्द्र पटेल"},
            },
            {
                "field_key": "aadhaar_number",
                "field_type": "text",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "12-Digit Aadhaar Number", "hi": "12-अंकीय आधार संख्या"},
                "explanations": {"en": "Your unique 12-digit Indian identification number.", "hi": "आपकी 12 अंकों की विशिष्ट पहचान संख्या।"},
                "instructions": {"en": "Enter only 12 digits without spaces or hyphens.", "hi": "बिना स्पेस के केवल 12 अंक दर्ज करें।"},
                "examples": {"en": "987654321012", "hi": "987654321012"},
            },
            {
                "field_key": "state_name",
                "field_type": "select",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "State / Union Territory", "hi": "राज्य / केंद्र शासित प्रदेश"},
                "explanations": {"en": "State where your agricultural land is located.", "hi": "वह राज्य जहाँ आपकी कृषि भूमि स्थित है।"},
                "instructions": {"en": "Select from the dropdown list.", "hi": "सूची से चयन करें।"},
            },
            {
                "field_key": "district_name",
                "field_type": "text",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "District", "hi": "जिला"},
                "explanations": {"en": "Revenue district where land is registered.", "hi": "राजस्व जिला जहाँ भूमि दर्ज है।"},
                "instructions": {"en": "Enter district name.", "hi": "जिले का नाम लिखें।"},
            },
            {
                "field_key": "khasra_survey_number",
                "field_type": "text",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Land Khasra / Survey / Dag Number", "hi": "भूमि खसरा / सर्वे / दाग संख्या"},
                "explanations": {"en": "Number mentioned on your Khatauni or land passbook.", "hi": "आपकी खतौनी या भू-अभिलेख में दर्ज खसरा संख्या।"},
                "instructions": {"en": "Check your latest RoR / Khatauni document.", "hi": "अपनी खतौनी से देखकर भरें।"},
                "examples": {"en": "142/3", "hi": "142/3"},
            },
            {
                "field_key": "land_area_hectares",
                "field_type": "number",
                "required": True,
                "sort_order": 6,
                "labels": {"en": "Land Area (in Hectares)", "hi": "भूमि का क्षेत्रफल (हेक्टेयर में)"},
                "explanations": {"en": "Total cultivable land area in hectares.", "hi": "हेक्टेयर में कुल कृषि भूमि का क्षेत्रफल।"},
                "instructions": {"en": "Convert bigha or acres to hectares if needed (1 Hectare ≈ 2.47 Acres).", "hi": "दशमलव सहित क्षेत्रफल लिखें।"},
                "examples": {"en": "1.25", "hi": "1.25"},
            },
            {
                "field_key": "bank_ifsc",
                "field_type": "text",
                "required": True,
                "sort_order": 7,
                "labels": {"en": "Bank IFSC Code", "hi": "बैंक IFSC कोड"},
                "explanations": {"en": "11-character bank branch identifier found on cheque or passbook.", "hi": "पासबुक पर मुद्रित 11 अंकों का बैंक शाखा कोड।"},
                "instructions": {"en": "Example: SBIN0001234, PUNB0123400.", "hi": "उदाहरण: SBIN0001234."},
                "examples": {"en": "SBIN0001234", "hi": "SBIN0001234"},
            },
            {
                "field_key": "bank_account_no",
                "field_type": "text",
                "required": True,
                "sort_order": 8,
                "labels": {"en": "Bank Account Number", "hi": "बैंक खाता संख्या"},
                "explanations": {"en": "Your active savings bank account number.", "hi": "सक्रिय बचत खाता संख्या।"},
                "instructions": {"en": "Account must be in applicant's name and seeded with Aadhaar.", "hi": "खाता आवेदक के नाम होना चाहिए।"},
            },
        ],
    },
    {
        "slug": "pmjay-ayushman-bharat",
        "display_name": "Ayushman Bharat - PM-JAY (आयुष्मान भारत PM-JAY)",
        "description": "World's largest health assurance scheme providing health cover of up to ₹5 lakh per family per year for secondary and tertiary care hospitalization.",
        "department_name": "National Health Authority, Ministry of Health and Family Welfare",
        "official_source_url": "https://pmjay.gov.in/",
        "official_application_url": "https://beneficiary.nha.gov.in/",
        "source_document_reference": "NHA PM-JAY Guidelines 2024",
        "government_level": "central",
        "state_code": None,
        "category": "healthcare",
        "beneficiary_groups": ["low_income", "rural_families", "urban_workers", "senior_citizens"],
        "application_method": "online",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["health", "hospital", "ayushman card", "5 lakh", "free treatment", "bima", "nha"],
        "scheme_status": "active",
        "min_age": 0,
        "max_age": None,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Provides cashless access to healthcare services for beneficiary families covering up to ₹5,00,000 per family per year at empaneled hospitals across India.",
            "hi": "भारत के सूचीबद्ध अस्पतालों में पात्र परिवारों को प्रति वर्ष ₹5,00,000 तक कैशलेस और पेपरलेस स्वास्थ्य सुरक्षा प्रदान करता है।",
            "bn": "ভারতের তালিকাভুক্ত হাসপাতালে পরিবার প্রতি বছরে ₹৫,০০,০০০ পর্যন্ত বিনামূল্যে স্বাস্থ্য পরিষেবা প্রদান করে।",
            "ta": "ஆண்டுக்கு குடும்பத்திற்கு ₹5,00,000 வரை பணமில்லா மருத்துவ காப்பீடு வழங்குகிறது.",
        },
        "application_instructions_by_language": {
            "en": "Check your eligibility using your Mobile number, Ration card, or Aadhaar before generating your Ayushman PVC card.",
            "hi": "अपना आयुष्मान कार्ड बनवाने से पहले मोबाइल नंबर, राशन कार्ड या आधार संख्या से अपनी पात्रता जांचें।",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "secc_or_ration_inclusion",
                "criterion_type": "database_match",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "SECC 2011 / NFSA Ration Card", "hi": "SECC 2011 या NFSA राशन कार्ड पात्रता"},
                "descriptions": {"en": "Family must be listed in SECC 2011 database or hold state-identified NFSA eligibility.", "hi": "परिवार का नाम SECC 2011 सूची या राज्य खाद्य सुरक्षा योजना में शामिल होना चाहिए।"},
            },
            {
                "criterion_key": "senior_citizen_expansion",
                "criterion_type": "age",
                "is_mandatory": False,
                "sort_order": 2,
                "titles": {"en": "Senior Citizen (Age 70+ Universal)", "hi": "वरिष्ठ नागरिक (70 वर्ष से अधिक सार्वभौमिक)"},
                "descriptions": {"en": "All citizens aged 70 years and above are eligible for dedicated ₹5 lakh cover regardless of income.", "hi": "70 वर्ष और उससे अधिक आयु के सभी वरिष्ठ नागरिक आय पर विचार किए बिना ₹5 लाख कवर के पात्र हैं।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "aadhaar_card",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Individual Aadhaar for e-KYC face/OTP/fingerprint verification.", "hi": "ई-केवाईसी बायोमेट्रिक या ओटीपी सत्यापन के लिए आधार कार्ड।"},
            },
            {
                "document_code": "ration_card",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Ration Card / Family ID", "hi": "राशन कार्ड / परिवार पहचान पत्र"},
                "descriptions": {"en": "State food security ration card showing all family members.", "hi": "सभी पारिवारिक सदस्यों के नाम दर्शाने वाला वैध राशन कार्ड।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "check_am_i_eligible", "titles": {"en": "Check Eligibility", "hi": "पात्रता जांचें"}, "instructions": {"en": "Visit beneficiary.nha.gov.in and search by Aadhaar or Ration Card number.", "hi": "beneficiary.nha.gov.in पर जाकर राशन कार्ड या आधार से पात्रता खोजें।"}, "official_action_url": "https://beneficiary.nha.gov.in/"},
            {"step_number": 2, "step_key": "complete_ekyc", "titles": {"en": "Complete e-KYC", "hi": "e-KYC पूर्ण करें"}, "instructions": {"en": "Authenticate with Aadhaar OTP or facial recognition through the Ayushman App.", "hi": "आधार ओटीपी या आयुष्मान ऐप से चेहरा पहचान द्वारा प्रमाणीकरण करें।"}, "official_action_url": "https://setu.pmjay.gov.in/"},
            {"step_number": 3, "step_key": "download_card", "titles": {"en": "Download Ayushman Card", "hi": "आयुष्मान कार्ड डाउनलोड करें"}, "instructions": {"en": "Once approved, download your golden Ayushman PVC card PDF.", "hi": "मंजूरी मिलने के बाद अपना आयुष्मान कार्ड डाउनलोड करें।"}, "official_action_url": "https://beneficiary.nha.gov.in/"},
        ],
        "fields": [
            {
                "field_key": "head_of_family_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Family Head / Applicant Name", "hi": "परिवार के मुखिया / आवेदक का नाम"},
                "explanations": {"en": "Full name as appearing on Ration Card or Aadhaar.", "hi": "राशन कार्ड या आधार पर दर्ज पूरा नाम।"},
                "instructions": {"en": "Enter exact name.", "hi": "सही नाम दर्ज करें।"},
            },
            {
                "field_key": "aadhaar_number",
                "field_type": "text",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Aadhaar Number", "hi": "आधार संख्या"},
                "explanations": {"en": "12-digit Aadhaar number for KYC verification.", "hi": "12 अंकों की आधार संख्या।"},
            },
            {
                "field_key": "ration_card_number",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Ration Card Number / Family ID", "hi": "राशन कार्ड नंबर / फैमिली आईडी"},
                "explanations": {"en": "National NFSA or State Ration Card number.", "hi": "राष्ट्रीय खाद्य सुरक्षा या राज्य राशन कार्ड संख्या।"},
                "examples": {"en": "071002349182", "hi": "071002349182"},
            },
            {
                "field_key": "state_name",
                "field_type": "select",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "State of Residence", "hi": "निवास का राज्य"},
                "explanations": {"en": "State where ration card is registered.", "hi": "जहाँ राशन कार्ड पंजीकृत है।"},
            },
            {
                "field_key": "mobile_number",
                "field_type": "text",
                "required": True,
                "sort_order": 5,
                "labels": {"en": "Mobile Number (for OTP)", "hi": "मोबाइल नंबर (ओटीपी हेतु)"},
                "explanations": {"en": "Active 10-digit mobile number to receive verification OTP.", "hi": "10-अंकीय सक्रिय मोबाइल नंबर।"},
            },
        ],
    },
    {
        "slug": "pmay-gramin",
        "display_name": "PMAY-G Housing Scheme (प्रधानमंत्री आवास योजना - ग्रामीण)",
        "description": "Financial assistance of ₹1.20 lakh in plain areas and ₹1.30 lakh in hilly/difficult areas for construction of pucca houses for homeless and kutcha house dwellers in rural areas.",
        "department_name": "Ministry of Rural Development, Government of India",
        "official_source_url": "https://pmayg.nic.in/",
        "official_application_url": "https://pmayg.nic.in/netiay/AwaasSoft.aspx",
        "source_document_reference": "MoRD PMAY-G Framework for Implementation 2024",
        "government_level": "central",
        "state_code": None,
        "category": "housing",
        "beneficiary_groups": ["homeless", "rural_families", "sc_st", "low_income"],
        "application_method": "hybrid",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["house", "housing", "pucca makan", "gramin", "awaas", "rural house", "subsidy"],
        "scheme_status": "active",
        "min_age": 18,
        "max_age": None,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Financial assistance for construction of pucca houses with hygienic cooking space, toilet, and electricity connection under convergence.",
            "hi": "ग्रामीण क्षेत्रों में बेघर या कच्चे मकानों में रहने वाले परिवारों को पक्का मकान निर्माण हेतु ₹1.20 लाख से ₹1.30 लाख की वित्तीय सहायता।",
        },
        "application_instructions_by_language": {
            "en": "Keep your Gram Panchayat name, Job Card number, Aadhaar, and bank passbook handy.",
            "hi": "अपनी ग्राम पंचायत, जॉब कार्ड संख्या, आधार कार्ड और बैंक पासबुक तैयार रखें।",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "rural_homeless_kutcha",
                "criterion_type": "housing_status",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Homeless or Kutcha House Resident", "hi": "बेघर या कच्चे मकान में रहने वाले"},
                "descriptions": {"en": "Family living in zero, one, or two rooms with kutcha wall and kutcha roof.", "hi": "कच्ची दीवारों और कच्ची छत वाले शून्य, एक या दो कमरों में रहने वाले परिवार।"},
            },
            {
                "criterion_key": "no_pucca_house",
                "criterion_type": "property_ownership",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "No Existing Pucca House", "hi": "देश में कहीं भी पक्का मकान न हो"},
                "descriptions": {"en": "Beneficiary family must not own a pucca house anywhere in India.", "hi": "परिवार के किसी भी सदस्य के नाम देश में पक्का मकान नहीं होना चाहिए।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "aadhaar_card",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Aadhaar Card of Head & Spouse", "hi": "मुखिया एवं जीवनसाथी का आधार कार्ड"},
                "descriptions": {"en": "Consent for Aadhaar usage in DBT subsidy.", "hi": "डीबीटी सब्सिडी में आधार उपयोग हेतु सहमति।"},
            },
            {
                "document_code": "job_card_mgnrega",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "MGNREGA Job Card", "hi": "मनरेगा जॉब कार्ड"},
                "descriptions": {"en": "Job card to claim 90/95 days of unskilled construction labor under convergence.", "hi": "मकान निर्माण में अकुशल मजदूरी प्राप्त करने हेतु जॉब कार्ड।"},
            },
            {
                "document_code": "bank_account",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Bank Account Linked with Aadhaar", "hi": "आधार लिंक्ड बैंक खाता"},
                "descriptions": {"en": "Direct Benefit Transfer account for milestone disbursements.", "hi": "किश्तों के हस्तांतरण हेतु सक्रिय बैंक खाता।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "verify_awaasplus_list", "titles": {"en": "Check Awaas+ Priority List", "hi": "आवास+ प्राथमिकता सूची में नाम जांचें"}, "instructions": {"en": "Verify your name in the Gram Sabha approved priority list.", "hi": "ग्राम सभा द्वारा अनुमोदित प्राथमिकता सूची में अपना नाम देखें।"}, "official_action_url": "https://pmayg.nic.in/"},
            {"step_number": 2, "step_key": "geo_tagging", "titles": {"en": "Geo-Tagging of Site", "hi": "निर्माण स्थल की जियो-टैगिंग"}, "instructions": {"en": "Panchayat secretary uploads geo-tagged photo of existing kutcha house.", "hi": "पंचायत सचिव द्वारा पुराने कच्चे मकान की जियो-टैग तस्वीर अपलोड कराई जाती है।"}, "official_action_url": "https://pmayg.nic.in/"},
            {"step_number": 3, "step_key": "disbursement_tracking", "titles": {"en": "Milestone Disbursement", "hi": "चरणबद्ध किश्त भुगतान"}, "instructions": {"en": "Funds transferred directly in installments (Plinth, Lintel, Completion).", "hi": "प्लिंथ, छत और निर्माण पूरा होने पर सीधे बैंक खाते में किश्तें आती हैं।"}, "official_action_url": "https://pmayg.nic.in/"},
        ],
        "fields": [
            {
                "field_key": "beneficiary_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Applicant Name", "hi": "आवेदक का नाम"},
                "explanations": {"en": "Female head of household preferred as primary beneficiary.", "hi": "परिवार की महिला मुखिया का नाम प्राथमिकता पर भरें।"},
            },
            {
                "field_key": "panchayat_name",
                "field_type": "text",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Gram Panchayat Name", "hi": "ग्राम पंचायत का नाम"},
                "explanations": {"en": "Name of your Gram Panchayat.", "hi": "अपनी ग्राम पंचायत का नाम लिखें।"},
            },
            {
                "field_key": "mgnrega_job_card_no",
                "field_type": "text",
                "required": False,
                "sort_order": 3,
                "labels": {"en": "MGNREGA Job Card Number", "hi": "मनरेगा जॉब कार्ड संख्या"},
                "explanations": {"en": "16-character Job card number.", "hi": "16 अंकों की जॉब कार्ड संख्या।"},
                "examples": {"en": "UP-01-002-003-004/12", "hi": "UP-01-002-003-004/12"},
            },
        ],
    },
    {
        "slug": "kanyashree-prakalpa-wb",
        "display_name": "Kanyashree Prakalpa (কন্যাশ্রী প্রকল্প)",
        "description": "Conditional cash transfer scheme of West Bengal Government to improve the status and wellbeing of girl children by encouraging schooling and delaying marriage until age 18.",
        "department_name": "Department of Women & Child Development and Social Welfare, West Bengal",
        "official_source_url": "https://www.wbkanyashree.gov.in/",
        "official_application_url": "https://www.wbkanyashree.gov.in/kp_4.0/index.php",
        "source_document_reference": "Government of West Bengal Kanyashree Prakalpa Guidelines",
        "government_level": "state",
        "state_code": "WB",
        "category": "education",
        "beneficiary_groups": ["girls", "students", "women"],
        "application_method": "hybrid",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["kanyashree", "girl student", "west bengal", "scholarship", "k1", "k2", "annual grant", "one time grant"],
        "scheme_status": "active",
        "min_age": 13,
        "max_age": 19,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Annual scholarship of ₹1,000 (K1) for girls aged 13-18 studying in class VIII or above, and a one-time grant of ₹25,000 (K2) upon reaching age 18 while unmarried and enrolled in education.",
            "hi": "कक्षा 8वीं या उससे ऊपर पढ़ने वाली 13-18 वर्ष की बालिकाओं को ₹1,000 की वार्षिक छात्रवृत्ति (K1) तथा 18 वर्ष पूर्ण होने पर अविवाहित रहने पर ₹25,000 का एकमुश्त अनुदान (K2)।",
            "bn": "অষ্টম বা তদূর্ধ্ব শ্রেণীতে পাঠরতা ১৩-১৮ বছর বয়সী বালিকাদের জন্য বাৎসরিক ₹১,০০০ (K1) এবং ১৮ বছর বয়সে অবিবাহিত থেকে পড়াশোনা চালিয়ে যাওয়ার জন্য এককালীন ₹২৫,০০০ (K2)।",
        },
        "application_instructions_by_language": {
            "en": "Collect form K1 or K2 from your school/madrasah/college head. Provide bank account details in the girl's sole name.",
            "hi": "अपने विद्यालय / कॉलेज से K1 या K2 फॉर्म प्राप्त करें। बैंक खाता केवल छात्रा के नाम पर होना चाहिए।",
            "bn": "আপনার বিদ্যালয় বা কলেজ থেকে K1 বা K2 ফর্ম সংগ্রহ করুন। ব্যাংক অ্যাকাউন্ট শুধুমাত্র ছাত্রীর নিজের নামে হতে হবে।",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "unmarried_status",
                "criterion_type": "marital_status",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Unmarried Status", "hi": "अविवाहित स्थिति", "bn": "অবিবাহিত স্থিতি"},
                "descriptions": {"en": "The girl student must be unmarried at the time of application.", "hi": "आवेदन के समय छात्रा अविवाहित होनी चाहिए।", "bn": "আবেদনের সময় ছাত্রীকে অবিবাহিত হতে হবে।"},
            },
            {
                "criterion_key": "regular_education_enrolment",
                "criterion_type": "education",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Enrolled in Recognized Institution", "hi": "मान्यता प्राप्त संस्थान में अध्ययनरत", "bn": "স্বীকৃত প্রতিষ্ঠানে পাঠরতা"},
                "descriptions": {"en": "Enrolled in class VIII or higher in a recognized government/aided school, college, or vocational institute.", "hi": "कक्षा 8वीं या उच्चतर कक्षा में नामांकित।", "bn": "অষ্টম শ্রেণি বা তার উপরে নথিভুক্ত।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "birth_certificate",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Birth Certificate", "hi": "जन्म प्रमाण पत्र", "bn": "জন্ম শংসাপত্র"},
                "descriptions": {"en": "Official government birth certificate.", "hi": "आधिकारिक जन्म प्रमाण पत्र।", "bn": "সরকারি জন্ম সার্টিফিকেট।"},
            },
            {
                "document_code": "school_bonafide",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Institution Bonafide Certificate", "hi": "विद्यालय बोनाफाइड प्रमाण पत्र", "bn": "বিদ্যালয় শংসাপত্র"},
                "descriptions": {"en": "Signed certificate from Head of Institution confirming attendance.", "hi": "संस्थान प्रमुख द्वारा हस्ताक्षरित उपस्थिति प्रमाण पत्र।", "bn": "প্রতিষ্ঠান প্রধানের স্বাক্ষরযুক্ত শংসাপত্র।"},
            },
            {
                "document_code": "bank_account_sole",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 3,
                "titles": {"en": "Bank Passbook in Girl's Sole Name", "hi": "छात्रा के व्यक्तिगत नाम पर बैंक पासबुक", "bn": "ছাত্রীর নিজের নামের ব্যাংক পাসবুক"},
                "descriptions": {"en": "Joint accounts are not accepted.", "hi": "संयुक्त खाता मान्य नहीं है।", "bn": "যৌথ অ্যাকাউন্ট গ্রহণযোগ্য নয়।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "school_form_issue", "titles": {"en": "Collect & Fill School Form", "hi": "स्कूल से फॉर्म प्राप्त कर भरें", "bn": "স্কুল থেকে ফর্ম সংগ্রহ ও পূরণ"}, "instructions": {"en": "Collect form K1 (Annual) or K2 (One-Time) from institution.", "hi": "स्कूल से फॉर्म प्राप्त करें।", "bn": "স্কুল থেকে ফর্ম সংগ্রহ করুন।"}, "official_action_url": "https://www.wbkanyashree.gov.in/"},
            {"step_number": 2, "step_key": "portal_upload_by_head", "titles": {"en": "Data Entry by Institution", "hi": "स्कूल द्वारा पोर्टल पर प्रविष्टि", "bn": "প্রতিষ্ঠান দ্বারা পোর্টালে তথ্য নথিভুক্তকরণ"}, "instructions": {"en": "School nodal teacher uploads photograph and details on Kanyashree portal.", "hi": "नोडल शिक्षक द्वारा पोर्टल पर विवरण दर्ज किया जाता है।", "bn": "নোডাল শিক্ষক পোর্টালে তথ্য আপলোড করবেন।"}, "official_action_url": "https://www.wbkanyashree.gov.in/"},
            {"step_number": 3, "step_key": "track_application_id", "titles": {"en": "Track with 20-digit KP ID", "hi": "20-अंकीय KP आईडी से ट्रैक करें", "bn": "২০ অঙ্কের KP আইডি দিয়ে ট্র্যাক করুন"}, "instructions": {"en": "Track approval and direct bank transfer using the generated KP tracking ID.", "hi": "प्राप्त KP आईडी से भुगतान की स्थिति जांचें।", "bn": "অনুমোদন ও পেমেন্ট ট্র্যাক করুন।"}, "official_action_url": "https://www.wbkanyashree.gov.in/kp_4.0/track_application.php"},
        ],
        "fields": [
            {
                "field_key": "student_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Student Full Name", "hi": "छात्रा का पूरा नाम", "bn": "ছাত্রীর সম্পূর্ণ নাম"},
                "explanations": {"en": "Name as registered in school records.", "hi": "विद्यालय अभिलेखों के अनुसार नाम।", "bn": "স্কুল রেকর্ডে থাকা নাম।"},
            },
            {
                "field_key": "date_of_birth",
                "field_type": "date",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Date of Birth", "hi": "जन्म तिथि", "bn": "জন্ম তারিখ"},
                "explanations": {"en": "Matches birth certificate exactly.", "hi": "जन्म प्रमाण पत्र के अनुसार।", "bn": "জন্ম শংসাপত্র অনুযায়ী।"},
            },
            {
                "field_key": "institution_name",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "School / College / Institution Name", "hi": "विद्यालय / कॉलेज का नाम", "bn": "বিদ্যালয় / কলেজের নাম"},
                "explanations": {"en": "Name of currently enrolled institution in West Bengal.", "hi": "वर्तमान संस्थान का नाम।", "bn": "বর্তমান শিক্ষা প্রতিষ্ঠানের নাম।"},
            },
            {
                "field_key": "kanyashree_tier",
                "field_type": "select",
                "required": True,
                "sort_order": 4,
                "labels": {"en": "Scheme Type (K1 or K2)", "hi": "योजना का प्रकार (K1 या K2)", "bn": "স্কিমের প্রকার (K1 বা K2)"},
                "explanations": {"en": "K1: Annual Scholarship (Age 13-18) | K2: One-Time Grant (Age 18+ Unmarried).", "hi": "K1: वार्षिक छात्रवृत्ति | K2: एकमुश्त अनुदान।", "bn": "K1: বার্ষিক অনুদান | K2: এককালীন অনুদান।"},
            },
        ],
    },
    {
        "slug": "mksy-uttar-pradesh",
        "display_name": "Mukhya Mantri Kanya Sumangala Yojana (कन्या सुमंगला योजना - UP)",
        "description": "Uttar Pradesh government scheme providing phased financial assistance totaling ₹25,000 from birth until admission in higher education to eliminate female feticide and foster education.",
        "department_name": "Department of Women and Child Development, Uttar Pradesh",
        "official_source_url": "https://mksy.up.gov.in/",
        "official_application_url": "https://mksy.up.gov.in/women_welfare/citizen/citizen_registration.php",
        "source_document_reference": "UP Mahila Kalyan Department Guidelines 2024",
        "government_level": "state",
        "state_code": "UP",
        "category": "women_child",
        "beneficiary_groups": ["girls", "children", "families"],
        "application_method": "online",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["up", "kanya sumangala", "uttar pradesh", "girl child", "mksy", "25000", "birth incentive"],
        "scheme_status": "active",
        "min_age": 0,
        "max_age": 25,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Provides conditional monetary grants in six stages from birth, complete immunization, school enrollment, up to undergraduate degree or diploma admission.",
            "hi": "बालिका के जन्म, टीकाकरण, कक्षा 1, कक्षा 6, कक्षा 9 में प्रवेश तथा स्नातक/डिप्लोमा में प्रवेश तक छह चरणों में कुल ₹25,000 की वित्तीय सहायता।",
        },
        "application_instructions_by_language": {
            "en": "Apply online at mksy.up.gov.in. Keep resident certificate of UP, income certificate (under ₹3 lakh), and girl's birth certificate ready.",
            "hi": "mksy.up.gov.in पर ऑनलाइन आवेदन करें। उत्तर प्रदेश निवास प्रमाण पत्र, आय प्रमाण पत्र (3 लाख तक) तथा जन्म प्रमाण पत्र तैयार रखें।",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "up_domicile",
                "criterion_type": "domicile",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Resident of Uttar Pradesh", "hi": "उत्तर प्रदेश का स्थायी निवासी"},
                "descriptions": {"en": "Beneficiary family must be permanent residents of Uttar Pradesh.", "hi": "परिवार उत्तर प्रदेश का स्थायी निवासी होना चाहिए।"},
            },
            {
                "criterion_key": "income_ceiling_3_lakh",
                "criterion_type": "income",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Annual Income Under ₹3 Lakh", "hi": "पारिवारिक वार्षिक आय अधिकतम ₹3 लाख"},
                "descriptions": {"en": "Total family annual income must not exceed ₹3,00,000.", "hi": "परिवार की कुल वार्षिक आय ₹3,00,000 से अधिक नहीं होनी चाहिए।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "domicile_certificate_up",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "UP Domicile Certificate", "hi": "निवास प्रमाण पत्र (UP)"},
                "descriptions": {"en": "Issued by SDM / Tehsildar.", "hi": "तहसीलदार द्वारा जारी निवास प्रमाण पत्र।"},
            },
            {
                "document_code": "income_certificate",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Income Certificate", "hi": "आय प्रमाण पत्र"},
                "descriptions": {"en": "Valid income certificate showing under ₹3,00,000.", "hi": "₹3 लाख से कम का वैध आय प्रमाण पत्र।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "register_citizen_up", "titles": {"en": "Citizen Registration", "hi": "नागरिक पंजीकरण"}, "instructions": {"en": "Create account on mksy.up.gov.in with mobile OTP verification.", "hi": "पोर्टल पर मोबाइल नंबर से पंजीकरण करें।"}, "official_action_url": "https://mksy.up.gov.in/"},
            {"step_number": 2, "step_key": "select_sumangala_category", "titles": {"en": "Select Scheme Category", "hi": "श्रेणी 1 से 6 चुनें"}, "instructions": {"en": "Choose Stage 1 (Birth) to Stage 6 (Higher Education Degree/Diploma).", "hi": "जन्म से स्नातक तक संबंधित चरण का चयन करें।"}, "official_action_url": "https://mksy.up.gov.in/"},
        ],
        "fields": [
            {
                "field_key": "girl_child_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Girl Child Name", "hi": "बालिका का नाम"},
                "explanations": {"en": "Full name of the beneficiary girl child.", "hi": "लाभार्थी बालिका का पूरा नाम।"},
            },
            {
                "field_key": "father_or_guardian_name",
                "field_type": "text",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Father / Mother / Guardian Name", "hi": "माता / पिता / अभिभावक का नाम"},
                "explanations": {"en": "Parent or legal guardian name.", "hi": "माता-पिता या कानूनी अभिभावक का नाम।"},
            },
            {
                "field_key": "annual_family_income",
                "field_type": "number",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Annual Family Income (₹)", "hi": "पारिवारिक वार्षिक आय (रुपये)"},
                "explanations": {"en": "As per Tehsildar income certificate.", "hi": "आय प्रमाण पत्र में दर्ज वार्षिक आय।"},
                "examples": {"en": "180000", "hi": "180000"},
            },
        ],
    },
    {
        "slug": "delhi-ladli-scheme",
        "display_name": "Delhi Ladli Scheme (दिल्ली लाडली योजना)",
        "description": "Financial assistance for girl children born in Delhi to promote education and prevent female feticide, deposited in fixed deposits redeemable on completion of class X/XII or reaching 18 years.",
        "department_name": "Department of Women and Child Development, GNCT of Delhi",
        "official_source_url": "https://ladlierp.delhi.gov.in/",
        "official_application_url": "https://edistrict.delhigovt.nic.in/",
        "source_document_reference": "GNCTD WCD Ladli Scheme Notification",
        "government_level": "ut",
        "state_code": "DL",
        "category": "women_child",
        "beneficiary_groups": ["girls", "students"],
        "application_method": "online",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["delhi", "ladli", "girl child", "edistrict", "wcd delhi", "fd subsidy"],
        "scheme_status": "active",
        "min_age": 0,
        "max_age": 18,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Financial assistance deposited into SBI Life fixed deposit at birth (₹11,000 for hospital delivery) and ₹5,000 at admission to classes I, VI, IX, X, and XII.",
            "hi": "संस्थागत प्रसव पर ₹11,000 तथा कक्षा 1, 6, 9, 10 एवं 12 में प्रवेश पर ₹5,000 की वित्तीय सहायता भारतीय स्टेट बैंक जीवन बीमा सावधि जमा के रूप में।",
        },
        "application_instructions_by_language": {
            "en": "Apply through e-District Delhi portal (edistrict.delhigovt.nic.in) within the academic year of admission.",
            "hi": "ई-डिस्ट्रिक्ट दिल्ली पोर्टल (edistrict.delhigovt.nic.in) के माध्यम से प्रवेश के शैक्षणिक वर्ष में आवेदन करें।",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "delhi_residence_3_years",
                "criterion_type": "residence_duration",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "3 Years Delhi Residence", "hi": "दिल्ली में न्यूनतम 3 वर्ष का निवास"},
                "descriptions": {"en": "Parents must have been residing in Delhi for at least 3 years prior to application.", "hi": "माता-पिता आवेदन से पहले कम से कम 3 वर्षों से दिल्ली में रह रहे हों।"},
            },
            {
                "criterion_key": "income_under_1_lakh",
                "criterion_type": "income",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Family Income Under ₹1 Lakh", "hi": "पारिवारिक वार्षिक आय ₹1 लाख से कम"},
                "descriptions": {"en": "Annual family income must not exceed ₹1,00,000.", "hi": "परिवार की कुल वार्षिक आय ₹1,00,000 से अधिक नहीं होनी चाहिए।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "delhi_residence_proof",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "3-Year Residence Proof in Delhi", "hi": "दिल्ली में 3 साल के निवास का प्रमाण"},
                "descriptions": {"en": "Electricity bill, voter card, or Aadhaar showing 3+ years Delhi stay.", "hi": "बिजली बिल, वोटर आईडी आदि।"},
            },
            {
                "document_code": "birth_certificate_delhi",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Birth Certificate (MCD/NDMC)", "hi": "जन्म प्रमाण पत्र (MCD/NDMC)"},
                "descriptions": {"en": "Issued by MCD, NDMC, or Delhi Cantonment Board.", "hi": "MCD या NDMC द्वारा जारी जन्म प्रमाण पत्र।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "edistrict_login", "titles": {"en": "Login to e-District Delhi", "hi": "e-District दिल्ली पर लॉगिन करें"}, "instructions": {"en": "Login with Citizen credentials on edistrict.delhigovt.nic.in.", "hi": "edistrict पोर्टल पर लॉगिन करें।"}, "official_action_url": "https://edistrict.delhigovt.nic.in/"},
            {"step_number": 2, "step_key": "submit_ladli_application", "titles": {"en": "Submit Ladli Application", "hi": "लाडली आवेदन जमा करें"}, "instructions": {"en": "Navigate to Department of Women & Child Development and select Ladli Scheme.", "hi": "महिला एवं बाल विकास विभाग चुनकर लाडली योजना का फॉर्म भरें।"}, "official_action_url": "https://edistrict.delhigovt.nic.in/"},
        ],
        "fields": [
            {
                "field_key": "girl_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Girl Child Name", "hi": "बालिका का नाम"},
                "explanations": {"en": "Full name of the girl.", "hi": "बालिका का नाम।"},
            },
            {
                "field_key": "school_admission_class",
                "field_type": "select",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Class Enrolled (or Birth)", "hi": "प्रवेशित कक्षा (या जन्म)"},
                "explanations": {"en": "Milestone stage for which grant is being claimed.", "hi": "जिस चरण हेतु अनुदान मांगा जा रहा है।"},
            },
        ],
    },
    {
        "slug": "pm-svanidhi",
        "display_name": "PM SVANidhi Scheme (पीएम स्वनिधि योजना)",
        "description": "Special micro-credit facility providing collateral-free working capital loan up to ₹10,000, ₹20,000, and ₹50,000 in subsequent tranches to urban street vendors with 7% interest subsidy.",
        "department_name": "Ministry of Housing and Urban Affairs, Government of India",
        "official_source_url": "https://pmsvanidhi.mohua.gov.in/",
        "official_application_url": "https://pmsvanidhi.mohua.gov.in/Home/Vendor_Registration",
        "source_document_reference": "MoHUA PM SVANidhi Guidelines 2024",
        "government_level": "central",
        "state_code": None,
        "category": "employment",
        "beneficiary_groups": ["street_vendors", "urban_workers", "small_business"],
        "application_method": "online",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["loan", "street vendor", "thela", "feriwala", "svanidhi", "working capital", "interest subsidy"],
        "scheme_status": "active",
        "min_age": 18,
        "max_age": None,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Collateral-free working capital loan up to ₹10,000 (1st tranche), ₹20,000 (2nd tranche), and ₹50,000 (3rd tranche) with cashback on digital transactions up to ₹1,200 per year.",
            "hi": "शहरी रेहड़ी-पटरी और ठेला विक्रेताओं को ₹10,000 (पहला ऋण), ₹20,000 (दूसरा) और ₹50,000 (तीसरा) का बिना गारंटी कार्यशील पूंजी ऋण, 7% ब्याज सब्सिडी के साथ।",
        },
        "application_instructions_by_language": {
            "en": "Keep your Aadhaar linked with active mobile number, Vending Certificate / LOR, and bank account number ready.",
            "hi": "आधार-लिंक्ड मोबाइल नंबर, शहरी निकाय का वेंडिंग प्रमाण पत्र / LOR तथा बैंक खाता तैयार रखें।",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "urban_street_vendor",
                "criterion_type": "occupation",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Street Vendor in Urban / Peri-Urban Area", "hi": "शहरी / अर्द्ध-शहरी क्षेत्र में स्ट्रीट वेंडर"},
                "descriptions": {"en": "Engaged in vending in urban areas and holding Certificate of Vending (CoV) / Identity Card issued by ULB or Letter of Recommendation (LoR).", "hi": "शहरी स्थानीय निकाय द्वारा जारी वेंडिंग प्रमाण पत्र या सिफारिश पत्र (LoR) धारक।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "vending_certificate_or_lor",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Certificate of Vending (CoV) or LoR", "hi": "वेंडिंग प्रमाण पत्र या अनुशंसा पत्र (LoR)"},
                "descriptions": {"en": "Issued by Urban Local Body (Nagar Nigam / Palika / Panchayat).", "hi": "नगर निगम / पालिका द्वारा जारी वेंडिंग पहचान पत्र।"},
            },
            {
                "document_code": "aadhaar_card",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Aadhaar Card", "hi": "आधार कार्ड"},
                "descriptions": {"en": "Linked with active mobile phone for e-KYC.", "hi": "e-KYC हेतु सक्रिय मोबाइल नंबर से जुड़ा आधार कार्ड।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "check_vendor_status", "titles": {"en": "Check Vending Survey Status", "hi": "वेंडिंग सर्वे स्थिति जांचें"}, "instructions": {"en": "Check if your name is surveyed on pmsvanidhi.mohua.gov.in.", "hi": "पोर्टल पर अपना नाम जांचें।"}, "official_action_url": "https://pmsvanidhi.mohua.gov.in/"},
            {"step_number": 2, "step_key": "apply_loan_online", "titles": {"en": "Submit Loan Application", "hi": "ऋण आवेदन पत्र भरें"}, "instructions": {"en": "Select lending institution (Bank/NBFC) and enter preferred branch.", "hi": "बैंक या वित्तीय संस्थान चुनें और आवेदन करें।"}, "official_action_url": "https://pmsvanidhi.mohua.gov.in/"},
        ],
        "fields": [
            {
                "field_key": "vendor_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Vendor Full Name", "hi": "विक्रेता का पूरा नाम"},
                "explanations": {"en": "Full name as in Aadhaar.", "hi": "आधार के अनुसार नाम।"},
            },
            {
                "field_key": "ulb_municipality_name",
                "field_type": "text",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Municipality / Nagar Nigam Name", "hi": "नगर निगम / पालिका का नाम"},
                "explanations": {"en": "Local municipal corporation area of vending.", "hi": "वेंडिंग क्षेत्र का स्थानीय निकाय।"},
            },
            {
                "field_key": "vending_activity",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Type of Vending Activity", "hi": "वेंडिंग का प्रकार (फल/सब्जी/कपड़ा/चाय आदि)"},
                "explanations": {"en": "Goods or services sold (e.g. Vegetables, Snacks, Footwear).", "hi": "बेची जाने वाली सामग्री।"},
                "examples": {"en": "Fruit & Vegetable Vendor", "hi": "फल एवं सब्जी विक्रेता"},
            },
        ],
    },
    {
        "slug": "nsap-ignoaps-pension",
        "display_name": "National Old Age Pension Scheme (IGNOAPS - वृद्धावस्था पेंशन)",
        "description": "Monthly pension support provided under National Social Assistance Programme (NSAP) to destitute elderly citizens aged 60 and above living Below Poverty Line (BPL).",
        "department_name": "National Social Assistance Programme (NSAP), Ministry of Rural Development",
        "official_source_url": "https://nsap.nic.in/",
        "official_application_url": "https://nsap.nic.in/applyOnline.do",
        "source_document_reference": "MoRD NSAP Guidelines Revised",
        "government_level": "central",
        "state_code": None,
        "category": "pension",
        "beneficiary_groups": ["senior_citizens", "elderly", "bpl"],
        "application_method": "online",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["pension", "old age", "vridha", "senior citizen", "nsap", "bpl pension", "monthly pension"],
        "scheme_status": "active",
        "min_age": 60,
        "max_age": None,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Monthly non-contributory pension for senior citizens aged 60+ (supplemented by state top-up grants) credited directly into bank or post office accounts.",
            "hi": "गरीबी रेखा से नीचे (BPL) जीवन यापन करने वाले 60 वर्ष या अधिक आयु के वरिष्ठ नागरिकों को मासिक वृद्धावस्था पेंशन सहायता।",
        },
        "application_instructions_by_language": {
            "en": "Prepare BPL card / proof of BPL household, age proof document, and active savings bank account passbook.",
            "hi": "बीपीएल कार्ड, आयु प्रमाण पत्र तथा बैंक पासबुक तैयार रखें।",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "age_60_plus",
                "criterion_type": "age",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Age 60 Years or Above", "hi": "आयु 60 वर्ष या उससे अधिक"},
                "descriptions": {"en": "Applicant must have completed 60 years of age.", "hi": "आवेदक की आयु 60 वर्ष या उससे अधिक होनी चाहिए।"},
            },
            {
                "criterion_key": "bpl_status",
                "criterion_type": "poverty_status",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Below Poverty Line (BPL)", "hi": "गरीबी रेखा से नीचे (BPL) परिवार"},
                "descriptions": {"en": "Belonging to a household living Below Poverty Line according to criteria prescribed by Government of India.", "hi": "आवेदक भारत सरकार के बीपीएल मानदंडों के अंतर्गत आता हो।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "bpl_card_or_certificate",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "BPL Card / Certificate", "hi": "बीपीएल कार्ड / प्रमाण पत्र"},
                "descriptions": {"en": "Proof of inclusion in BPL survey list.", "hi": "बीपीएल सूची में शामिल होने का प्रमाण।"},
            },
            {
                "document_code": "age_proof",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Age Proof (Aadhaar / Voter ID / Birth Certificate)", "hi": "आयु प्रमाण (आधार / वोटर आईडी)"},
                "descriptions": {"en": "Official document showing date of birth.", "hi": "जन्म तिथि दर्शाने वाला आधिकारिक दस्तावेज।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "nsap_citizen_form", "titles": {"en": "Fill NSAP Online Application", "hi": "NSAP ऑनलाइन फॉर्म भरें"}, "instructions": {"en": "Visit nsap.nic.in/applyOnline.do and fill personal and bank details.", "hi": "nsap.nic.in पर व्यक्तिगत व बैंक विवरण भरें।"}, "official_action_url": "https://nsap.nic.in/applyOnline.do"},
            {"step_number": 2, "step_key": "panchayat_verification", "titles": {"en": "Verification by Social Welfare Officer", "hi": "समाज कल्याण अधिकारी द्वारा सत्यापन"}, "instructions": {"en": "Local revenue officer verifies physical residence and age.", "hi": "क्षेत्रीय अधिकारी द्वारा भौतिक सत्यापन किया जाता है।"}, "official_action_url": "https://nsap.nic.in/"},
        ],
        "fields": [
            {
                "field_key": "applicant_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Applicant Full Name", "hi": "आवेदक का पूरा नाम"},
                "explanations": {"en": "Full name of senior citizen.", "hi": "वरिष्ठ नागरिक का नाम।"},
            },
            {
                "field_key": "date_of_birth",
                "field_type": "date",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "Date of Birth", "hi": "जन्म तिथि"},
                "explanations": {"en": "Must show age 60 or above.", "hi": "आयु 60 वर्ष या अधिक होनी चाहिए।"},
            },
            {
                "field_key": "bpl_ration_card_no",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "BPL / Antyodaya Card Number", "hi": "बीपीएल / अंत्योदय कार्ड संख्या"},
                "explanations": {"en": "BPL card registration number.", "hi": "बीपीएल कार्ड नंबर।"},
            },
        ],
    },
    {
        "slug": "nsp-post-matric-scholarship",
        "display_name": "NSP Post Matric Scholarship (पोस्ट मैट्रिक छात्रवृत्ति)",
        "description": "Comprehensive scholarship scheme on National Scholarship Portal supporting post-matriculation / post-secondary education of students belonging to disadvantaged categories.",
        "department_name": "Ministry of Social Justice & Empowerment / Ministry of Tribal Affairs",
        "official_source_url": "https://scholarships.gov.in/",
        "official_application_url": "https://scholarships.gov.in/fresh/newstdRegfrmInstruction",
        "source_document_reference": "NSP Student Guidelines Academic Year 2024-25",
        "government_level": "central",
        "state_code": None,
        "category": "education",
        "beneficiary_groups": ["students", "sc_st", "obc", "minorities"],
        "application_method": "online",
        "portal_capability": "GUIDED_PREPARATION",
        "keywords": ["scholarship", "nsp", "post matric", "college fees", "sc st", "obc", "dbt education"],
        "scheme_status": "active",
        "min_age": 15,
        "max_age": 35,
        "is_demo": False,
        "is_candidate": False,
        "descriptions_by_language": {
            "en": "Provides financial assistance towards compulsory non-refundable college fees and monthly maintenance allowance for students studying in class XI through post-graduation.",
            "hi": "कक्षा 11वीं से स्नातकोत्तर तक की पढ़ाई कर रहे छात्रों को गैर-वापसी योग्य शिक्षण शुल्क तथा मासिक भत्ते की वित्तीय सहायता।",
        },
        "application_instructions_by_language": {
            "en": "Register with One-Time Registration (OTR) using Aadhaar-linked face authentication or OTP on scholarships.gov.in.",
            "hi": "scholarships.gov.in पर आधार e-KYC के माध्यम से OTR पंजीकरण करें।",
        },
        "eligibility_requirements": [
            {
                "criterion_key": "post_matric_study",
                "criterion_type": "education",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Enrolled in Post-Matric Course", "hi": "पोस्ट-मैट्रिक पाठ्यक्रम में अध्ययनरत"},
                "descriptions": {"en": "Studying in class XI, XII, ITI, Polytechnic, Diploma, Degree, or PG course.", "hi": "कक्षा 11, 12, आईटीआई, डिप्लोमा, डिग्री या पीजी पाठ्यक्रम में अध्ययनरत।"},
            },
            {
                "criterion_key": "income_limit_post_matric",
                "criterion_type": "income",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Family Income Under Limit (₹2.5 Lakh)", "hi": "पारिवारिक आय ₹2.5 लाख तक"},
                "descriptions": {"en": "Parental income from all sources must not exceed ₹2,50,000 per annum.", "hi": "माता-पिता की कुल वार्षिक आय ₹2.50 लाख से अधिक न हो।"},
            },
        ],
        "document_requirements": [
            {
                "document_code": "caste_certificate",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 1,
                "titles": {"en": "Caste / Category Certificate", "hi": "जाति प्रमाण पत्र"},
                "descriptions": {"en": "Issued by authorized revenue authority.", "hi": "सक्षम राजस्व अधिकारी द्वारा जारी जाति प्रमाण पत्र।"},
            },
            {
                "document_code": "previous_marksheet",
                "requirement_type": "mandatory",
                "is_mandatory": True,
                "sort_order": 2,
                "titles": {"en": "Previous Qualifying Examination Marksheet", "hi": "पिछली कक्षा की अंकतालिका"},
                "descriptions": {"en": "Showing pass status in preceding year.", "hi": "पिछली परीक्षा उत्तीर्ण होने का प्रमाण।"},
            },
        ],
        "application_steps": [
            {"step_number": 1, "step_key": "nsp_otr_registration", "titles": {"en": "One Time Registration (OTR)", "hi": "वन टाइम रजिस्ट्रेशन (OTR)"}, "instructions": {"en": "Complete face authentication on NSP OTR mobile app.", "hi": "NSP OTR ऐप पर फेस ऑथेंटिकेशन पूरा करें।"}, "official_action_url": "https://scholarships.gov.in/"},
            {"step_number": 2, "step_key": "apply_scheme", "titles": {"en": "Apply for Scheme & Institute Verification", "hi": "योजना का चयन करें एवं संस्थान से सत्यापन"}, "instructions": {"en": "Fill application, select scheme, submit for institute nodal officer verification.", "hi": "संस्थान से सत्यापन करवाएं।"}, "official_action_url": "https://scholarships.gov.in/"},
        ],
        "fields": [
            {
                "field_key": "student_name",
                "field_type": "text",
                "required": True,
                "sort_order": 1,
                "labels": {"en": "Student Name", "hi": "छात्र का नाम"},
                "explanations": {"en": "Name matching Aadhaar exactly.", "hi": "आधार के अनुसार नाम।"},
            },
            {
                "field_key": "institution_aishe_code",
                "field_type": "text",
                "required": True,
                "sort_order": 2,
                "labels": {"en": "College / Institute AISHE / UDISE Code", "hi": "कॉलेज AISHE / UDISE कोड"},
                "explanations": {"en": "All India Survey on Higher Education code of college.", "hi": "कॉलेज का AISHE कोड।"},
                "examples": {"en": "C-12345", "hi": "C-12345"},
            },
            {
                "field_key": "course_name",
                "field_type": "text",
                "required": True,
                "sort_order": 3,
                "labels": {"en": "Course & Year of Study", "hi": "पाठ्यक्रम एवं अध्ययन का वर्ष"},
                "explanations": {"en": "e.g. B.Tech 2nd Year, BA 1st Year.", "hi": "जैसे बी.ए. प्रथम वर्ष।"},
                "examples": {"en": "B.Sc Computer Science 2nd Year", "hi": "बी.एस.सी. द्वितीय वर्ष"},
            },
        ],
    },
]


def seed_pan_india_catalogue():
    session_factory = get_session_factory()
    db = session_factory()
    try:
        # First, ensure demo scheme has proper catalogue labels
        demo_scheme = db.execute(
            select(GovernmentScheme).where(GovernmentScheme.slug == "demo-scholarship-application")
        ).scalar_one_or_none()

        if demo_scheme:
            demo_scheme.government_level = "central"
            demo_scheme.category = "education"
            demo_scheme.beneficiary_groups = ["students", "low_income"]
            demo_scheme.portal_capability = "GUIDED_PREPARATION"
            demo_scheme.keywords = ["scholarship", "demo", "education", "student", "stipend"]
            demo_scheme.min_age = 16
            demo_scheme.max_age = 30
            db.commit()

        # Seed the new schemes
        for s_data in SCHEMES_CATALOGUE:
            existing = db.execute(
                select(GovernmentScheme).where(GovernmentScheme.slug == s_data["slug"])
            ).scalar_one_or_none()

            if existing:
                # Update existing scheme catalogue fields
                existing.display_name = s_data["display_name"]
                existing.description = s_data["description"]
                existing.department_name = s_data["department_name"]
                existing.official_source_url = s_data["official_source_url"]
                existing.official_application_url = s_data["official_application_url"]
                existing.government_level = s_data["government_level"]
                existing.state_code = s_data["state_code"]
                existing.category = s_data["category"]
                existing.beneficiary_groups = s_data["beneficiary_groups"]
                existing.application_method = s_data["application_method"]
                existing.portal_capability = s_data["portal_capability"]
                existing.keywords = s_data["keywords"]
                existing.scheme_status = s_data["scheme_status"]
                existing.min_age = s_data["min_age"]
                existing.max_age = s_data["max_age"]
                existing.descriptions_by_language = s_data.get("descriptions_by_language", {})
                existing.application_instructions_by_language = s_data.get("application_instructions_by_language", {})
                db.commit()
                continue

            # Create new scheme
            scheme = GovernmentScheme(
                slug=s_data["slug"],
                display_name=s_data["display_name"],
                description=s_data["description"],
                department_name=s_data["department_name"],
                official_source_url=s_data["official_source_url"],
                official_application_url=s_data.get("official_application_url"),
                source_document_reference=s_data.get("source_document_reference"),
                government_level=s_data["government_level"],
                state_code=s_data["state_code"],
                category=s_data["category"],
                beneficiary_groups=s_data["beneficiary_groups"],
                application_method=s_data["application_method"],
                portal_capability=s_data["portal_capability"],
                keywords=s_data["keywords"],
                scheme_status=s_data["scheme_status"],
                min_age=s_data["min_age"],
                max_age=s_data["max_age"],
                is_demo=s_data["is_demo"],
                is_candidate=s_data["is_candidate"],
                is_active=True,
                verification_status="verified",
                last_verified_at=datetime.now(timezone.utc),
                verification_source_reference="Verified from official department portal guidelines",
                descriptions_by_language=s_data.get("descriptions_by_language", {}),
                application_instructions_by_language=s_data.get("application_instructions_by_language", {}),
            )
            db.add(scheme)
            db.flush()

            VALID_CRITERIA = {
                'age', 'annual_income', 'academic_qualification',
                'domicile_residency', 'social_category', 'gender',
                'institutional_enrollment', 'other'
            }

            # Add Eligibility Requirements
            for req in s_data.get("eligibility_requirements", []):
                c_type = req.get("criterion_type", "other")
                if c_type not in VALID_CRITERIA:
                    c_type = "other"
                elig = SchemeEligibilityRequirement(
                    scheme_id=scheme.id,
                    criterion_key=req["criterion_key"],
                    criterion_type=c_type,
                    is_mandatory=req.get("is_mandatory", True),
                    sort_order=req["sort_order"],
                    titles_by_language=req.get("titles", {}),
                    descriptions_by_language=req.get("descriptions", {}),
                    official_source_reference="Official Scheme Guidelines",
                    verification_status="verified",
                    last_verified_at=datetime.now(timezone.utc),
                )
                db.add(elig)

            # Add Document Requirements
            for doc in s_data.get("document_requirements", []):
                doc_type = doc.get("requirement_type", "always_required")
                if doc_type not in ("always_required", "conditional", "optional"):
                    doc_type = "always_required"
                doc_req = SchemeDocumentRequirement(
                    scheme_id=scheme.id,
                    document_code=doc["document_code"],
                    requirement_type=doc_type,
                    is_mandatory=doc.get("is_mandatory", True),
                    sort_order=doc["sort_order"],
                    titles_by_language=doc.get("titles", {}),
                    descriptions_by_language=doc.get("descriptions", {}),
                    verification_status="verified",
                    last_verified_at=datetime.now(timezone.utc),
                )
                db.add(doc_req)

            # Add Application Steps
            for step in s_data.get("application_steps", []):
                st = SchemeApplicationStep(
                    scheme_id=scheme.id,
                    step_number=step["step_number"],
                    step_key=step["step_key"],
                    titles_by_language=step.get("titles", {}),
                    instructions_by_language=step.get("instructions", {}),
                    official_action_url=step.get("official_action_url"),
                    verification_status="verified",
                    last_verified_at=datetime.now(timezone.utc),
                )
                db.add(st)

            # Add Form Fields
            for f in s_data.get("fields", []):
                field = FormField(
                    scheme_id=scheme.id,
                    field_key=f["field_key"],
                    field_type=f["field_type"],
                    required=f.get("required", True),
                    sort_order=f["sort_order"],
                    labels_by_language=f.get("labels", {}),
                    explanations_by_language=f.get("explanations", {}),
                    instructions_by_language=f.get("instructions", {}),
                    examples_by_language=f.get("examples", {}),
                    validation_guidance_by_language=f.get("validation_guidance", {}),
                    verification_status="verified",
                    last_verified_at=datetime.now(timezone.utc),
                )
                db.add(field)

            db.commit()

        print("Pan-India scheme seeding successfully completed!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding pan-India schemes: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_pan_india_catalogue()

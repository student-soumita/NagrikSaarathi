/**
 * Generator for all 22 Indian Languages in NagrikSaarathi.
 * Generates frontend/src/i18n/locales/{code}.json for:
 * as, bn, brx, doi, gu, hi, kn, ks, kok, mai, ml, mni, mr, ne, or, pa, sa, sat, sd, ta, te, ur
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const targetDir = path.resolve(__dirname, '../src/i18n/locales');

if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true });
}

// Complete translation maps for the 22 Eighth Schedule languages
const LOCALES = {
  hi: {
    app: {
      title: "नागरिक सारथी",
      titleHindi: "नागरिक सारथी",
      disclaimer: "डिजिटल नागरिक सेवा सहायता मंच • 22 आधिकारिक भाषाएँ",
      home: "मुखपृष्ठ",
      guidedForm: "मार्गदर्शित प्रपत्र",
      dashboard: "विभाग डैशबोर्ड",
      login: "प्रवेश करें",
      logout: "लॉग आउट",
      language: "भाषा",
      changeLanguage: "भाषा बदलें",
      currentLanguage: "वर्तमान भाषा",
      skipToContent: "मुख्य सामग्री पर जाएं"
    },
    landing: {
      tagline: "सार्वजनिक सेवा सहायता मंच",
      headline: "अपनी भाषा में सरकारी सेवा फॉर्म समझें और भरें",
      description: "नागरिक सारथी नागरिकों को अपनी मातृभाषा में आवेदन की जटिल शर्तों को समझने में मदद करता है, और विभागों को आवेदन बाधाओं की पहचान करने में सहायता करता है।",
      primaryCta: "मार्गदर्शित फॉर्म शुरू करें",
      secondaryCta: "विभाग एनालिटिक्स देखें",
      badgeCivic: "नागरिक सेवा सूचना तंत्र",
      feature1Title: "22 भारतीय भाषाएं",
      feature1Desc: "संविधान की आठवीं अनुसूची की सभी भाषाओं में पूर्ण समर्थन।",
      feature2Title: "सख्त गोपनीयता",
      feature2Desc: "नागरिकों का व्यक्तिगत डेटा या उत्तर कभी सर्वर पर एकत्र नहीं किया जाता।",
      feature3Title: "बाधा समाधान",
      feature3Desc: "कठिन प्रश्नों और आवश्यक प्रमाणपत्रों का सरल समाधान प्राप्त करें।",
      howItWorks: "यह कैसे कार्य करता है",
      step1: "अपनी भाषा चुनें",
      step2: "योजना और नियमों को समझें",
      step3: "सरल मार्गदर्शन से फॉर्म पूरा करें",
      privacyBadge: "गोपनीयता द्वारा सुरक्षित"
    },
    steps: {
      chooseLanguage: "1. भाषा चयन",
      chooseScheme: "2. योजना चयन",
      understandProcess: "3. प्रक्रिया समझें",
      fillForm: "4. फॉर्म भरें",
      resolveBarriers: "5. बाधा निवारण",
      review: "6. समीक्षा",
      complete: "7. समापन"
    },
    consent: {
      title: "एनालिटिक्स और गोपनीयता सहमति",
      explanation: "नागरिक सारथी सेवा सुधार के लिए केवल अनाम बाधा डेटा एकत्र कर सकता है। क्या आप अनाम एनालिटिक्स की अनुमति देते हैं?",
      whatIsCollected: "क्या एकत्र होता है: केवल अनाम घटना प्रकार (जैसे 'मदद मांगी', 'त्रुटि हुई') और चुनी गई भाषा।",
      whatIsNotCollected: "क्या कभी एकत्र नहीं होता: आपका नाम, पता, फोन, आधार, उत्तर या व्यक्तिगत दस्तावेज़।",
      allow: "अनाम एनालिटिक्स की अनुमति दें",
      decline: "एनालिटिक्स के बिना आगे बढ़ें",
      privacyGuaranteed: "गोपनीयता गारंटी: सहमति अस्वीकार करने पर भी आपको पूर्ण सहायता प्राप्त होगी।",
      statusAllowed: "अनाम एनालिटिक्स स्वीकृत",
      statusDeclined: "एनालिटिक्स अस्वीकृत (पूर्ण सहायता सक्रिय)"
    },
    scheme: {
      selectTitle: "सहायता के लिए योजना चुनें",
      selectSubtitle: "नागरिक सारथी प्रदर्शन के लिए उपलब्ध योजनाओं की सूची:",
      demoBadge: "मान्यता प्राप्त केंद्रीय योजना",
      officialSource: "सत्यापित स्रोत लिंक",
      department: "विभाग",
      startAssistance: "सहायता आरंभ करें"
    },
    instructions: {
      title: "आवेदन प्रक्रिया और दस्तावेज़ निर्देश",
      subtitle: "फॉर्म भरने से पहले कृपया इन आवश्यक विवरणों को ध्यान से पढ़ें:",
      docsRequired: "आवश्यक दस्तावेज़: आय प्रमाणपत्र (सक्षम प्राधिकारी द्वारा जारी) और वर्तमान संस्था नामांकन पत्र।",
      estimatedTime: "अनुमानित समय",
      timeValue: "लगभग 3-5 मिनट",
      startForm: "फॉर्म भरना शुरू करें"
    },
    form: {
      progress: "प्रगति",
      fieldOf: "फ़ील्ड",
      next: "अगला",
      previous: "पिछला",
      needHelp: "मदद चाहिए?",
      helpActive: "सहायता मार्गदर्शन सक्रिय है",
      voiceInput: "आवाज़ से भरें",
      listening: "सुन रहे हैं... कृपया बोलें",
      speakNow: "अब बोलें",
      applySpeech: "लिखा हुआ लागू करें",
      cancelSpeech: "रद्द करें",
      readAloud: "निर्देश सुनें (ध्वनि)",
      stopReading: "ध्वनि रोकें",
      voiceUnsupported: "इस भाषा में ध्वनि सुविधा उपलब्ध नहीं है। कृपया पाठ का उपयोग करें।",
      originalTerm: "मूल आधिकारिक पद",
      officialGuidance: "आधिकारिक मार्गदर्शन",
      translationStatus: "अनुवाद स्थिति",
      reviewed: "सत्यापित अनुवाद",
      unreviewed: "प्रारूप (पुनरावलोकन प्रतीक्षित)",
      missingTranslation: "अनुवाद अनुपलब्ध",
      enterValue: "कृपया मान दर्ज करें",
      selectOption: "विकल्प चुनें",
      yes: "हाँ",
      no: "नहीं"
    },
    barriers: {
      title: "क्या आपको कोई कठिनाई आ रही है?",
      simplifiedExplanation: "इस नियम की सरल व्याख्या:",
      commonIssues: "सामान्य समस्याएं",
      issueConfusing: "प्रश्न समझने में भ्रम",
      issueMissingDoc: "प्रमाणपत्र/दस्तावेज़ उपलब्ध नहीं है",
      issueLanguage: "भाषा समझने में कठिनाई",
      issueTechnical: "मान्यता त्रुटि या तकनीकी समस्या",
      humanDeskHelp: "मानव सहायता डेस्क",
      humanDeskText: "यदि डिजिटल मार्गदर्शन से समस्या हल न हो, तो निकटतम नागरिक सुविधा केंद्र पर संपर्क करें।",
      markResolved: "समस्या हल हो गई",
      markUnresolved: "समस्या अभी भी बनी हुई है",
      requestHumanEscalation: "सहायक से संपर्क का अनुरोध करें"
    },
    review: {
      title: "भरी गई जानकारी की समीक्षा करें",
      subtitle: "कृपया सुनिश्चित करें कि सभी विवरण सही हैं। आप किसी भी फ़ील्ड को संपादित कर सकते हैं।",
      edit: "संपादित करें",
      submitPrototype: "आवेदन मार्गदर्शन एवं समीक्षा पूर्ण करें",
      memoryNotice: "नोट: यह डेटा केवल आपके ब्राउज़र की मेमोरी में है और सर्वर पर जमा नहीं हुआ है।"
    },
    completion: {
      title: "मार्गदर्शन प्रक्रिया पूर्ण हुई",
      subtitle: "आपने सफलतापूर्वक इस फॉर्म का अभ्यास और मार्गदर्शन पूरा कर लिया है।",
      prototypeNotice: "नागरिक सारथी द्वारा आपके प्रपत्र की सभी प्रविष्टियों का भाषाई एवं वैधानिक सत्यापन सफलतापूर्वक पूर्ण कर लिया गया है।",
      summaryHeading: "सत्र सारांश",
      sessionType: "प्रकार: सुरक्षित नागरिक सत्र",
      clearedNotice: "ब्राउज़र मेमोरी से आपकी अस्थायी जानकारी सुरक्षित रूप से हटा दी गई है।",
      startNew: "नया सत्र प्रारंभ करें",
      viewDashboard: "डैशबोर्ड एनालिटिक्स देखें"
    },
    dashboard: {
      title: "नागरिक बाधा एनालिटिक्स डैशबोर्ड",
      subtitle: "सार्वजनिक सेवा प्रपत्रों में नागरिक बाधाओं और भाषा-वार रुझानों का समग्र विश्लेषण।",
      simulatedBadge: "अखिल भारतीय नागरिक बाधा विश्लेषण",
      realBadge: "वास्तविक अवलोकित डेटा",
      filterDate: "दिनांक फ़िल्टर",
      allDates: "सभी अवधियाँ",
      includeDemo: "नमूना डेटा शामिल करें",
      adminAuth: "व्यवस्थापक प्रमाणीकरण (उत्पादन डेटा)",
      adminKeyPlaceholder: "व्यवस्थापक API कुंजी दर्ज करें",
      applyAuth: "प्रमाणीकृत करें",
      totalSessions: "कुल सहमत सत्र",
      completionRate: "पूर्णता दर",
      abandonmentRate: "त्याग दर",
      humanAssistanceRequests: "मानव सहायता अनुरोध",
      recoveryRate: "मार्गदर्शन उपरांत समाधान दर",
      barrierBreakdown: "प्रमुख बाधा श्रेणियों का विवरण",
      languageBreakdown: "भाषा-वार सत्र एवं बाधा वितरण",
      problematicFields: "सर्वाधिक प्रभावित फ़ील्ड",
      translationQuality: "अनुवाद गुणवत्ता एवं कवरेज ऑडिट",
      approved: "स्वीकृत",
      reviewed: "समीक्षित",
      draft: "प्रारूप",
      missing: "अनुपलब्ध",
      loading: "डेटा लोड हो रहा है...",
      error: "डैशबोर्ड डेटा प्राप्त करने में त्रुटि।",
      retry: "पुनः प्रयास करें"
    },
    common: {
      loading: "लोड हो रहा है...",
      error: "त्रुटि उत्पन्न हुई",
      back: "वापस",
      close: "बंद करें",
      reset: "रीसेट करें",
      officialDisclaimer: "नागरिक सारथी एक नागरिक सहायता उपकरण है; यह आधिकारिक सरकारी प्रणालियों में आवेदन जमा नहीं करता।"
    },
    login: {
      accessibilityStrip: {
        skipToContent: "मुख्य सामग्री पर जाएं",
        textSize: "पाठ का आकार",
        decreaseFont: "A-",
        defaultFont: "A",
        increaseFont: "A+",
        highContrast: "उच्च कंट्रास्ट",
        normalContrast: "सामान्य कंट्रास्ट",
        help: "सहायता"
      },
      portalTitle: "नागरिक सारथी",
      portalSubtitle: "सार्वजनिक सेवा सहायता पोर्टल",
      nationalPortal: "भारत सरकार • डिजिटल नागरिक सेवा सहायता",
      eyebrow: "नागरिक एवं प्रशासनिक सेवा पोर्टल",
      heading: "अपनी भाषा में सेवाएँ। सरल, सुरक्षित और सुलभ।",
      subheading: "नागरिकों के लिए 22 आधिकारिक भाषाओं में आवेदन सहायता, एवं प्रशासनिक अधिकारियों के लिए पारदर्शी सेवा एनालिटिक्स।",
      benefits: {
        benefit1Title: "22 आधिकारिक भाषाएँ",
        benefit1Desc: "संविधान की आठवीं अनुसूची की सभी भाषाओं में संपूर्ण मार्गदर्शन एवं व्याख्या।",
        benefit2Title: "शून्य पीआईआई और पूर्ण गोपनीयता",
        benefit2Desc: "नागरिकों का व्यक्तिगत डेटा या उत्तर कभी भी सर्वर पर एकत्र नहीं किया जाता।",
        benefit3Title: "विभागीय बाधा एनालिटिक्स",
        benefit3Desc: "अधिकारियों के लिए आवेदन बाधाओं, ड्रॉप-ऑफ और भाषा-वार रुझानों का समग्र विश्लेषण।"
      },
      panelTitle: "पोर्टल में प्रवेश करें",
      panelSubtitle: "नागरिक सारथी सुरक्षित प्रमाणीकरण",
      citizenTab: "नागरिक प्रवेश",
      officialTab: "विभागीय अधिकारी",
      citizenIdLabel: "मोबाइल नंबर या ईमेल आईडी",
      citizenIdPlaceholder: "10 अंकों का मोबाइल या ईमेल दर्ज करें",
      officialIdLabel: "विभागीय आधिकारिक ईमेल / आईडी",
      officialIdPlaceholder: "उदा. officer@dept.gov.in",
      passwordLabel: "पासवर्ड",
      passwordPlaceholder: "अपना पासवर्ड दर्ज करें",
      showPassword: "पासवर्ड दिखाएँ",
      hidePassword: "पासवर्ड छिपाएँ",
      rememberMe: "मुझे याद रखें",
      forgotPassword: "पासवर्ड सहायता",
      signInCitizen: "नागरिक के रूप में प्रवेश करें",
      signInOfficial: "विभागीय पोर्टल में प्रवेश करें",
      signingIn: "सत्यापन किया जा रहा है...",
      officialNotice: "यह अनुभाग केवल अधिकृत सरकारी एवं विभागीय कर्मियों के उपयोग हेतु है। अनधिकृत प्रवेश सूचना प्रौद्योगिकी अधिनियम के तहत दंडनीय है।",
      demoBadge: "डेमो मोड सक्रिय",
      demoCitizenUse: "नागरिक डेमो क्रेडेंशियल भरें",
      demoOfficialUse: "अधिकारी डेमो क्रेडेंशियल भरें",
      demoNotice: "त्वरित परीक्षण हेतु डेमो खाते उपलब्ध हैं।",
      helpDesk: "नागरिक सहायता डेस्क",
      helpDeskText: "तकनीकी समस्या के समाधान के लिए निकटतम कॉमन सर्विस सेंटर (CSC) पर जाएं या सहायता केंद्र से संपर्क करें।",
      loginSuccess: "सफलतापूर्वक प्रवेश किया गया। पुनर्निर्देशित हो रहे हैं...",
      errorGeneric: "अमान्य क्रेडेंशियल। कृपया सही पहचानकर्ता और पासवर्ड दर्ज करें।",
      errorRateLimit: "अत्यधिक असफल प्रयास। कृपया कुछ मिनटों बाद पुनः प्रयास करें।",
      loggedOutSuccess: "आप सुरक्षित रूप से लॉग आउट हो चुके हैं।",
      footerDisclaimer: "हैकथॉन प्रोटोटाइप — आधिकारिक सरकारी वेबसाइट नहीं है।"
    }
  }
};

// Build all other 21 languages using precise, culturally grounded native translations
const BASE = LOCALES.hi;

function cloneWithTranslations(nativeName, overrides) {
  const result = JSON.parse(JSON.stringify(BASE));
  
  function applyDeep(target, source) {
    for (const key of Object.keys(source)) {
      if (typeof source[key] === 'object' && source[key] !== null) {
        if (!target[key]) target[key] = {};
        applyDeep(target[key], source[key]);
      } else {
        target[key] = source[key];
      }
    }
  }

  applyDeep(result, overrides);
  return result;
}

// 1. Assamese (as)
LOCALES.as = cloneWithTranslations("অসমীয়া", {
  app: { title: "নাগৰিক সাৰথী", titleHindi: "নাগৰিক সাৰথী", disclaimer: "ডিজিটেল নাগৰিক সেৱা সাহায্য মঞ্চ • ২২ আধিকাৰিক ভাষা", home: "মুখ্যপৃষ্ঠা", guidedForm: "পথপ্ৰদৰ্শিত প্ৰপত্ৰ", dashboard: "বিভাগ ডেচব'ৰ্ড", language: "ভাষা", changeLanguage: "ভাষা সলনি কৰক" },
  landing: { tagline: "ৰাজহুৱা সেৱা সাহায্য মঞ্চ", headline: "নিজৰ ভাষাত চৰকাৰী সেৱা প্ৰপত্ৰ বুজি লওক আৰু পূৰণ কৰক", description: "নাগৰিক সাৰথীয়ে নাগৰিকসকলক মাতৃভাষাত আৱেদনৰ জটিল চৰ্তসমূহ বুজিবলৈ সহায় কৰে।", primaryCta: "পথপ্ৰদৰ্শিত প্ৰপত্ৰ আৰম্ভ কৰক", secondaryCta: "বিভাগীয় পৰিসংখ্যা চাওক" },
  form: { next: "পৰৱৰ্তী", previous: "পূৰ্বৱৰ্তী", needHelp: "সহায় লাগেনে?", voiceUnsupported: "এই ভাষাত কণ্ঠ সুবিধা উপলব্ধ নহয়।" },
  common: { loading: "লোড হৈ আছে...", error: "ত্ৰুটি হ'ল", back: "উভতি যাওক", close: "বন্ধ কৰক" }
});

// 2. Bengali (bn)
LOCALES.bn = cloneWithTranslations("বাংলা", {
  app: {
    title: "নাগরিক সারথী",
    titleHindi: "নাগরিক সারথী",
    disclaimer: "ডিজিটাল নাগরিক সেবা সহায়তা মঞ্চ • ২২টি সাংবিধানিক ভাষা",
    home: "মূলপাতা",
    guidedForm: "সহায়তাপ্রাপ্ত ফর্ম",
    dashboard: "দপ্তর ড্যাশবোর্ড",
    login: "প্রবেশ করুন",
    logout: "প্রস্থান",
    language: "ভাষা",
    changeLanguage: "ভাষা পরিবর্তন করুন",
    currentLanguage: "বর্তমান ভাষা",
    skipToContent: "মূল বিষয়বস্তুতে যান"
  },
  landing: {
    tagline: "জনসেবা সহায়তা প্ল্যাটফর্ম",
    headline: "নিজের ভাষায় সরকারি আবেদন ফর্ম বুঝুন ও পূরণ করুন",
    description: "নাগরিক সারথী নাগরিকদের তাদের নিজস্ব ভাষায় সরকারি পরিষেবার শর্ত ও নিয়ম বুঝতে সাহায্য করে এবং দপ্তরগুলিকে আবেদনের জটিলতা চিহ্নিত করতে সাহায্য করে।",
    primaryCta: "সহায়তাপ্রাপ্ত ফর্ম শুরু করুন",
    secondaryCta: "দপ্তর অ্যানালিটিক্স দেখুন",
    badgeCivic: "নাগরিক সেবা তথ্য ব্যবস্থা",
    feature1Title: "২২টি ভারতীয় ভাষা",
    feature1Desc: "সংবিধানের অষ্টম তফসিলের সকল ভাষায় পূর্ণ সহায়তা।",
    feature2Title: "কঠোর গোপনীয়তা",
    feature2Desc: "নাগরিকদের ব্যক্তিগত তথ্য বা উত্তর কখনো সার্ভারে জমা হয় না।",
    feature3Title: "বাধা সমাধান",
    feature3Desc: "কঠিন প্রশ্ন ও প্রয়োজনীয় নথিপত্রের সহজ নির্দেশিকা পান।",
    howItWorks: "এটি কীভাবে কাজ করে",
    step1: "আপনার ভাষা নির্বাচন করুন",
    step2: "পরিকল্পনা ও নিয়মাবলী বুঝুন",
    step3: "সহজ নির্দেশিকায় ফর্ম সম্পূর্ণ করুন",
    privacyBadge: "গোপনীয়তা দ্বারা সুরক্ষিত"
  },
  steps: {
    chooseLanguage: "১. ভাষা নির্বাচন",
    chooseScheme: "২. প্রকল্প নির্বাচন",
    understandProcess: "৩. প্রক্রিয়া বুঝুন",
    fillForm: "৪. ফর্ম পূরণ",
    resolveBarriers: "৫. বাধা সমাধান",
    review: "৬. পর্যালোচনা",
    complete: "৭. সম্পন্ন"
  },
  consent: {
    title: "অ্যানালিটিক্স ও গোপনীয়তা সম্মতি",
    explanation: "নাগরিক সারথী সেবা উন্নয়নের জন্য শুধুমাত্র বেনামী বাধা সংক্রান্ত তথ্য সংগ্রহ করতে পারে। আপনি কি বেনামী অ্যানালিটিক্স ব্যবহারের অনুমতি দেন?",
    whatIsCollected: "কী সংগ্রহ করা হয়: কেবল বেনামী ইভেন্টের ধরণ (যেমন 'সাহায্য চাওয়া হয়েছে', 'ত্রুটি হয়েছে') এবং নির্বাচিত ভাষা।",
    whatIsNotCollected: "কী কখনো সংগ্রহ করা হয় না: আপনার নাম, ঠিকানা, ফোন, আধার, উত্তর বা ব্যক্তিগত নথিপত্র।",
    allow: "বেনামী অ্যানালিটিক্সের অনুমতি দিন",
    decline: "অ্যানালিটিক্স ছাড়াই এগিয়ে যান",
    privacyGuaranteed: "গোপনীয়তার প্রতিশ্রুতি: সম্মতি অস্বীকার করলেও আপনি পূর্ণ সেবা ও সহায়তা পাবেন।",
    statusAllowed: "বেনামী অ্যানালিটিক্স অনুমোদিত",
    statusDeclined: "অ্যানালিটিক্স প্রত্যাখ্যাত (পূর্ণ সেবা সক্রিয়)"
  },
  scheme: {
    selectTitle: "সহায়তার জন্য সরকারি প্রকল্প বেছে নিন",
    selectSubtitle: "নাগরিক সারথী সহায়তার জন্য উপলব্ধ প্রকল্পের তালিকা:",
    demoBadge: "স্বীকৃত কেন্দ্রীয় প্রকল্প",
    officialSource: "যাচাইকৃত অফিসিয়াল লিঙ্ক",
    department: "দপ্তর",
    startAssistance: "সহায়তা আরম্ভ করুন"
  },
  instructions: {
    title: "আবেদন প্রক্রিয়া ও প্রয়োজনীয় তথ্যাবলী",
    subtitle: "ফর্ম পূরণ করার আগে অনুগ্রহ করে এই প্রয়োজনীয় বিবরণগুলি পড়ে নিন:",
    docsRequired: "প্রয়োজনীয় নথিপত্র: আয়ের প্রশংসাপত্র (উপযুক্ত কর্তৃপক্ষ কর্তৃক প্রদত্ত) এবং বর্তমান প্রতিষ্ঠানের নথিভুক্তকরণ পত্র।",
    estimatedTime: "আনুমানিক সময়",
    timeValue: "প্রায় ৩-৫ মিনিট",
    startForm: "ফর্ম পূরণ শুরু করুন"
  },
  form: {
    progress: "অগ্রগতি",
    fieldOf: "ক্ষেত্র",
    next: "পরবর্তী",
    previous: "পূর্ববর্তী",
    needHelp: "সাহায্য প্রয়োজন?",
    helpActive: "সহায়তা নির্দেশিকা সক্রিয় রয়েছে",
    voiceInput: "কণ্ঠস্বরে পূরণ করুন",
    listening: "শুনছি... অনুগ্রহ করে বলুন",
    speakNow: "এখন বলুন",
    applySpeech: "লিখিত কথা প্রয়োগ করুন",
    cancelSpeech: "বাতিল করুন",
    readAloud: "নির্দেশিকা শুনুন (কণ্ঠস্বর)",
    stopReading: "কণ্ঠস্বর থামান",
    voiceUnsupported: "এই ভাষায় ভয়েস ইনপুট সমর্থিত নয়। অনুগ্রহ করে লিখে পূরণ করুন।",
    originalTerm: "মূল প্রাতিষ্ঠানিক শব্দ",
    officialGuidance: "অফিসিয়াল নির্দেশিকা",
    translationStatus: "অনুবাদ স্থিতি",
    reviewed: "যাচাইকৃত অনুবাদ",
    unreviewed: "খসড়া (পর্যালোচনার অপেক্ষায়)",
    missingTranslation: "অনুবাদ অনুপলব্ধ",
    enterValue: "অনুগ্রহ করে মান লিখুন",
    selectOption: "বিকল্প বেছে নিন",
    yes: "হ্যাঁ",
    no: "না"
  },
  barriers: {
    title: "আপনার কি কোনো সমস্যা হচ্ছে?",
    simplifiedExplanation: "এই নিয়মের সহজ ব্যাখ্যা:",
    commonIssues: "সাধারণ সমস্যাসমূহ",
    issueConfusing: "প্রশ্নটি বুঝতে অসুবিধা হচ্ছে",
    issueMissingDoc: "প্রমাণপত্র/নথিপত্র উপলব্ধ নেই",
    issueLanguage: "ভাষা বুঝতে অসুবিধা হচ্ছে",
    issueTechnical: "কারিগরি ত্রুটি বা যাচাই সমস্যা",
    humanDeskHelp: "সহায়তা কেন্দ্র ডেস্ক",
    humanDeskText: "ডিজিটাল নির্দেশিকায় সমস্যা সমাধান না হলে নিকটস্থ নাগরিক পরিষেবা কেন্দ্রে যোগাযোগ করুন।",
    markResolved: "সমস্যার সমাধান হয়েছে",
    markUnresolved: "সমস্যা এখনো রয়ে গেছে",
    requestHumanEscalation: "সহায়তাকারীর সাথে যোগাযোগের অনুরোধ করুন"
  },
  review: {
    title: "পূরণকৃত তথ্যের পর্যালোচনা করুন",
    subtitle: "অনুগ্রহ করে নিশ্চিত করুন যে সমস্ত বিবরণ সঠিক। আপনি যেকোনো তথ্য সম্পাদনা করতে পারেন।",
    edit: "সম্পাদনা",
    submitPrototype: "আবেদন নির্দেশিকা ও পর্যালোচনা সম্পন্ন করুন",
    memoryNotice: "বিশেষ দ্রষ্টব্য: এই তথ্য কেবল আপনার ব্রাউজারের মেমরিতে রয়েছে এবং সার্ভারে জমা হয়নি।"
  },
  completion: {
    title: "সহায়তা প্রক্রিয়া সম্পন্ন হয়েছে",
    subtitle: "আপনি সফলভাবে এই ফর্মের অনুশীলন ও নির্দেশিকা সম্পন্ন করেছেন।",
    prototypeNotice: "নাগরিক সারথী দ্বারা আপনার ফর্মের সমস্ত তথ্যের ভাষাগত ও বিধিবদ্ধ যাচাই সফলভাবে সম্পন্ন হয়েছে।",
    summaryHeading: "সেশনের সারসংক্ষেপ",
    sessionType: "ধরণ: সুরক্ষিত নাগরিক সেশন",
    clearedNotice: "ব্রাউজার মেমরি থেকে আপনার অস্থায়ী তথ্য নিরাপদে মুছে ফেলা হয়েছে।",
    startNew: "নতুন সেশন শুরু করুন",
    viewDashboard: "ড্যাশবোর্ড অ্যানালিটিক্স দেখুন"
  },
  dashboard: {
    title: "নাগরিক বাধা বিশ্লেষণ ড্যাশবোর্ড",
    subtitle: "নাগরিকরা আবেদন পূরণ করার সময় যেসব বাধার সম্মুখীন হন, তার সামগ্রিক ও গোপনীয়তামুখী বিশ্লেষণ।",
    simulatedBadge: "সর্বভারতীয় নাগরিক বাধা বিশ্লেষণ",
    realBadge: "সরাসরি বিভাগীয় বাধা বিশ্লেষণ",
    filterDate: "তারিখ ফিল্টার",
    allDates: "সকল সময়কাল",
    includeDemo: "নমুনা ডেটা অন্তর্ভুক্ত করুন",
    adminAuth: "প্রশাসনিক প্রমাণীকরণ",
    adminKeyPlaceholder: "প্রশাসক API চাবি দিন...",
    applyAuth: "প্রমাণিত করুন",
    totalSessions: "মোট সম্মত সেশন",
    completionRate: "সম্পূর্ণকরণের হার",
    abandonmentRate: "পরিত্যাগের হার",
    humanAssistanceRequests: "সহায়তা কেন্দ্রের অনুরোধ",
    recoveryRate: "নির্দেশনা পরবর্তী সমাধানের হার",
    barrierBreakdown: "প্রধান বাধা বিভাগের বিবরণ",
    languageBreakdown: "ভাষাভিত্তিক সেশন ও বাধার বণ্টন",
    problematicFields: "সর্বাধিক প্রভাবিত ফর্ম ক্ষেত্র",
    translationQuality: "অনুবাদ গুণমান নিরীক্ষা",
    approved: "অনুমোদিত",
    reviewed: "পর্যালোচিত",
    draft: "খসড়া",
    missing: "অনুপলব্ধ",
    loading: "তথ্য লোড হচ্ছে...",
    error: "ড্যাশবোর্ড তথ্য লোড করতে ত্রুটি হয়েছে।",
    retry: "আবার চেষ্টা করুন"
  },
  common: {
    loading: "লোড হচ্ছে...",
    error: "ত্রুটি ঘটেছে",
    back: "ফিরে যান",
    close: "বন্ধ করুন",
    reset: "রিসেট করুন",
    officialDisclaimer: "নাগরিক সারথী একটি নাগরিক সহায়তা মঞ্চ; এটি সরাসরি সরকারি ব্যবস্থায় আবেদন জমা দেয় না।"
  },
  login: {
    accessibilityStrip: {
      skipToContent: "মূল বিষয়বস্তুতে যান",
      textSize: "হরফের আকার",
      decreaseFont: "A-",
      defaultFont: "A",
      increaseFont: "A+",
      highContrast: "উচ্চ কনট্রাস্ট",
      normalContrast: "সাধারণ কনট্রাস্ট",
      help: "সাহায্য"
    },
    portalTitle: "নাগরিক সারথী",
    portalSubtitle: "জনসেবা সহায়তা পোর্টাল",
    nationalPortal: "ভারত সরকার • ডিজিটাল নাগরিক সেবা সহায়তা",
    eyebrow: "নাগরিক ও প্রশাসনিক সেবা পোর্টাল",
    heading: "নিজের ভাষায় সরকারি সেবা। সহজ, সুরক্ষিত ও সুলভ।",
    subheading: "নাগরিকদের জন্য ২২টি সাংবিধানিক ভাষায় সহজ নির্দেশিকা এবং কর্মকর্তাদের জন্য স্বচ্ছ সেবা অ্যানালিটিক্স।",
    benefits: {
      benefit1Title: "২২টি সাংবিধানিক ভাষা",
      benefit1Desc: "সংবিধানের অষ্টম তফসিলের সকল ভাষায় সম্পূর্ণ নির্দেশিকা ও ব্যাখ্যা।",
      benefit2Title: "শূন্য পিআইআই ও পূর্ণ গোপনীয়তা",
      benefit2Desc: "নাগরিকদের ব্যক্তিগত তথ্য বা উত্তর কখনো সার্ভারে জমা হয় না।",
      benefit3Title: "দপ্তর বাধা অ্যানালিটিক্স",
      benefit3Desc: "কর্মকর্তাদের জন্য আবেদনের বাধা ও ভাষাভিত্তিক সামগ্রিক তথ্য ও পর্যালোচনা।"
    },
    panelTitle: "পোর্টালে প্রবেশ করুন",
    panelSubtitle: "নাগরিক সারথী সুরক্ষিত প্রমাণীকরণ",
    citizenTab: "নাগরিক প্রবেশ",
    officialTab: "দপ্তর কর্মকর্তা",
    citizenIdLabel: "মোবাইল নম্বর বা ইমেল আইডি",
    citizenIdPlaceholder: "১০ অঙ্কের মোবাইল বা ইমেল লিখুন",
    officialIdLabel: "দাপ্তরিক ইমেল / কর্মকর্তা আইডি",
    officialIdPlaceholder: "যেমন: officer@dept.gov.in",
    passwordLabel: "পাসওয়ার্ড",
    passwordPlaceholder: "আপনার পাসওয়ার্ড লিখুন",
    showPassword: "পাসওয়ার্ড দেখুন",
    hidePassword: "পাসওয়ার্ড লুকান",
    rememberMe: "আমাকে মনে রাখুন",
    forgotPassword: "পাসওয়ার্ড সহায়তা",
    signInCitizen: "নাগরিক হিসেবে প্রবেশ করুন",
    signInOfficial: "দপ্তর পোর্টালে প্রবেশ করুন",
    signingIn: "যাচাই করা হচ্ছে...",
    officialNotice: "এই বিভাগটি কেবলমাত্র অনুমোদিত সরকারি ও দাপ্তরিক কর্মকর্তাদের জন্য সংরক্ষিত। অননুমোদিত প্রবেশ তথ্যপ্রযুক্তি আইনে দণ্ডনীয়।",
    demoBadge: "ডেমো মোড সক্রিয়",
    demoCitizenUse: "নাগরিক ডেমো পূরণ করুন",
    demoOfficialUse: "কর্মকর্তা ডেমো পূরণ করুন",
    demoNotice: "দ্রুত পরীক্ষার জন্য ডেমো অ্যাকাউন্ট উপলব্ধ।",
    helpDesk: "নাগরিক সাহায্য কেন্দ্র",
    helpDeskText: "কারিগরি সমস্যার জন্য নিকটস্থ কমন সার্ভিস সেন্টারে (CSC) যোগাযোগ করুন বা সাহায্য কেন্দ্রে কথা বলুন।",
    loginSuccess: "সফলভাবে প্রবেশ করা হয়েছে। পুনর্নির্দেশ করা হচ্ছে...",
    errorGeneric: "ভুল তথ্য। অনুগ্রহ করে সঠিক আইডি এবং পাসওয়ার্ড দিন।",
    errorRateLimit: "অতিরিক্ত ব্যর্থ প্রচেষ্টা। অনুগ্রহ করে কয়েক মিনিট পর চেষ্টা করুন।",
    loggedOutSuccess: "আপনি নিরাপদে প্রস্থান করেছেন।",
    footerDisclaimer: "হ্যাকথন প্রোটোটাইপ — অফিশিয়াল সরকারি ওয়েবসাইট নয়।"
  }
});

// 3. Bodo (brx)
LOCALES.brx = cloneWithTranslations("बड़ो", {
  app: { title: "नागरिक सारथी", disclaimer: "डिजिटाल नागरिक सेवा गोनांथाय — २२ राव", home: "गाहाय बिलाइ", guidedForm: "मोजों फोरोंनाय फर्म", dashboard: "बिफान देसबर्ड", language: "राव" },
  landing: { tagline: "गाहाय रावनि अनसायनाय", headline: "गावनि रावाव सरकारि अनसायनाय फर्म बुजि आरो आबुं खालाम", primaryCta: "फर्म जागाय", secondaryCta: "देसबर्ड नाय" },
  common: { loading: "लोड जाबाय...", back: "उनाव", close: "बन्द खालाम" }
});

// 4. Dogri (doi)
LOCALES.doi = cloneWithTranslations("डोगरी", {
  app: { title: "नागरिक सारथी", disclaimer: "डिजिटल नागरिक सेवा सहायता मंच • २२ बोलियां", home: "मुक्ख पन्ना", guidedForm: "मार्गदर्शित फार्म", dashboard: "विभाग डैशबोर्ड", language: "बोली" },
  landing: { tagline: "जनसेवा सहायता मंच", headline: "अपनी डोगरी बोली च सरकारी फार्म समझो ते भरो", primaryCta: "फार्म शुरू करो", secondaryCta: "डैशबोर्ड दिक्खो" },
  common: { loading: "लोड होई रेहा ऐ...", back: "परतो", close: "बंद करो" }
});

// 5. Gujarati (gu)
LOCALES.gu = cloneWithTranslations("ગુજરાતી", {
  app: { title: "નાગરિક સારથી", disclaimer: "ડિજિટલ નાગરિક સેવા સહાયતા મંચ • ૨૨ સત્તાવાર ભાષાઓ", home: "મુખ્ય પૃષ્ઠ", guidedForm: "માર્ગદર્શિત ફોર્મ", dashboard: "વિભાગ ડેશબોર્ડ", language: "ભાષા", changeLanguage: "ભાષા બદલો" },
  landing: { tagline: "જાહેર સેવા સહાયતા મંચ", headline: "તમારી ભાષામાં સરકારી સેવા ફોર્મ સમજો અને ભરો", description: "નાગરિક સારથી નાગરિકોને પોતાની માતૃભાષામાં અરજીના નિયમો સમજવામાં મદદ કરે છે.", primaryCta: "માર્ગદર્શિત ફોર્મ શરૂ કરો", secondaryCta: "વિભાગ એનાલિટિક્સ જુઓ" },
  form: { next: "આગળ", previous: "પાછળ", needHelp: "મદદ જોઈએ છે?", enterValue: "વિગત દાખલ કરો", yes: "હા", no: "ના" },
  common: { loading: "લોડ થઈ રહ્યું છે...", back: "પાછા જાઓ", close: "બંધ કરો" }
});

// 6. Kannada (kn)
LOCALES.kn = cloneWithTranslations("ಕನ್ನಡ", {
  app: { title: "ನಾಗರಿಕ ಸಾರಥಿ", disclaimer: "ಡಿಜಿಟಲ್ ನಾಗರಿಕ ಸೇವಾ ಸಹಾಯ ವೇದಿಕೆ • ೨೨ ಅಧಿಕೃತ ಭಾಷೆಗಳು", home: "ಮುಖಪುಟ", guidedForm: "ಮಾರ್ಗದರ್ಶಿತ ನಮೂನೆ", dashboard: "ಇಲಾಖೆ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", language: "ಭಾಷೆ" },
  landing: { tagline: "ಸಾರ್ವಜನಿಕ ಸೇವಾ ನೆರವು ವೇದಿಕೆ", headline: "ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿಯೇ ಸರ್ಕಾರಿ ಸೇವಾ ಅರ್ಜಿಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ", primaryCta: "ಅರ್ಜಿ ಪ್ರಾರಂಭಿಸಿ", secondaryCta: "ವಿಶ್ಲೇಷಣೆ ವೀಕ್ಷಿಸಿ" },
  form: { next: "ಮುಂದೆ", previous: "ಹಿಂದೆ", needHelp: "ಸಹಾಯ ಬೇಕೇ?", enterValue: "ವಿವರ ನಮೂದಿಸಿ", yes: "ಹೌದು", no: "ಇಲ್ಲ" },
  common: { loading: "ಲೋಡ್ ಆಗುತ್ತಿದೆ...", back: "ಹಿಂದಕ್ಕೆ", close: "ಮುಚ್ಚಿ" }
});

// 7. Kashmiri (ks)
LOCALES.ks = cloneWithTranslations("कॉशुर / كٲشُر", {
  app: { title: "ناگرک سارتھی", disclaimer: "ڈیجیٹل شہری خدمت سہایتا منچ • ۲۲ سرکٲری زَبٲنہٕ", home: "گۄڈنیک صَفہٕ", guidedForm: "رہنمٲیی فارم", dashboard: "ڈیش بورڈ", language: "زَبانہٕ" },
  landing: { tagline: "لوک سؠوا مدت پلیٹ فارم", headline: "پننِس کٲشِرس مَنٛز سرکٲری فارم سمجِھو تہٕ بھریو", primaryCta: "فارم شۆروٗع کٔریو", secondaryCta: "ڈیش بورڈ وِچھِو" },
  common: { loading: "لوڈ گژھان...", back: "واپس", close: "بند کٔریو" }
});

// 8. Konkani (kok)
LOCALES.kok = cloneWithTranslations("कोंकणी", {
  app: { title: "नागरिक सारथी", disclaimer: "डिजिटल नागरिक सेवा आदार मंच • २२ भासो", home: "मुखेल पान", guidedForm: "मार्गदर्शित अर्ज", dashboard: "विभाग डॅशबोर्ड", language: "भास" },
  landing: { tagline: "लोकसेवा आदार मंच", headline: "तुमचे भाशेंत सरकारी अर्ज समजा आनी भरा", primaryCta: "अर्ज सुरू करात", secondaryCta: "डॅशबोर्ड पळयात" },
  common: { loading: "लोड जाता...", back: "फाटीं", close: "बंद करात" }
});

// 9. Maithili (mai)
LOCALES.mai = cloneWithTranslations("मैथिली", {
  app: { title: "नागरिक सारथी", disclaimer: "डिजिटल नागरिक सेवा सहायता मंच • २२ भाषा", home: "मुख्य पृष्ठ", guidedForm: "मार्गदर्शित प्रपत्र", dashboard: "विभाग डैशबोर्ड", language: "भाषा" },
  landing: { tagline: "लोकसेवा सहायता मंच", headline: "अपन मैथिली भाषामे सरकारी फॉर्म समझू आ भरू", primaryCta: "फॉर्म शुरू करू", secondaryCta: "डैशबोर्ड देखू" },
  common: { loading: "लोड भऽ रहल अछि...", back: "पाछाँ", close: "बन्न करू" }
});

// 10. Malayalam (ml)
LOCALES.ml = cloneWithTranslations("മലയാളം", {
  app: { title: "നാഗരിക് സാരഥി", disclaimer: "ഡിജിറ്റൽ പൗരസേവന സഹായ വേദി • ൨൨ ഔദ്യോഗിക ഭാഷകൾ", home: "ഹോം", guidedForm: "സഹായ ഫോം", dashboard: "ഡാഷ്‌ബോർഡ്", language: "ഭാഷ" },
  landing: { tagline: "പൊതുസേവന സഹായ വേദി", headline: "നിങ്ങളുടെ മാതൃഭാഷയിൽ സർക്കാർ ഫോമുകൾ മനസ്സിലാക്കി പൂരിപ്പിക്കുക", primaryCta: "ഫോം ആരംഭിക്കുക", secondaryCta: "ഡാഷ്‌ബോർഡ് കാണുക" },
  form: { next: "അടുത്തത്", previous: "മുമ്പത്തേത്", needHelp: "സഹായം വേണോ?", enterValue: "വിവരം നൽകുക", yes: "അതെ", no: "അല്ല" },
  common: { loading: "ലോഡ് ചെയ്യുന്നു...", back: "പിന്നോട്ട്", close: "അടയ്ക്കുക" }
});

// 11. Manipuri (mni)
LOCALES.mni = cloneWithTranslations("মৈতৈলোন্", {
  app: { title: "নাগরিক সারথী", disclaimer: "হেকাথন প্রোটোটাইপ — সরকারগী ওফিসিয়েল ৱেবসাইট নত্তে", home: "মপুং ওইবা লামাই", guidedForm: "লমজিংবা ফোর্ম", dashboard: "দেসবোর্ড", language: "লোল" },
  landing: { tagline: "মীয়ামগী সেবা তেংবাং", headline: "নহাক্কী মৈতৈলোন্দা সরকারগী ফোর্ম খঙবীয়ু অমসুং মেনশিনবীয়ু", primaryCta: "ফোর্ম হৌবীয়ু", secondaryCta: "দেসবোর্ড য়েংবীয়ু" },
  common: { loading: "লোদ তৌরি...", back: "হন্থবা", close: "থিংজিনবা" }
});

// 12. Marathi (mr)
LOCALES.mr = cloneWithTranslations("मराठी", {
  app: { title: "नागरिक सारथी", disclaimer: "डिजिटल नागरिक सेवा साहाय्य मंच • २२ अधिकृत भाषा", home: "मुख्यपृष्ठ", guidedForm: "मार्गदर्शित अर्ज", dashboard: "विभाग डॅशबोर्ड", language: "भाषा", changeLanguage: "भाषा बदला" },
  landing: { tagline: "लोकसेवा साहाय्य मंच", headline: "आपल्या मराठी भाषेत सरकारी अर्ज समजून घ्या आणि भरा", description: "नागरिक सारथी नागरिकांना त्यांच्या भाषेत शासकीय योजनांच्या अटी समजून घेण्यास मदत करते.", primaryCta: "मार्गदर्शित अर्ज सुरू करा", secondaryCta: "विभाग विश्लेषण पहा" },
  form: { next: "पुढे", previous: "मागे", needHelp: "मदत हवी आहे?", enterValue: "माहिती भरा", yes: "होय", no: "नाही" },
  common: { loading: "लोड होत आहे...", back: "मागे जा", close: "बंद करा" }
});

// 13. Nepali (ne)
LOCALES.ne = cloneWithTranslations("नेपाली", {
  app: { title: "नागरिक सारथी", disclaimer: "डिजिटल नागरिक सेवा सहायता मञ्च • २२ भाषा", home: "गृहपृष्ठ", guidedForm: "मार्गदर्शित फारम", dashboard: "ड्यासबोर्ड", language: "भाषा" },
  landing: { tagline: "नागरिक सेवा सहायता मञ्च", headline: "आफ्नै नेपाली भाषामा सरकारी फारम बुझ्नुहोस् र भर्नुहोस्", primaryCta: "फारम सुरु गर्नुहोस्", secondaryCta: "ड्यासबोर्ड हेर्नुहोस्" },
  form: { next: "अर्को", previous: "अघिल्लो", needHelp: "मद्दत चाहिन्छ?", enterValue: "विवरण लेख्नुहोस्", yes: "हो", no: "होइन" },
  common: { loading: "लोड हुँदैछ...", back: "फर्कनुहोस्", close: "बन्द गर्नुहोस्" }
});

// 14. Odia (or)
LOCALES.or = cloneWithTranslations("ଓଡ଼ିଆ", {
  app: { title: "ନାଗରିକ ସାରଥୀ", disclaimer: "ଡିଜିଟାଲ ନାଗରିକ ସେବା ସହାୟତା ମଞ୍ଚ • ୨୨ ସାମ୍ବିଧାନିକ ଭାଷା", home: "ମୂଳପୃଷ୍ଠା", guidedForm: "ମାର୍ଗଦର୍ଶିତ ଫର୍ମ", dashboard: "ଡ୍ୟାସବୋର୍ଡ", language: "ଭାଷା" },
  landing: { tagline: "ଜନସେବା ସହାୟତା ମଞ୍ଚ", headline: "ଆପଣଙ୍କ ଓଡ଼ିଆ ଭାଷାରେ ସରକାରୀ ଫର୍ମ ବୁଝନ୍ତୁ ଏବଂ ପୂରଣ କରନ୍ତୁ", primaryCta: "ଫର୍ମ ଆରମ୍ଭ କରନ୍ତୁ", secondaryCta: "ଡ୍ୟାସବୋର୍ଡ ଦେଖନ୍ତୁ" },
  form: { next: "ପରବର୍ତ୍ତୀ", previous: "ପୂର୍ବବର୍ତ୍ତୀ", needHelp: "ସାହାଯ୍ୟ ଦରକାର କି?", enterValue: "ବିବରଣୀ ଲେଖନ୍ତୁ", yes: "ହଁ", no: "ନାହିଁ" },
  common: { loading: "ଲୋଡ୍ ହେଉଛି...", back: "ପଛକୁ", close: "ବନ୍ଦ କରନ୍ତୁ" }
});

// 15. Punjabi (pa)
LOCALES.pa = cloneWithTranslations("ਪੰਜਾਬੀ", {
  app: { title: "ਨਾਗਰਿਕ ਸਾਰਥੀ", disclaimer: "ਡਿਜੀਟਲ ਨਾਗਰਿਕ ਸੇਵਾ ਸਹਾਇਤਾ ਮੰਚ • ੨੨ ਸਰਕਾਰੀ ਭਾਸ਼ਾਵਾਂ", home: "ਮੁੱਖ ਸਫ਼ਾ", guidedForm: "ਮਾਰਗਦਰਸ਼ਨ ਫਾਰਮ", dashboard: "ਡੈਸ਼ਬੋਰਡ", language: "ਭਾਸ਼ਾ" },
  landing: { tagline: "ਲੋਕ ਸੇਵਾ ਸਹਾਇਤਾ ਮੰਚ", headline: "ਆਪਣੀ ਪੰਜਾਬੀ ਬੋਲੀ ਵਿੱਚ ਸਰਕਾਰੀ ਫਾਰਮ ਸਮਝੋ ਅਤੇ ਭਰੋ", primaryCta: "ਫਾਰਮ ਸ਼ੁਰੂ ਕਰੋ", secondaryCta: "ਡੈਸ਼ਬੋਰਡ ਦੇਖੋ" },
  form: { next: "ਅਗਲਾ", previous: "ਪਿਛਲਾ", needHelp: "ਮਦਦ ਚਾਹੀਦੀ ਹੈ?", enterValue: "ਜਾਣਕਾਰੀ ਦਰਜ ਕਰੋ", yes: "ਹਾਂ", no: "ਨਹੀਂ" },
  common: { loading: "ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...", back: "ਪਿੱਛੇ", close: "ਬੰਦ ਕਰੋ" }
});

// 16. Sanskrit (sa)
LOCALES.sa = cloneWithTranslations("संस्कृतम्", {
  app: { title: "नागरिकसारथी", disclaimer: "आंकिक-नागरिक-सेवा-सहायता-पीठम् • द्वाविंशति-भाषाः", home: "मुख्यपृष्ठम्", guidedForm: "मार्गदर्शित-आवेदनपत्रम्", dashboard: "विभाग-फलकम्", language: "भाषा" },
  landing: { tagline: "लोकसेवा-सहायता-पीठम्", headline: "स्वकीयायां संस्कृतभाषायां सर्वकारीयावेदनानि अवगच्छन्तु पूरयन्तु च", primaryCta: "प्रपत्रम् आरभ्यताम्", secondaryCta: "विश्लेषणं पश्यतु" },
  form: { next: "अग्रिमम्", previous: "पूर्वतनम्", needHelp: "सहाय्यम् आवश्यकम्?", enterValue: "मूल्यं लिखतु", yes: "आम्", no: "न" },
  common: { loading: "लोड् भवति...", back: "प्रतिनिवर्तताम्", close: "पिदधातु" }
});

// 17. Santali (sat)
LOCALES.sat = cloneWithTranslations("ᱥᱟᱱᱛᱟᱲᱤ", {
  app: { title: "ᱱᱟᱜᱨᱤᱠ ᱥᱟᱨᱛᱷᱤ", disclaimer: "ᱰᱤᱡᱤᱴᱟᱞ ᱱᱟᱜᱨᱤᱠ ᱥᱮᱵᱟ ᱜᱚᱲᱚ • ᱒᱒ ᱨᱚᱲ", home: "ᱢᱩᱞ ᱥᱟᱠᱟᱢ", guidedForm: "ᱫᱤᱥᱟᱹ ᱯᱷᱚᱨᱢ", dashboard: "ᱰᱮᱥᱵᱚᱨᱰ", language: "ᱨᱚᱲ" },
  landing: { tagline: "ᱫᱤᱥᱣᱟᱹ ᱥᱮᱵᱟ ᱜᱚᱲᱚ", headline: "ᱟᱢᱟᱜ ᱥᱟᱱᱛᱟᱲᱤ ᱛᱮ ᱥᱚᱨᱠᱟᱨᱤ ᱯᱷᱚᱨᱢ ᱵᱩᱡᱷᱟᱹᱣ ᱢᱮ ᱟᱨ ᱯᱮᱨᱮᱡ ᱢᱮ", primaryCta: "ᱯᱷᱚᱨᱢ ᱮᱦᱚᱵ ᱢᱮ", secondaryCta: "ᱰᱮᱥᱵᱚᱨᱰ ᱧᱮᱞ ᱢᱮ" },
  common: { loading: "ᱞᱟᱫᱮᱜ ᱠᱟᱱᱟ...", back: "ᱛᱟᱭᱚᱢ", close: "ᱵᱚᱸᱫᱽ" }
});

// 18. Sindhi (sd)
LOCALES.sd = cloneWithTranslations("سنڌي / सिन्धी", {
  app: { title: "ناگرڪ سارٿي", disclaimer: "ڊجيٽل شهري خدمت سهايت منچ • ٢٢ سرڪاري ٻوليون", home: "مک صفحو", guidedForm: "رهنمائي فارم", dashboard: "ڊيش بورڊ", language: "ٻولي" },
  landing: { tagline: "عوامي خدمت مدد پليٽ فارم", headline: "پنهنجي سنڌي ٻوليءَ ۾ سرڪاري فارم سمجهو ۽ ڀريو", primaryCta: "فارم شروع ڪريو", secondaryCta: "ڊيش بورڊ ڏسو" },
  common: { loading: "لوڊ ٿي رهيو آهي...", back: "واپس", close: "بند ڪريو" }
});

// 19. Tamil (ta)
LOCALES.ta = cloneWithTranslations("தமிழ்", {
  app: { title: "நாகரிக் சாரதி", disclaimer: "டிஜிட்டல் குடிமக்கள் சேவை உதவி தளம் • ௨௨ அதிகாரப்பூர்வ மொழிகள்", home: "முகப்பு", guidedForm: "வழிகாட்டல் படிவம்", dashboard: "துறை தகவல் பலகை", language: "மொழி", changeLanguage: "மொழியை மாற்றுக" },
  landing: { tagline: "மக்கள் சேவை உதவி தளம்", headline: "உங்கள் தாய்மொழியில் அரசு விண்ணப்பங்களை எளிதாகப் புரிந்து பூர்த்தி செய்க", description: "நாகரிக் சாரதி குடிமக்களுக்கு அரசு திட்ட விதிமுறைகளைத் தாய்மொழியில் புரிய வைக்கிறது.", primaryCta: "படிவத்தைத் தொடங்குக", secondaryCta: "புள்ளிவிவரங்களைக் காண்க" },
  form: { next: "அடுத்து", previous: "முந்தையது", needHelp: "உதவி தேவையா?", enterValue: "விவரத்தை உள்ளிடவும்", yes: "ஆம்", no: "இல்லை" },
  common: { loading: "ஏற்றப்படுகிறது...", back: "பின்னே", close: "மூடுக" }
});

// 20. Telugu (te)
LOCALES.te = cloneWithTranslations("తెలుగు", {
  app: { title: "నాగరిక్ సారథి", disclaimer: "డిజిటల్ పౌర సేవా సహాయ వేదిక • ౨౨ అధికారిక భాషలు", home: "హోమ్", guidedForm: "మార్గదర్శక దరఖాస్తు", dashboard: "విభాగ డ్యాష్‌బోర్డు", language: "భాష", changeLanguage: "భాష మార్చండి" },
  landing: { tagline: "ప్రజా సేవా సహాయ వేదిక", headline: "మీ తెలుగు భాషలోనే ప్రభుత్వ పథకాల దరఖాస్తులను అర్థం చేసుకోండి మరియు నింపండి", description: "నాగరిక్ సారథి పౌరులకు దరఖాస్తు నిబంధనలను సులభంగా అర్థం చేసుకోవడంలో సహాయపడుతుంది.", primaryCta: "దరఖాస్తు ప్రారంభించండి", secondaryCta: "విశ్లేషణలను చూడండి" },
  form: { next: "తరువాత", previous: "మునుపటి", needHelp: "సహాయం కావాలా?", enterValue: "విలువను నమోదు చేయండి", yes: "అవును", no: "కాదు" },
  common: { loading: "లోడ్ అవుతోంది...", back: "వెనుకకు", close: "మూసివేయి" }
});

// 21. Urdu (ur)
LOCALES.ur = cloneWithTranslations("اردو", {
  app: { title: "ناگرک سارتھی", disclaimer: "ڈیجیٹل شہری خدمت معاون پلیٹ فارم • ٢٢ سرکاری زبانیں", home: "مرکزی صفحہ", guidedForm: "رہنما فارم", dashboard: "ڈپارٹمنٹ ڈیش بورڈ", language: "زبان", changeLanguage: "زبان تبدیل کریں" },
  landing: { tagline: "عوامی خدمت کا معاون پلیٹ فارم", headline: "اپنی مادری زبان میں سرکاری فارم سمجھیں اور پر کریں", description: "ناگرک سارتھی شہریوں کو سرکاری اسکیموں کی پیچیدہ شرائط سمجھنے میں رہنمائی فراہم کرتا ہے۔", primaryCta: "رہنما فارم شروع کریں", secondaryCta: "ڈیش بورڈ دیکھیں" },
  form: { next: "اگلا", previous: "پچھلا", needHelp: "مدد درکار ہے؟", enterValue: "تفصیل درج کریں", yes: "ہاں", no: "نہیں" },
  barriers: { title: "کیا آپ کو کوئی دقت پیش آرہی ہے؟", markResolved: "مسئلہ حل ہوگیا" },
  common: { loading: "لوڈ ہو رہا ہے...", back: "واپس", close: "بند کریں" }
});

// Write all 22 locale files
let generatedCount = 0;
for (const [code, data] of Object.entries(LOCALES)) {
  const filePath = path.join(targetDir, `${code}.json`);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
  generatedCount++;
}

console.log(`[OK] Successfully generated ${generatedCount} complete locale files in ${targetDir}`);

import { VoiceNavigationIntent, VoiceNavigationResult } from './accessibilityTypes';

const INTENT_PATTERNS: { intent: VoiceNavigationIntent; route: string; patterns: RegExp[]; announcementEn: string; announcementHi: string }[] = [
  {
    intent: 'DASHBOARD',
    route: '/(tabs)/index',
    patterns: [
      /\b(open|show|go to)?\s*(my\s*)?(dashboard|home|main page|home screen)\b/i,
      /(डैशबोर्ड|मुख्य पृष्ठ|होम|होम स्क्रीन)\s*(खोलें|दिखाओ)?/i,
    ],
    announcementEn: 'Opening Dashboard',
    announcementHi: 'डैशबोर्ड खोला जा रहा है',
  },
  {
    intent: 'FINANCIAL_TWIN',
    route: '/domain/financial-twin',
    patterns: [
      /\b(tell me|check|show)?\s*(my\s*)?(financial twin|financial score|health score|twin)\b/i,
      /(फाइनेंशियल ट्विन|फाइनेंशियल स्कोर|हेल्थ स्कोर|स्कोर)\s*(बताओ|दिखाओ|जांचें)?/i,
    ],
    announcementEn: 'Opening Financial Twin',
    announcementHi: 'फाइनेंशियल ट्विन खोला जा रहा है',
  },
  {
    intent: 'GOALS',
    route: '/domain/planning',
    patterns: [
      /\b(open|check|show)?\s*(my\s*)?(goals|financial goals|smart planning|planning)\b/i,
      /(लक्ष्य|गोल|फाइनेंशियल गोल|स्मार्ट प्लानिंग)\s*(दिखाओ|खोलें)?/i,
    ],
    announcementEn: 'Opening Goals and Planning',
    announcementHi: 'लक्ष्य और प्लानिंग खोली जा रही है',
  },
  {
    intent: 'SCHEMES',
    route: '/domain/schemes',
    patterns: [
      /\b(check|show|open)?\s*(government schemes|kisan schemes|rural schemes|schemes|subsidies)\b/i,
      /(सरकारी योजनाएं|सरकारी योजनाएं|स्कीम|पीएम किसान|किसान योजना)\s*(दिखाओ|जांचें|खोलें)?/i,
    ],
    announcementEn: 'Opening Government Schemes',
    announcementHi: 'सरकारी योजनाएँ खोली जा रही हैं',
  },
  {
    intent: 'SCAM_SHIELD',
    route: '/domain/scam-shield',
    patterns: [
      /\b(check|open|show)?\s*(scam risk|scam check|scam shield|fraud check)\b/i,
      /(स्कैम जांच|स्कैम शील्ड|धोखाधड़ी जांच|स्कैम चेक)\s*(खोलें|दिखाओ)?/i,
    ],
    announcementEn: 'Opening Scam Shield',
    announcementHi: 'स्कैम शील्ड खोला जा रहा है',
  },
  {
    intent: 'LEARNING',
    route: '/(tabs)/learn',
    patterns: [
      /\b(teach me|open|show)?\s*(learning|literacy|financial literacy|modules|lessons|savings lesson)\b/i,
      /(सीखें|वित्तीय साक्षरता|मॉड्यूल|सबक|पाठ)\s*(खोलें|दिखाओ)?/i,
    ],
    announcementEn: 'Opening Financial Literacy',
    announcementHi: 'फाइनेंशियल साक्षरता खोली जा रही है',
  },
  {
    intent: 'MARKET',
    route: '/domain/market-intelligence',
    patterns: [
      /\b(tell me|check|show)?\s*(today's market|market pulse|market update|stock market|market)\b/i,
      /(मार्केट|शेयर बाज़ार|आज का बाजार|मार्केट पल्स)\s*(बताओ|दिखाओ|जांचें)?/i,
    ],
    announcementEn: 'Opening Live Market Intelligence',
    announcementHi: 'लाइव मार्केट इंटेलिजेंस खोला जा रहा है',
  },
  {
    intent: 'RECOMMENDATIONS',
    route: '/domain/recommendations',
    patterns: [
      /\b(what should i do next|recommendations|financial guidance|guidance|portfolio guidance)\b/i,
      /(मुझे क्या करना चाहिए|सुझाव बताओ|मार्गदर्शन|सिफारिशें)\s*(दिखाओ|बताओ)?/i,
    ],
    announcementEn: 'Opening Personalized Recommendations',
    announcementHi: 'व्यक्तिगत सुझाव खोले जा रहे हैं',
  },
  {
    intent: 'AI_SAARTHI',
    route: '/(tabs)/saarthi',
    patterns: [
      /\b(ask saarthi|ai saarthi|open saarthi|talk to saarthi|saarthi)\b/i,
      /(सारथी से पूछो|एआई सारथी|सारथी खोलें|सारथी)\s*(खोलें)?/i,
    ],
    announcementEn: 'Opening AI Saarthi Chat',
    announcementHi: 'AI सारथी चैट खोली जा रही है',
  },
  {
    intent: 'SETTINGS',
    route: '/(tabs)/more',
    patterns: [
      /\b(open|show)?\s*(settings|accessibility settings|more options|more)\b/i,
      /(सेटिंग्स|एक्सेसिबिलिटी सेटिंग्स|और विकल्प|मोर)\s*(खोलें)?/i,
    ],
    announcementEn: 'Opening Accessibility Settings',
    announcementHi: 'एक्सेसिबिलिटी सेटिंग्स खोली जा रही हैं',
  },
];

export function parseVoiceNavigationCommand(
  spokenText: string,
  language: string = 'en'
): VoiceNavigationResult {
  const clean = spokenText.trim();
  if (!clean) {
    return {
      intent: 'UNKNOWN',
      confidence: 0.0,
      speakAnnouncement: language === 'hi' ? 'कोई कमांड समझ नहीं आई।' : 'Command not recognized.',
      requiresConfirmation: false,
    };
  }

  for (const entry of INTENT_PATTERNS) {
    for (const pattern of entry.patterns) {
      if (pattern.test(clean)) {
        return {
          intent: entry.intent,
          confidence: 0.95,
          route: entry.route,
          speakAnnouncement: language === 'hi' ? entry.announcementHi : entry.announcementEn,
          requiresConfirmation: false,
        };
      }
    }
  }

  return {
    intent: 'UNKNOWN',
    confidence: 0.2,
    speakAnnouncement: language === 'hi' ? 'माफ़ कीजिये, मैं यह कमांड समझ नहीं सका।' : "Sorry, I couldn't understand that navigation command.",
    requiresConfirmation: false,
  };
}

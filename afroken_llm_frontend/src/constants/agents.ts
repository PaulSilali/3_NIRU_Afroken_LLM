// Agent types based on AfroKen LLM architecture
export type AgentType = 'service' | 'policy' | 'translation' | 'feedback';

export interface Agent {
  id: AgentType;
  name: string;
  description: string;
  capabilities: string[];
  icon: string;
}

export const AGENTS: Agent[] = [
  {
    id: 'service',
    name: 'Service Agent',
    description: 'Guides users through government service workflows',
    capabilities: [
      'ID renewal procedures',
      'NTSA licence applications',
      'Passport processing',
      'Business registration',
      'Land title searches',
    ],
    icon: 'Workflow',
  },
  {
    id: 'policy',
    name: 'Policy Agent',
    description: 'Summarizes laws, acts, and government gazettes',
    capabilities: [
      'Policy document summaries',
      'Legal gazette interpretation',
      'Regulation explanations',
      'Compliance guidelines',
      'Bill tracking',
    ],
    icon: 'Scale',
  },
  {
    id: 'translation',
    name: 'Translation Agent',
    description: 'Provides instant multilingual support',
    capabilities: [
      'English ↔ Swahili translation',
      'Sheng interpretation',
      'Regional dialect support',
      'Context-aware translation',
      'Cultural nuance handling',
    ],
    icon: 'Languages',
  },
  {
    id: 'feedback',
    name: 'Feedback Agent',
    description: 'Records sentiment and manages escalations',
    capabilities: [
      'Citizen sentiment analysis',
      'Escalation ticket creation',
      'Service quality tracking',
      'Issue categorization',
      'Response time monitoring',
    ],
    icon: 'MessageSquarePlus',
  },
];

// Performance targets from the brief
export const PERFORMANCE_TARGETS = {
  responseLatency: 1.5, // seconds
  answerAccuracy: 90, // percent
  satisfactionTarget: 80, // percent
  responseTimeReduction: 60, // percent
  satisfactionImprovement: 30, // percent
  annualSavings: 300000000, // KES
  newJobs: 1000, // count
};

// Data sources
export const DATA_SOURCES = [
  {
    name: 'Government Open Data Portal',
    category: 'Structured Data',
    coverage: 'KNBS, ICTA, eCitizen datasets',
  },
  {
    name: 'Policy Documents & Gazettes',
    category: 'Legal Documents',
    coverage: 'Laws, circulars, regulations',
  },
  {
    name: 'Huduma Centre FAQ Logs',
    category: 'Service Queries',
    coverage: '2018-2024 resolution history',
  },
  {
    name: 'Social Media Feedback',
    category: 'Citizen Sentiment',
    coverage: 'Twitter, Facebook (anonymized)',
  },
  {
    name: 'eCitizen Service Guidelines',
    category: 'Service Manuals',
    coverage: 'Ministry operational procedures',
  },
  {
    name: 'Translation Corpus',
    category: 'Multilingual Data',
    coverage: 'English–Swahili–regional dialects',
  },
];

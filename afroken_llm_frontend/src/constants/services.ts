import { ServiceType } from '@/types';

export interface ServiceConfig {
  id: ServiceType;
  name: string;
  icon: string;
  color: string;
  examples: string[];
  description?: string;
  logo?: string;
}

export const SERVICES: ServiceConfig[] = [
  {
    id: 'nhif',
    name: 'NHIF Health Insurance',
    description: 'Check status, renew membership, and get coverage information',
    icon: 'Heart',
    color: 'hsl(var(--primary))',
    logo: '/logos/NHIF-logo.jpg',
    examples: [
      'How do I register for NHIF?',
      'What are the NHIF contribution rates?',
      'How do I check my NHIF balance?',
    ],
  },
  {
    id: 'kra',
    name: 'KRA Tax Services',
    description: 'File returns, get PIN, check compliance status',
    icon: 'FileText',
    color: 'hsl(var(--accent))',
    logo: '/logos/kra_logo.png',
    examples: [
      'How do I file my tax returns?',
      'How do I get a KRA PIN?',
      'What are the tax deadlines?',
    ],
  },
  {
    id: 'huduma',
    name: 'Huduma Centre',
    description: 'Register for Huduma Number and manage services',
    icon: 'Building2',
    color: 'hsl(var(--info))',
    logo: '/logos/huduma center logo.png',
    examples: [
      'How do I book a Huduma Centre appointment?',
      'What documents do I need for ID renewal?',
      'Where is the nearest Huduma Centre?',
    ],
  },
];

export const MOCK_CITATIONS = [
  {
    id: '1',
    title: 'NHIF Act 1998',
    url: 'https://www.nhif.or.ke/act',
    snippet: 'National Hospital Insurance Fund regulations and guidelines',
  },
  {
    id: '2',
    title: 'KRA Tax Guide 2024',
    url: 'https://www.kra.go.ke/taxpayers-guide',
    snippet: 'Complete guide to tax filing and compliance in Kenya',
  },
  {
    id: '3',
    title: 'Huduma Centre Services',
    url: 'https://www.hudumakenya.go.ke/services',
    snippet: 'List of all services offered at Huduma Centres',
  },
  {
    id: '4',
    title: 'eCitizen Portal Guide',
    url: 'https://www.ecitizen.go.ke/guide',
    snippet: 'How to access government services online',
  },
];

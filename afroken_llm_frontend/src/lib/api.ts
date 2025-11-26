import { ChatRequest, ChatResponse, FeedbackRequest, DashboardMetrics } from '@/types';
import { MOCK_CITATIONS } from '@/constants/services';
import countiesData from '@/constants/counties.json';

const API_DELAY = 1000; // Simulate network delay

// Simulate API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Mock responses for different services
const MOCK_RESPONSES: Record<string, string> = {
  nhif: 'To register for NHIF, visit any Huduma Centre with your ID card and KRA PIN. You can also register online at www.nhif.or.ke. The minimum monthly contribution is KES 500 for self-employed individuals. Registration is free and immediate.',
  kra: 'To get a KRA PIN, visit www.kra.go.ke and click on "iTax Registration". You will need your ID number, email, and phone number. The PIN is generated instantly. You can also visit any KRA office or Huduma Centre for assistance.',
  huduma: 'To book a Huduma Centre appointment, visit www.hudumakenya.go.ke and select "Book Appointment". Choose your preferred service, date, and time. You will receive an SMS confirmation. Walk-ins are also welcome, but appointments get priority.',
  default: 'I can help you with NHIF, KRA, and Huduma Centre services. Please ask me a specific question about health insurance, tax services, or government document processing.',
};

export async function postChat(payload: ChatRequest): Promise<ChatResponse> {
  await delay(API_DELAY);

  const serviceKey = payload.context?.service || 'default';
  let answer = MOCK_RESPONSES[serviceKey] || MOCK_RESPONSES.default;

  // Check for specific keywords in the message
  const message = payload.message.toLowerCase();
  if (message.includes('nhif') || message.includes('health') || message.includes('insurance')) {
    answer = MOCK_RESPONSES.nhif;
  } else if (message.includes('kra') || message.includes('tax') || message.includes('pin')) {
    answer = MOCK_RESPONSES.kra;
  } else if (message.includes('huduma') || message.includes('id') || message.includes('passport')) {
    answer = MOCK_RESPONSES.huduma;
  }

  // Add language-specific variations
  if (payload.lang === 'sw') {
    answer = `[Swahili] ${answer}`;
  } else if (payload.lang === 'sheng') {
    answer = `[Sheng] ${answer}`;
  }

  const relevantCitations = MOCK_CITATIONS.filter((citation) => {
    const title = citation.title.toLowerCase();
    return (
      (message.includes('nhif') && title.includes('nhif')) ||
      (message.includes('kra') && title.includes('kra')) ||
      (message.includes('huduma') && title.includes('huduma'))
    );
  }).slice(0, 2);

  return {
    id: `msg_${Date.now()}`,
    answer,
    citations: relevantCitations.length > 0 ? relevantCitations : [MOCK_CITATIONS[3]],
    actions: serviceKey === 'huduma'
      ? [
          {
            type: 'BOOK',
            label: 'Book Appointment',
            payload: { service: 'huduma' },
          },
        ]
      : undefined,
  };
}

export async function postFeedback(feedback: FeedbackRequest): Promise<void> {
  await delay(500);
  console.log('Feedback submitted:', feedback);
  // In a real app, this would send to the backend
}

export async function getMetrics(county?: string): Promise<DashboardMetrics> {
  await delay(800);

  const filteredCounties = county
    ? countiesData.filter((c) => c.countyName.toLowerCase() === county.toLowerCase())
    : countiesData;

  const totalQueries = filteredCounties.reduce((sum, c) => sum + c.queries, 0);
  const totalEscalations = filteredCounties.reduce((sum, c) => sum + c.escalations, 0);
  const avgSatisfaction =
    filteredCounties.reduce((sum, c) => sum + c.satisfaction, 0) / filteredCounties.length;

  return {
    totalQueries,
    satisfactionRate: Math.round(avgSatisfaction),
    avgResponseTime: 2.3,
    escalations: totalEscalations,
    topIntents: [
      { intent: 'NHIF Registration', count: 1234, percentage: 28 },
      { intent: 'KRA PIN Application', count: 987, percentage: 22 },
      { intent: 'Huduma Appointments', count: 876, percentage: 20 },
      { intent: 'Tax Returns Filing', count: 654, percentage: 15 },
      { intent: 'ID Renewal', count: 543, percentage: 12 },
    ],
    countySummary: filteredCounties.map(c => ({
      ...c,
      coordinates: c.coordinates as [number, number]
    })),
  };
}

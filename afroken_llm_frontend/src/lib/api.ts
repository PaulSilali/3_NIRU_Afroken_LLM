import { ChatRequest, ChatResponse, FeedbackRequest, DashboardMetrics } from '@/types';
import { MOCK_CITATIONS } from '@/constants/services';
import countiesData from '@/constants/counties.json';

// API base URL - use environment variable or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Check if we should use mock mode (when backend is not available)
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true' || false;

const API_DELAY = 1000; // Simulate network delay

// Simulate API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Mock responses for different services (fallback)
const MOCK_RESPONSES: Record<string, string> = {
  nhif: 'To register for NHIF, visit any Huduma Centre with your ID card and KRA PIN. You can also register online at www.nhif.or.ke. The minimum monthly contribution is KES 500 for self-employed individuals. Registration is free and immediate.',
  kra: 'To get a KRA PIN, visit www.kra.go.ke and click on "iTax Registration". You will need your ID number, email, and phone number. The PIN is generated instantly. You can also visit any KRA office or Huduma Centre for assistance.',
  huduma: 'To book a Huduma Centre appointment, visit www.hudumakenya.go.ke and select "Book Appointment". Choose your preferred service, date, and time. You will receive an SMS confirmation. Walk-ins are also welcome, but appointments get priority.',
  default: 'I can help you with NHIF, KRA, and Huduma Centre services. Please ask me a specific question about health insurance, tax services, or government document processing.',
};

export async function postChat(payload: ChatRequest): Promise<ChatResponse> {
  // Use mock if explicitly enabled or if API_BASE_URL is not set
  if (USE_MOCK) {
    return postChatMock(payload);
  }

  try {
    // Call real backend API
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: payload.message,
        language: payload.lang || 'en', // Frontend uses 'lang', backend expects 'language'
        device: 'web',
        conversation_id: undefined,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Transform backend response to frontend format
    // Backend returns: { reply, citations: [{title, filename, source}, ...] }
    // Frontend expects: { id, answer, citations: [{id, title, url, snippet?}, ...] }
    const transformedCitations = (data.citations || []).map((cit: any, idx: number) => ({
      id: cit.filename || `cit_${idx}`,
      title: cit.title || 'Untitled',
      url: cit.source || cit.filename || '',
      snippet: cit.snippet || '',
    }));

    return {
      id: `msg_${Date.now()}`,
      answer: data.reply || data.answer || 'No response received',
      citations: transformedCitations,
      actions: undefined, // Backend doesn't return actions yet
    };
  } catch (error) {
    console.error('API call failed, falling back to mock:', error);
    // Fallback to mock on error
    return postChatMock(payload);
  }
}

// Mock function (kept for fallback)
function postChatMock(payload: ChatRequest): Promise<ChatResponse> {
  return new Promise((resolve) => {
    setTimeout(() => {
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

      resolve({
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
      });
    }, API_DELAY);
  });
}

export async function postFeedback(feedback: FeedbackRequest): Promise<void> {
  await delay(500);
  console.log('Feedback submitted:', feedback);
  // In a real app, this would send to the backend
}

// Dummy data for demo purposes - comprehensive dataset
const DUMMY_METRICS_BASE: DashboardMetrics = {
  totalQueries: 19220,
  satisfactionRate: 84,
  avgResponseTime: 2.3,
  escalations: 342,
  topIntents: [
    { intent: 'NHIF Registration', count: 1234, percentage: 28 },
    { intent: 'KRA PIN Application', count: 987, percentage: 22 },
    { intent: 'Huduma Appointments', count: 876, percentage: 20 },
    { intent: 'Tax Returns Filing', count: 654, percentage: 15 },
    { intent: 'ID Renewal', count: 543, percentage: 12 },
  ],
  countySummary: countiesData.map(c => ({
    ...c,
    coordinates: c.coordinates as [number, number]
  })),
};

// Time range multipliers for realistic variation
const TIME_RANGE_MULTIPLIERS = {
  '7d': { queries: 0.25, escalations: 0.25 },
  '30d': { queries: 1.0, escalations: 1.0 },
  '90d': { queries: 2.8, escalations: 2.8 },
};

// Generate dummy metrics based on filters (instant, no API calls)
export function getDummyMetrics(county?: string, timeRange: '7d' | '30d' | '90d' = '30d'): DashboardMetrics {
  // Filter counties
  const filteredCounties = county
    ? countiesData.filter((c) => c.countyName.toLowerCase() === county.toLowerCase())
    : countiesData;

  // Calculate totals from filtered counties
  const totalQueries = filteredCounties.reduce((sum, c) => sum + c.queries, 0);
  const totalEscalations = filteredCounties.reduce((sum, c) => sum + c.escalations, 0);
  const avgSatisfaction = filteredCounties.length > 0
    ? Math.round(filteredCounties.reduce((sum, c) => sum + c.satisfaction, 0) / filteredCounties.length)
    : 84;

  // Apply time range multiplier
  const multiplier = TIME_RANGE_MULTIPLIERS[timeRange];
  const adjustedQueries = Math.round(totalQueries * multiplier.queries);
  const adjustedEscalations = Math.round(totalEscalations * multiplier.escalations);

  // Adjust top intents based on time range
  const intentMultiplier = multiplier.queries;
  const adjustedTopIntents = DUMMY_METRICS_BASE.topIntents.map(intent => ({
    ...intent,
    count: Math.round(intent.count * intentMultiplier),
    percentage: intent.percentage, // Keep percentages consistent
  }));

  return {
    totalQueries: adjustedQueries,
    satisfactionRate: avgSatisfaction,
    avgResponseTime: 2.3,
    escalations: adjustedEscalations,
    topIntents: adjustedTopIntents,
    countySummary: filteredCounties.map(c => ({
      ...c,
      coordinates: c.coordinates as [number, number]
    })),
  };
}

// Simplified getMetrics - uses dummy data only for smooth filtering
export async function getMetrics(county?: string, timeRange: '7d' | '30d' | '90d' = '30d'): Promise<DashboardMetrics> {
  // Use dummy data only - instant response, no API delays
  return new Promise((resolve) => {
    // Simulate minimal delay for smooth UX (50ms)
    setTimeout(() => {
      resolve(getDummyMetrics(county, timeRange));
    }, 50);
  });
}

// Admin API functions
export async function uploadPDF(file: File, category?: string) {
  const formData = new FormData();
  formData.append('file', file);
  if (category) formData.append('category', category);

  const response = await fetch(`${API_BASE_URL}/api/v1/admin/documents/upload-pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    // Try to extract error message from response
    let errorMessage = 'Upload failed';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export async function scrapeURL(url: string, category?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/documents/scrape-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, category }),
  });

  if (!response.ok) {
    // Try to extract error message from response
    let errorMessage = 'Scraping failed';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export async function getJobs(status?: string, jobType?: string) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (jobType) params.append('job_type', jobType);

  const response = await fetch(`${API_BASE_URL}/api/v1/admin/jobs?${params}`);
  if (!response.ok) throw new Error('Failed to fetch jobs');
  return response.json();
}

export async function getJobStatus(jobId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/jobs/${jobId}`);
  if (!response.ok) throw new Error('Failed to fetch job status');
  return response.json();
}

// Services Management
export async function getServices() {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/services`);
  if (!response.ok) throw new Error('Failed to fetch services');
  return response.json();
}

export async function createService(formData: FormData) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/services`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create service');
  }
  return response.json();
}

// Huduma Centres Management
export async function getHudumaCentres() {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/huduma-centres`);
  if (!response.ok) throw new Error('Failed to fetch Huduma Centres');
  return response.json();
}

export async function createHudumaCentre(data: {
  name: string;
  county: string;
  sub_county?: string;
  town?: string;
  latitude?: number;
  longitude?: number;
  contact_phone?: string;
  contact_email?: string;
}) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/huduma-centres`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create Huduma Centre');
  }
  return response.json();
}

// Chat Metrics (for dual implementation)
export async function getChatMetrics() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/admin/metrics`);
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return response.json();
  } catch (error) {
    console.error('Failed to fetch chat metrics:', error);
    return null; // Return null to indicate fallback to dummy data
  }
}

# AfroKen — Citizen Service Copilot

A production-ready, accessible, multilingual AI chatbot for Kenyan government services. Built with React, TypeScript, Tailwind CSS, and designed to be mobile-first, PWA-capable, and WCAG AA compliant.

## 🚀 Features

- **Multilingual Support**: English, Kiswahili, and Sheng
- **Service Coverage**: NHIF, KRA, and Huduma Centre services
- **Real-time Chat**: AI-powered conversational interface with citation sources
- **Dashboard Analytics**: Query metrics, satisfaction rates, and county-level insights
- **Accessible Design**: WCAG AA compliant, keyboard navigable, screen reader friendly
- **Mobile-First**: Responsive design optimized for all devices
- **Interactive Map**: Leaflet-based county visualization with query distribution

## 📋 Tech Stack

### Core
- **React 18** with TypeScript
- **Vite** for build tooling
- **React Router** for navigation
- **TanStack Query** for data fetching and caching
- **Zustand** for lightweight state management

### UI & Styling
- **Tailwind CSS** for utility-first styling
- **shadcn/ui** component primitives
- **Framer Motion** for animations
- **Lucide React** for icons

### Features
- **i18next** for internationalization
- **React Leaflet** for interactive maps
- **Recharts** for data visualization
- **Sonner** for toast notifications

## 🏗️ Project Structure

```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatWindow.tsx       # Main chat interface
│   │   ├── ChatInput.tsx        # Message input with voice support
│   │   └── MessageBubble.tsx    # Message display with citations
│   ├── Header.tsx               # Navigation header
│   ├── Footer.tsx               # App footer
│   ├── LanguageSwitcher.tsx     # Language selector
│   ├── ServiceCard.tsx          # Service selection cards
│   ├── CountyMap.tsx            # Interactive Kenya county map
│   └── MetricCard.tsx           # Dashboard metric display
├── pages/
│   ├── Index.tsx                # Home page
│   ├── Dashboard.tsx            # Analytics dashboard
│   ├── Settings.tsx             # User preferences
│   └── NotFound.tsx             # 404 page
├── lib/
│   ├── api.ts                   # Mock API functions
│   ├── i18n.ts                  # i18n configuration
│   └── utils.ts                 # Utility functions
├── store/
│   └── chatStore.ts             # Zustand chat state
├── hooks/
│   └── useChat.ts               # Chat functionality hook
├── types/
│   └── index.ts                 # TypeScript type definitions
├── constants/
│   ├── services.ts              # Service configurations
│   └── counties.json            # County data
└── locales/
    ├── en/translation.json      # English translations
    ├── sw/translation.json      # Swahili translations
    └── sheng/translation.json   # Sheng translations
```

## 🚦 Getting Started

### Prerequisites
- Node.js 18+ or Bun
- npm, pnpm, or bun

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Setup

To connect to a real backend API, set the following environment variable:

```bash
VITE_API_BASE_URL=https://your-api-endpoint.com
```

Update `src/lib/api.ts` to use this URL instead of mock responses.

## 🎨 Design System

The app uses a Kenya-inspired color palette:

- **Primary**: Kenya green (`hsl(142 76% 25%)`) for main actions
- **Accent**: Kenya red (`hsl(0 85% 45%)`) for highlights
- **Neutral**: Grayscale for backgrounds and text

All colors are defined as HSL CSS variables in `src/index.css` and `tailwind.config.ts` for easy theming.

## 🌍 Internationalization

Add or modify translations in `src/locales/[lang]/translation.json`. The app uses i18next for runtime translation switching.

Languages are automatically persisted to localStorage.

## 🗺️ Map Integration

The county map uses React Leaflet with OpenStreetMap tiles. To use Mapbox instead:

1. Get a Mapbox API token
2. Update the `TileLayer` component in `src/components/CountyMap.tsx`
3. Change the URL to Mapbox's tile service

## 📊 Mock Data

Mock API responses are in `src/lib/api.ts`. Sample county data is in `src/constants/counties.json`.

To generate more mock data, create a script in `scripts/gen-mock-data.ts`:

```typescript
// Generate 50 sample chats, metrics, etc.
```

## ♿ Accessibility

- All interactive elements have proper ARIA labels
- Keyboard navigation fully supported (Tab, Enter, Escape)
- Chat updates use `aria-live="polite"`
- Color contrast meets WCAG AA standards (4.5:1 for text)
- Focus indicators on all interactive elements

## 🔗 Real API Integration

To connect to a real FastAPI backend:

1. Set `VITE_API_BASE_URL` environment variable
2. Update `src/lib/api.ts` to use `fetch(VITE_API_BASE_URL + endpoint)`
3. Ensure backend returns data matching the TypeScript interfaces in `src/types/index.ts`

### Expected API Endpoints

```
POST /api/chat
  Body: { userId?, lang, message, context? }
  Response: { id, answer, citations, actions? }

POST /api/feedback
  Body: { chatId, messageId, rating, comments? }

GET /api/metrics?county=xxx
  Response: { totalQueries, satisfactionRate, avgResponseTime, escalations, topIntents, countySummary }
```

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Docker
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t afroken-frontend .
docker run -p 3000:80 afroken-frontend
```

## 🧪 Testing

```bash
# Run tests (when implemented)
npm run test

# Lint code
npm run lint

# Format code
npm run format
```

## 📝 Product Brief Reference

This implementation follows the AfroKen/AgriSentinel product specification provided in the original brief, including:

- Service coverage: NHIF, KRA, Huduma Centre, eCitizen
- Multilingual support: English, Kiswahili, Sheng
- Citation-based responses with RAG sources
- County-level analytics and visualizations
- Accessibility-first design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper TypeScript types
4. Ensure accessibility standards are met
5. Submit a pull request

## 📄 License

© 2025 AfroKen. All rights reserved.

---

**Built with ❤️ for Kenyan citizens**

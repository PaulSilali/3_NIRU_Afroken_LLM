# AfroKen Architecture Documentation

## Overview

AfroKen is a production-ready, accessible citizen service copilot built with modern React patterns and best practices. This document details the architectural decisions, data flow, and component hierarchy.

## Technology Choices & Rationale

### Frontend Framework
- **React 18** with TypeScript for type safety and modern React features
- **Vite** for fast development and optimized production builds
- Chosen over Next.js to match Lovable platform requirements

### State Management
- **Zustand** for global state (chat, language preferences)
  - Lightweight alternative to Redux
  - Minimal boilerplate
  - Perfect for chat state and UI toggles
- **TanStack Query** for server state
  - Automatic caching and background refetching
  - Loading and error states handled automatically
  - Perfect for API data

### UI & Styling
- **Tailwind CSS** for utility-first styling
  - Highly customizable via `tailwind.config.ts`
  - Design system enforced via CSS variables
- **shadcn/ui** component primitives
  - Accessible by default (WCAG AA)
  - Fully customizable
  - Tree-shakeable
- **Framer Motion** for animations
  - Declarative animations
  - Accessibility features built-in (respects prefers-reduced-motion)

### Internationalization
- **i18next** + **react-i18next**
  - Runtime language switching
  - Nested translations
  - TypeScript support
  - localStorage persistence

### Maps
- **React Leaflet** with OpenStreetMap
  - Free and open-source
  - Easy to swap for Mapbox if needed
  - Mobile-friendly

## Architecture Patterns

### Component Structure

```
┌─────────────────────────────────────┐
│           App.tsx (Root)            │
│  ┌─────────────────────────────┐   │
│  │  QueryClientProvider        │   │
│  │  I18nextProvider            │   │
│  │  TooltipProvider            │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼──────┐       ┌──────▼─────┐
│  Pages   │       │  Layout    │
│          │       │  Components│
│ - Index  │       │            │
│ - Dash   │       │ - Header   │
│ - Settings│      │ - Footer   │
└──────────┘       │ - Chat     │
                   └────────────┘
```

### State Management Strategy

#### Global State (Zustand)
- Chat open/closed state
- Current service context
- User language preference
- Message history (ephemeral)

#### Server State (TanStack Query)
- Dashboard metrics
- County data
- Cached with background refetching

#### Local State (useState)
- Form inputs
- UI toggles (dropdowns, accordions)
- Component-specific state

### Data Flow

```
User Action
    │
    ▼
Component Handler
    │
    ├─► Local State Update (UI feedback)
    │
    ├─► Zustand Action (global state)
    │
    └─► TanStack Query Mutation
            │
            ▼
        API Call (lib/api.ts)
            │
            ├─► Success → Update cache → Re-render
            │
            └─► Error → Show toast → Rollback
```

## File Organization

### Components
- **Atomic design** principle
- **Colocation** of related components
- **Index exports** for cleaner imports

### Types
- Central `types/index.ts` for all interfaces
- Exported from single location
- Reused across components and API

### API Layer
- `lib/api.ts` abstracts all backend calls
- Mock responses for development
- Easy to swap with real backend

### Internationalization
- JSON files per language
- Nested structure mirrors UI hierarchy
- Example: `home.hero.title`

## Accessibility Implementation

### Semantic HTML
```tsx
<header>
  <nav aria-label="Main navigation">
    <NavLink to="/" aria-current={isActive ? 'page' : undefined}>
```

### ARIA Attributes
- `aria-label` on icons and buttons without text
- `aria-live="polite"` on chat messages
- `aria-expanded` on collapsible elements
- `role` attributes where semantic HTML isn't sufficient

### Keyboard Navigation
- All interactive elements focusable
- Visible focus indicators (`:focus-visible`)
- Keyboard shortcuts (Enter to send, Escape to close)
- Tab order follows visual order

### Color Contrast
- All text meets WCAG AA (4.5:1 minimum)
- Kenya green primary: verified against white
- Tested with tools like WebAIM Contrast Checker

## Performance Optimizations

### Code Splitting
- Route-based splitting via React Router
- Lazy loading for heavy components (maps, charts)

### Image Optimization
- Generated icons served from CDN-friendly paths
- Proper sizing and formats

### API Caching
- TanStack Query caches API responses
- Stale-while-revalidate pattern
- Background refetching

### Bundle Size
- Tree-shaking enabled
- Only used icons imported from Lucide
- Production build minified and compressed

## Security Considerations

### XSS Protection
- React's JSX escaping by default
- No `dangerouslySetInnerHTML` except for controlled content

### CORS
- API calls respect CORS policies
- Configured in backend (not frontend concern)

### Data Privacy
- No sensitive data in localStorage (only language preference)
- User messages not persisted client-side
- Analytics aggregated and anonymized

## Deployment Strategy

### Development
```bash
npm run dev  # Hot module replacement
```

### Production Build
```bash
npm run build  # Vite optimized build
npm run preview  # Test production build locally
```

### Docker Deployment
```bash
docker build -t afroken-frontend .
docker run -p 8080:80 afroken-frontend
```

### CI/CD
- GitHub Actions workflow in `.github/workflows/ci.yml`
- Lint, type-check, build on every push
- Docker image built on main branch

## Testing Strategy (To Be Implemented)

### Unit Tests
- Component rendering (React Testing Library)
- Utility functions (Vitest)
- Hooks (React Hooks Testing Library)

### Integration Tests
- API mocking with MSW
- User flows (chat, language switch)
- Accessibility testing (jest-axe)

### E2E Tests
- Playwright or Cypress
- Critical user journeys
- Mobile viewport testing

## Future Enhancements

### PWA Features
- Service worker for offline support
- Push notifications for escalations
- App install prompt

### Advanced Features
- WebSocket for real-time chat
- Voice input with Web Speech API
- File upload for document processing

### Analytics
- User behavior tracking
- Error monitoring (Sentry)
- Performance monitoring (Web Vitals)

## Environment Variables

```bash
# Required
VITE_API_BASE_URL=https://api.afroken.go.ke

# Optional
VITE_MAPBOX_TOKEN=pk.xxx  # If using Mapbox
VITE_ANALYTICS_ID=G-XXX  # Google Analytics
```

## Maintenance & Monitoring

### Dependencies
- Regular updates via Dependabot
- Security audit: `npm audit`
- Bundle size monitoring

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES2020+ features
- Polyfills not required

### Accessibility Audits
- Lighthouse CI in GitHub Actions
- Regular manual testing with screen readers
- Keyboard navigation testing

---

**Document Version**: 1.0
**Last Updated**: 2025-01-XX
**Maintainer**: AfroKen Team

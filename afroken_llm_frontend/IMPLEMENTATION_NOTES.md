# Implementation Notes

This document contains important notes about the implementation, workarounds, and things to be aware of.

## Current Implementation Status

### ✅ Completed Features
- [x] Design system with Kenya-inspired colors
- [x] Multilingual support (EN/SW/Sheng)
- [x] Chat interface with citations
- [x] Dashboard with analytics
- [x] County map visualization
- [x] Settings page
- [x] Responsive mobile-first design
- [x] Accessibility features (WCAG AA)
- [x] Docker deployment setup
- [x] CI/CD pipeline
- [x] Mock API layer

### 🚧 Partial/Mock Implementations

#### Voice Input
**Status**: UI implemented, functionality mocked

The chat input has a microphone button, but currently only shows toast notifications. To implement real voice input:

```typescript
// In ChatInput.tsx
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = language === 'sw' ? 'sw-KE' : 'en-KE';
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  setMessage(transcript);
};
recognition.start();
```

#### Real-time Streaming
**Status**: Not implemented

Chat responses are returned in full. To add streaming:

1. Backend: Return Server-Sent Events (SSE) or WebSocket
2. Frontend: Use `EventSource` or WebSocket client
3. Update `MessageBubble` to append text incrementally

#### PWA Installation
**Status**: Manifest created, service worker not implemented

To add offline support:

```bash
npm install vite-plugin-pwa
```

Update `vite.config.ts`:
```typescript
import { VitePWA } from 'vite-plugin-pwa';

plugins: [
  VitePWA({
    registerType: 'autoUpdate',
    manifest: {
      // Use existing manifest.json
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,ico,png,svg}']
    }
  })
]
```

## Known Limitations

### Map Icons
Only the 512x512 icon has been generated. To create other sizes:

```bash
# Using ImageMagick
convert public/icons/icon-512x512.png -resize 192x192 public/icons/icon-192x192.png
convert public/icons/icon-512x512.png -resize 144x144 public/icons/icon-144x144.png
# ... repeat for 72, 96, 128, 152, 384
```

Or use an online tool like [PWA Asset Generator](https://www.pwabuilder.com/).

### Leaflet CSS
Leaflet CSS is imported globally in `index.css`. This adds ~20KB to the bundle. If not using maps on all pages, consider lazy-loading it:

```typescript
// In CountyMap.tsx
import('leaflet/dist/leaflet.css');
```

### Type Safety
The i18next translations are not fully type-safe. To add type safety:

```typescript
// src/types/i18next.d.ts
import 'react-i18next';
import type en from '@/locales/en/translation.json';

declare module 'react-i18next' {
  interface CustomTypeOptions {
    resources: {
      translation: typeof en;
    };
  }
}
```

## Real Backend Integration

### API Contract
The mock API in `src/lib/api.ts` matches this contract:

```typescript
// POST /api/chat
Request: {
  userId?: string;
  lang: 'en' | 'sw' | 'sheng';
  message: string;
  context?: {
    service?: 'nhif' | 'kra' | 'huduma';
    county?: string;
  };
}

Response: {
  id: string;
  stream?: boolean;  // If true, use SSE
  answer: string;
  citations: Array<{
    id: string;
    title: string;
    url: string;
    snippet?: string;
  }>;
  actions?: Array<{
    type: 'BOOK' | 'LINK' | 'FORM';
    label: string;
    payload?: any;
  }>;
}
```

### Authentication
Currently no auth implemented. To add:

1. Backend: Use JWT tokens
2. Frontend: Store token in memory (not localStorage for security)
3. Add `Authorization: Bearer ${token}` header to all API calls

Example:
```typescript
// src/lib/auth.ts
let authToken: string | null = null;

export const setAuthToken = (token: string) => {
  authToken = token;
};

export const getAuthToken = () => authToken;

// In api.ts
headers: {
  'Authorization': authToken ? `Bearer ${authToken}` : '',
  'Content-Type': 'application/json',
}
```

## Mobile Testing Checklist

- [ ] Touch targets at least 44x44px
- [ ] Viewport meta tag present
- [ ] Text readable without zoom
- [ ] No horizontal scrolling
- [ ] Forms work with mobile keyboard
- [ ] Chat input doesn't get hidden by keyboard
- [ ] Maps work with touch gestures

## Browser Compatibility

### Tested On
- ✅ Chrome 120+
- ✅ Firefox 121+
- ✅ Safari 17+
- ✅ Edge 120+

### Known Issues
- Safari < 15: CSS `aspect-ratio` not supported
- Firefox: Leaflet marker popup positioning slightly off
- Mobile browsers: Virtual keyboard may cover chat input

### Polyfills
None required for modern browsers. If supporting IE11:

```bash
npm install core-js regenerator-runtime
```

## Performance Tips

### Reduce Bundle Size
```bash
# Analyze bundle
npm run build
npx vite-bundle-visualizer dist/stats.html
```

Common optimizations:
- Use dynamic imports for heavy components
- Consider date-fns instead of moment.js (we're using date-fns)
- Lazy load Recharts if not needed on initial page

### Optimize Images
```bash
# Using Sharp (Node.js)
npm install sharp
```

```javascript
const sharp = require('sharp');
sharp('icon-512x512.png')
  .resize(192, 192)
  .webp({ quality: 80 })
  .toFile('icon-192x192.webp');
```

## Debugging

### Common Issues

#### "Cannot find module" errors
- Check `tsconfig.json` paths
- Ensure `@/` alias is configured in `vite.config.ts`

#### Map not rendering
- Check Leaflet CSS is imported
- Verify container has height
- Check coordinates are [lat, lng] not [lng, lat]

#### i18next translations not updating
- Clear localStorage
- Hard refresh (Ctrl+Shift+R)
- Check browser console for i18next errors

### Development Tools
```bash
# Type checking
npm run type-check

# Lint
npm run lint

# Format
npx prettier --write src/
```

## Security Best Practices

### XSS Prevention
- Never use `innerHTML` or `dangerouslySetInnerHTML` with user input
- Sanitize any HTML content from API
- React escapes JSX by default

### CSRF Prevention
- Use SameSite cookies for session
- Add CSRF tokens to state-changing requests
- Validate origin header on backend

### Content Security Policy
Add to `index.html`:
```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self' data:;
  connect-src 'self' https://api.afroken.go.ke;
">
```

## Deployment Checklist

- [ ] Set `VITE_API_BASE_URL` environment variable
- [ ] Update `manifest.json` with production URLs
- [ ] Generate all icon sizes
- [ ] Add robots.txt
- [ ] Configure CDN/caching
- [ ] Set up error monitoring (Sentry)
- [ ] Configure analytics
- [ ] Test on real mobile devices
- [ ] Run Lighthouse audit
- [ ] Test with screen reader
- [ ] Verify all links work
- [ ] Check 404 page

## Support & Maintenance

### Updating Dependencies
```bash
# Check for updates
npm outdated

# Update all (careful!)
npm update

# Update specific package
npm install package-name@latest
```

### Monitoring
- Set up Sentry for error tracking
- Monitor Core Web Vitals
- Track user flows with analytics
- Monitor API response times

---

**Questions?** Contact the AfroKen team or open an issue on GitHub.

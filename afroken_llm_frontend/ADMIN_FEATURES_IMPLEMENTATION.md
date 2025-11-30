# Admin Dashboard Features Implementation

## Overview

This document describes the implementation of admin features for adding services and Huduma Centres, plus the dual implementation for dashboard metrics.

## Features Implemented

### 1. Add Service Feature

**Location**: Admin Dashboard → Settings Tab → "Add New Service" Card

**Functionality**:
- Admin can add a new government service
- Form includes:
  - **Title** (required): Service name
  - **Description** (required): Brief description
  - **Category**: Dropdown (general, health, finance, identity, business, travel, transport)
  - **Logo** (optional): Upload image file
- Service is saved to `services` table in database
- Service appears as a card on the Services page
- **Duplicate Prevention**: If service already exists in dummy data or database, it won't be added again

**Backend Endpoint**: `POST /api/v1/admin/services`
- Accepts FormData with title, description, category, and optional logo file
- Uploads logo to MinIO/storage
- Creates service record in database

**Frontend Integration**:
- Services page fetches from API every 30 seconds
- Merges API services with dummy data
- Avoids duplicates by checking service name

### 2. Add Huduma Centre Feature

**Location**: Admin Dashboard → Settings Tab → "Add New Huduma Centre" Card

**Functionality**:
- Admin can add a new Huduma Centre location
- Form includes:
  - **Name** (required): Centre name
  - **County** (required): County name
  - **Sub-County** (optional)
  - **Town** (optional)
  - **Latitude** (optional): GPS coordinate
  - **Longitude** (optional): GPS coordinate
  - **Contact Phone** (optional)
  - **Contact Email** (optional)
- Centre is saved to `huduma_centres` table
- Default operating hours and facilities are set automatically

**Backend Endpoint**: `POST /api/v1/admin/huduma-centres`
- Accepts JSON with centre details
- Generates center code automatically
- Sets default opening hours and facilities

### 3. Dual Implementation for Dashboard Metrics

**Location**: Dashboard page (`/dashboard`)

**Functionality**:
- **Dummy Data**: Maintains existing dummy data for demo purposes
- **Real Data**: Fetches metrics from `chat_metrics` table
- **Combined Display**: Adds real data to dummy data
  - Total queries = dummy + real
  - Satisfaction rate = average of dummy + real
  - Response time = average of dummy + real
  - Escalations = dummy + real
  - Top intents = merged list (top 5)

**Backend Endpoint**: `GET /api/v1/admin/metrics`
- Aggregates data from `chat_metrics` table (last 30 days)
- Returns:
  - Total queries, conversations, messages
  - Average response time
  - Satisfaction rate
  - Top intents
  - Unique users

**Frontend Implementation**:
- `getMetrics()` function in `src/lib/api.ts`
- Tries to fetch real metrics first
- If successful, combines with dummy data
- If failed, falls back to dummy data only
- This allows testing DB connection while maintaining demo functionality

## Database Tables Used

### services
- Stores service information
- Fields: name, category, description, service_website, keywords, is_active
- Used by: Services page, Admin dashboard

### huduma_centres
- Stores Huduma Centre locations
- Fields: name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities
- Used by: Location search, appointment booking

### chat_metrics
- Stores aggregated chat metrics
- Fields: date_hour, total_conversations, total_messages, total_queries, average_response_time_ms, unique_users, top_intents, average_satisfaction_score, etc.
- Used by: Dashboard (dual implementation)

## API Endpoints

### Services Management
```
GET  /api/v1/admin/services          - Get all services
POST /api/v1/admin/services          - Create new service (FormData: title, description, category, logo)
```

### Huduma Centres Management
```
GET  /api/v1/admin/huduma-centres    - Get all Huduma Centres
POST /api/v1/admin/huduma-centres    - Create new Huduma Centre (JSON body)
```

### Metrics
```
GET  /api/v1/admin/metrics            - Get aggregated chat metrics
```

## Frontend Components Updated

### 1. `src/pages/AdminDashboard.tsx`
- Added "Add New Service" form in Settings tab
- Added "Add New Huduma Centre" form in Settings tab
- Added mutation hooks for creating services and centres
- Added form state management

### 2. `src/pages/Services.tsx`
- Added `useQuery` to fetch services from API
- Added `useEffect` to merge API services with dummy data
- Prevents duplicate services
- Auto-refreshes every 30 seconds

### 3. `src/pages/Dashboard.tsx`
- Already uses `getMetrics()` which now implements dual mode
- No changes needed - works automatically

### 4. `src/lib/api.ts`
- Added `getServices()` function
- Added `createService()` function
- Added `createHudumaCentre()` function
- Added `getChatMetrics()` function
- Updated `getMetrics()` to implement dual mode (dummy + real)

## SQL Scripts

### 1. `afroken_llm_seed_data.sql`
- Seeds `services` table with 10 core services
- Seeds `huduma_centres` table with 28+ centres
- Seeds `service_steps` with procedural guidance

### 2. `seed_chat_metrics.sql` (NEW)
- Seeds `chat_metrics` table with sample data
- Includes historical data (past 7 days)
- Includes recent data for testing
- Includes current hour data for real-time display
- Run this to test the dual implementation

## Usage Instructions

### 1. Adding a Service

1. Go to Admin Dashboard
2. Click "Settings" tab
3. Scroll to "Add New Service" card
4. Fill in:
   - Service Title (required)
   - Description (required)
   - Category (select from dropdown)
   - Logo (optional - upload image)
5. Click "Add Service"
6. Service will appear on Services page immediately (after refresh)

### 2. Adding a Huduma Centre

1. Go to Admin Dashboard
2. Click "Settings" tab
3. Scroll to "Add New Huduma Centre" card
4. Fill in:
   - Centre Name (required)
   - County (required)
   - Other fields (optional)
5. Click "Add Huduma Centre"
6. Centre will be saved to database

### 3. Testing Dashboard Metrics

1. Run the seed script:
   ```bash
   psql -U afroken -d afroken_llm_db -f seed_chat_metrics.sql
   ```

2. Go to Dashboard page
3. Metrics will show:
   - Dummy data + Real data from database
   - Combined totals
   - If DB connection fails, shows dummy data only

4. To verify DB connection:
   - Check browser console for API calls
   - Metrics should be higher than dummy data alone
   - Top intents should include data from database

## Testing Checklist

- [ ] Admin can add a service with title, description, category
- [ ] Admin can upload a logo for service
- [ ] Service appears on Services page as a card
- [ ] Duplicate services are not added
- [ ] Admin can add a Huduma Centre
- [ ] Huduma Centre is saved with all details
- [ ] Dashboard shows combined metrics (dummy + real)
- [ ] Dashboard falls back to dummy data if DB unavailable
- [ ] Services page auto-refreshes every 30 seconds
- [ ] Logo uploads work correctly
- [ ] Form validation works (required fields)

## Notes

1. **Duplicate Prevention**: Services are checked by name (case-insensitive). If a service with the same name exists in dummy data or database, it won't be added again.

2. **Logo Storage**: Logos are uploaded to MinIO/storage and the URL is stored in the database. If MinIO is not available, the service is still created but without a logo URL.

3. **Dual Implementation**: The dashboard maintains dummy data for demo purposes while also reading from the database. This allows:
   - Testing database connection
   - Maintaining demo functionality
   - Gradual migration from dummy to real data

4. **Auto-refresh**: Services page automatically refetches from API every 30 seconds to show newly added services.

5. **Error Handling**: All API calls have error handling with user-friendly toast notifications.

## Future Enhancements

1. Edit/Delete services and Huduma Centres
2. Bulk import services from CSV
3. Service categories management
4. Real-time metrics updates (WebSocket)
5. Metrics export functionality
6. Service analytics dashboard


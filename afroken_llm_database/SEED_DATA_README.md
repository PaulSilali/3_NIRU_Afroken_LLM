# Seed Data Script Documentation

## Overview

The `afroken_llm_seed_data.sql` script populates the AfroKen LLM database with initial data for:
1. **Huduma Centres** - 28+ centres across major counties (extendable to all 57)
2. **Government Services** - 10 core services based on frontend analysis
3. **Service Steps** - Procedural guidance for key services

## What's Included

### Huduma Centres (28+ Centres)

The script includes Huduma Centres from:

#### Nairobi County (5 centres)
- Huduma Centre GPO (Teleposta Towers, Kenyatta Avenue)
- Huduma Centre City Square (Haile Selassie Avenue)
- Huduma Centre Eastleigh (Eastleigh Social Hall)
- Huduma Centre Makadara (Jogoo Road)
- Huduma Centre Kibra (Kibra Sub-County Office)

#### Central Kenya (5 centres)
- Gatundu North (Kamwangi DO Office, Kiambu)
- Thika (Thika Town, Kiambu)
- Nyeri (Dedan Kimathi Street, Nyeri)
- Murang'a (Murang'a Town)
- Kirinyaga (Kerugoya Town)

#### Rift Valley (5 centres)
- Eldoret (Uasin Gishu)
- Nakuru (Moi Road, Nakuru)
- Naivasha (Nakuru County)
- Kapsabet (Nandi County)
- Kericho (Kericho Town)

#### Western Kenya (4 centres)
- Kakamega (Kakamega Town)
- Bungoma (Bungoma Town)
- Kisumu (Kisumu Town)
- Siaya (Siaya Town)

#### Eastern Kenya (4 centres)
- Meru (Meru Town)
- Embu (Embu Town)
- Machakos (Machakos Town)
- Isiolo (Isiolo Town)

#### Coast Region (3 centres)
- Mombasa (Mombasa Town)
- Kilifi (Kilifi Town)
- Lamu (Lamu Town)

#### Northeastern Kenya (2 centres)
- Garissa (Garissa Town)
- Wajir (Wajir Town)

**Note**: To complete all 57 centres, add remaining centres following the same pattern.

### Government Services (10 Services)

Based on frontend analysis (`src/pages/Services.tsx` and `src/constants/services.ts`):

1. **NHIF Health Insurance**
   - Category: Health
   - Cost: KES 500/month (minimum)
   - Processing: 2 hours
   - Completion Rate: 89.5%
   - Satisfaction: 4.3/5

2. **KRA Tax Services**
   - Category: Finance
   - Cost: Free
   - Processing: 1 hour (instant PIN)
   - Completion Rate: 92.0%
   - Satisfaction: 4.4/5

3. **National ID**
   - Category: Identity
   - Cost: KES 1,000
   - Processing: 21 days
   - Completion Rate: 85.0%
   - Satisfaction: 4.2/5

4. **Business Registration**
   - Category: Business
   - Cost: KES 1,050
   - Processing: 7 days
   - Completion Rate: 88.0%
   - Satisfaction: 4.3/5

5. **Birth Certificate**
   - Category: Identity
   - Cost: KES 200
   - Processing: 14 days
   - Completion Rate: 87.5%
   - Satisfaction: 4.2/5

6. **Passport Services**
   - Category: Travel
   - Cost: KES 4,500
   - Processing: 21 days
   - Completion Rate: 90.0%
   - Satisfaction: 4.4/5

7. **Huduma Number**
   - Category: Identity
   - Cost: Free
   - Processing: 1 hour
   - Completion Rate: 91.0%
   - Satisfaction: 4.5/5

8. **NSSF Pension**
   - Category: Finance
   - Cost: KES 200
   - Processing: 7 days
   - Completion Rate: 85.0%
   - Satisfaction: 4.1/5

9. **Driving License Services (NTSA)**
   - Category: Transport
   - Cost: KES 3,000
   - Processing: 14 days
   - Completion Rate: 90.0%
   - Satisfaction: 4.3/5

10. **Police Clearance Certificate**
    - Category: Security
    - Cost: KES 1,000
    - Processing: 14 days
    - Completion Rate: 88.5%
    - Satisfaction: 4.2/5

### Service Steps

Detailed step-by-step guidance for:
- **NHIF Registration** (4 steps)
- **KRA PIN Application** (4 steps)
- **National ID Application** (5 steps)

## Usage

### Prerequisites
1. Database schema must be created first
2. Run `create_schema_without_pgvector.sql` before this script
3. PostgreSQL database `afroken_llm_db` must exist

### Running the Script

```bash
# Using psql command line
psql -U afroken -d afroken_llm_db -f afroken_llm_seed_data.sql

# Or from psql prompt
\i afroken_llm_seed_data.sql
```

### Verifying Data

```sql
-- Check Huduma Centres
SELECT COUNT(*) FROM huduma_centres;
-- Should return 28+

-- Check Services
SELECT name, category, completion_rate FROM services;
-- Should return 10 services

-- Check Service Steps
SELECT s.name, COUNT(ss.id) as step_count 
FROM services s 
LEFT JOIN service_steps ss ON s.id = ss.service_id 
GROUP BY s.name;
-- Should show steps for NHIF, KRA, and National ID
```

## Data Structure

### Huduma Centres Fields
- **Location**: County, Sub-County, Town, GPS coordinates
- **Contact**: Phone, Email
- **Services**: JSON array of services offered
- **Hours**: JSON object with daily operating hours
- **Facilities**: JSON array (parking, wifi, disabled_access, etc.)
- **Metrics**: Satisfaction score, average wait time

### Services Fields
- **Basic Info**: Name, Category, Description
- **Cost**: Amount in KES, Currency
- **Timeline**: Processing days/hours
- **Requirements**: JSON array of required documents
- **Eligibility**: JSON object with criteria
- **Agency Info**: Government agency details
- **Metrics**: Completion rate, satisfaction score

### Service Steps Fields
- **Step Info**: Number, Title, Description
- **Guidance**: Tips and notes
- **Requirements**: Documents needed for this step
- **Time**: Estimated minutes
- **Location**: Where to perform step (huduma_centre, online, both)

## Extending the Data

### Adding More Huduma Centres

```sql
INSERT INTO huduma_centres (name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities, is_active, customer_satisfaction_score, average_wait_time_minutes) VALUES
('Huduma Centre [Name]', 'HC-XXX', '[County]', '[Sub-County]', '[Town]', [lat], [lon], '+254 20 2222XXX', '[email]@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.0, 30);
```

### Adding More Services

```sql
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, requirements, eligibility_criteria, government_agency_name, service_website, completion_rate, satisfaction_score, keywords, is_active) VALUES
('[Service Name]', '[Category]', '[Short Description]', '[Detailed Description]',
 [cost], 'KES', [days], 
 '["Document 1", "Document 2"]'::jsonb,
 '{"criteria": "value"}'::jsonb,
 '[Agency Name]', '[Website URL]', [rate], [score], '[keywords]', true);
```

### Adding Service Steps

```sql
INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, [step_num], '[Title]', '[Description]', '[Tips]',
 '["Doc1"]'::jsonb, [minutes], '[location_type]', '[Instructions]'
FROM services WHERE name = '[Service Name]';
```

## Updating Statistics from Dashboard

To update service statistics based on dashboard analytics:

```sql
-- Update completion rates
UPDATE services 
SET completion_rate = [new_rate],
    satisfaction_score = [new_score],
    average_processing_days = [new_days]
WHERE name = '[Service Name]';

-- Update Huduma Centre metrics
UPDATE huduma_centres 
SET customer_satisfaction_score = [new_score],
    average_wait_time_minutes = [new_wait_time]
WHERE center_code = 'HC-XXX';
```

## Notes

1. **Coordinates**: GPS coordinates are approximate. Update with exact coordinates if available.
2. **Contact Info**: Phone numbers and emails are placeholder format. Update with actual contact details.
3. **Services Offered**: JSON arrays can be extended with more services as needed.
4. **Operating Hours**: Standard hours are 8AM-5PM Mon-Fri, 8AM-1PM Sat. Some centres may vary.
5. **Statistics**: Completion rates and satisfaction scores are initial estimates. Update based on real data.

## Troubleshooting

### Foreign Key Errors
- Ensure services are inserted before service_steps
- Check that service names match exactly in service_steps queries

### Constraint Violations
- Verify GPS coordinates are within Kenya bounds (-35 to 5 lat, 21 to 42 lon)
- Check satisfaction scores are between 0 and 5
- Ensure wait times are non-negative

### Duplicate Key Errors
- Service names must be unique
- Center codes must be unique
- Check for existing data before inserting

## Next Steps

1. Run the seed data script
2. Verify data insertion
3. Test queries from frontend/backend
4. Update statistics based on real usage data
5. Add remaining Huduma Centres (to reach 57 total)
6. Add service steps for remaining services
7. Populate additional tables (users, conversations, etc.) as needed


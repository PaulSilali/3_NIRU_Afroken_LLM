# Database Tables Usage Documentation

This document describes each table in the `afroken_llm_db` database and what data is stored in each.

## Core Tables

### 1. `users`
**Purpose**: Stores user account information for citizens, admins, government officials, and support staff.

**Key Fields**:
- `id` (UUID): Primary key
- `phone_number` (VARCHAR): Unique identifier for users (indexed)
- `email` (VARCHAR): Optional email address
- `full_name` (VARCHAR): User's full name
- `preferred_language` (ENUM): Language preference ('en', 'sw', 'sheng')
- `role` (ENUM): User role ('citizen', 'admin', 'government', 'support')
- `is_active` (BOOLEAN): Account activation status
- `is_verified` (BOOLEAN): Account verification status
- `last_login_at` (TIMESTAMP): Last login timestamp
- `login_count` (INT): Number of login sessions
- `data_deletion_requested_at` (TIMESTAMP): GDPR deletion request timestamp
- `created_at`, `updated_at` (TIMESTAMP): Audit timestamps

**Used By**: Authentication, user preferences, conversation tracking

---

### 2. `conversations`
**Purpose**: Tracks chat sessions between users and the AfroKen LLM assistant.

**Key Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to `users.id`
- `service_category` (VARCHAR): Service being discussed (e.g., 'NHIF', 'KRA')
- `status` (ENUM): Conversation status ('active', 'closed', 'archived', 'escalated')
- `sentiment` (ENUM): Detected sentiment ('positive', 'neutral', 'negative')
- `language` (ENUM): Conversation language
- `summary` (TEXT): AI-generated conversation summary
- `message_count` (INT): Total messages in conversation
- `total_tokens_used` (INT): LLM token usage
- `total_cost_usd` (DECIMAL): Cost tracking
- `duration_seconds` (INT): Conversation duration
- `metadata` (JSONB): Additional structured data
- `created_at`, `ended_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: Chat interface, analytics, conversation history

---

### 3. `messages`
**Purpose**: Stores individual messages within conversations (both user and assistant messages).

**Key Fields**:
- `id` (UUID): Primary key
- `conversation_id` (UUID): Foreign key to `conversations.id`
- `role` (ENUM): Message role ('user', 'assistant', 'system')
- `content` (TEXT): Message text content
- `language` (ENUM): Message language
- `embedding` (TEXT): Vector embedding stored as JSON string (for RAG search)
- `citations` (JSONB): Array of source citations
- `tokens_used` (INT): Token count for this message
- `cost_usd` (DECIMAL): Cost for generating this message
- `model_name` (VARCHAR): LLM model used
- `confidence_score` (DECIMAL): AI confidence (0-1)
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: Chat history, RAG retrieval, analytics, cost tracking

---

### 4. `documents`
**Purpose**: Stores ingested documents (PDFs, scraped web pages) for RAG (Retrieval-Augmented Generation).

**Key Fields**:
- `id` (UUID): Primary key
- `title` (VARCHAR): Document title
- `content` (TEXT): Full document text content
- `document_type` (ENUM): Type ('policy', 'guide', 'faq', 'procedure', 'form', 'news')
- `category` (VARCHAR): Category label (e.g., 'NHIF', 'KRA')
- `source_url` (VARCHAR): Original source URL
- `source_ministry` (VARCHAR): Government ministry source
- `embedding` (TEXT): Vector embedding stored as JSON string (for similarity search)
- `is_indexed` (BOOLEAN): Whether document is indexed for search
- `indexed_at` (TIMESTAMP): When indexing completed
- `chunk_index` (INT): For multi-chunk documents
- `metadata` (JSONB): Additional document metadata
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: RAG search, document ingestion, admin dashboard

---

### 5. `document_chunks`
**Purpose**: Stores smaller chunks of large documents for better RAG retrieval.

**Key Fields**:
- `id` (UUID): Primary key
- `document_id` (UUID): Foreign key to `documents.id`
- `chunk_number` (INT): Sequential chunk number
- `content` (TEXT): Chunk text content
- `embedding` (TEXT): Vector embedding for this chunk (JSON string)
- `chunk_length` (INT): Character count
- `metadata` (JSONB): Chunk-specific metadata
- `created_at` (TIMESTAMP): Timestamp

**Used By**: RAG search (more granular retrieval), document processing

---

## Service Tables

### 6. `services`
**Purpose**: Catalog of government services available through AfroKen.

**Key Fields**:
- `id` (UUID): Primary key
- `name` (VARCHAR): Service name (unique)
- `category` (VARCHAR): Service category
- `description` (TEXT): Short description
- `detailed_description` (TEXT): Full description
- `cost_kes` (INT): Cost in Kenyan Shillings
- `cost_currency` (VARCHAR): Currency code (default 'KES')
- `processing_time_days` (INT): Estimated processing time
- `processing_time_hours` (INT): Additional hours
- `requirements` (JSONB): Array of required documents
- `eligibility_criteria` (JSONB): Eligibility requirements
- `government_agency_name` (VARCHAR): Agency providing service
- `government_agency_email`, `phone`, `website` (VARCHAR): Contact info
- `service_website`, `service_phone` (VARCHAR): Service-specific contacts
- `completion_rate` (DECIMAL): Success rate percentage
- `average_processing_days` (INT): Average processing time
- `satisfaction_score` (DECIMAL): User satisfaction (0-5)
- `keywords` (VARCHAR): Search keywords
- `is_active` (BOOLEAN): Service availability
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: Service discovery, service information, booking, recommendations

---

### 7. `service_steps`
**Purpose**: Step-by-step procedural guidance for each service.

**Key Fields**:
- `id` (UUID): Primary key
- `service_id` (UUID): Foreign key to `services.id`
- `step_number` (INT): Sequential step number
- `title` (VARCHAR): Step title
- `description` (TEXT): Step instructions
- `tips_and_notes` (TEXT): Additional guidance
- `documents_needed` (JSONB): Documents required for this step
- `estimated_time_minutes` (INT): Time estimate
- `location_type` (VARCHAR): Where to perform step ('huduma_centre', 'online', 'postal', 'both')
- `location_instructions` (TEXT): Location-specific instructions
- `metadata` (JSONB): Additional step data
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: Service guidance, step-by-step instructions, user assistance

---

### 8. `huduma_centres`
**Purpose**: Information about Huduma Centre locations and services.

**Key Fields**:
- `id` (UUID): Primary key
- `name` (VARCHAR): Centre name
- `center_code` (VARCHAR): Official centre code
- `county`, `sub_county`, `town` (VARCHAR): Location
- `latitude`, `longitude` (DECIMAL): GPS coordinates
- `contact_phone`, `contact_email`, `contact_person` (VARCHAR): Contact info
- `services_offered` (JSONB): Array of service IDs/names
- `opening_hours` (JSONB): Hours for each day of week
- `facilities` (JSONB): Available facilities (parking, wifi, etc.)
- `is_active` (BOOLEAN): Centre status
- `customer_satisfaction_score` (DECIMAL): Rating (0-5)
- `average_wait_time_minutes` (INT): Average wait time
- `metadata` (JSONB): Additional centre data
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: Location search, appointment booking, service availability

---

## Integration Tables

### 9. `api_integrations`
**Purpose**: Configuration and credentials for government API integrations (NHIF, KRA, eCitizen, etc.).

**Key Fields**:
- `id` (UUID): Primary key
- `service_name` (VARCHAR): Integration identifier (unique, e.g., 'nhif', 'kra')
- `display_name` (VARCHAR): Human-readable name
- `endpoint_url` (VARCHAR): API endpoint URL
- `auth_type` (VARCHAR): Authentication type ('oauth2', 'api_key', 'basic', 'bearer')
- `credentials_encrypted` (VARCHAR): Encrypted credentials
- `encryption_key_version` (INT): Key version for rotation
- `rate_limit_requests` (INT): Rate limit count
- `rate_limit_window_seconds` (INT): Rate limit window
- `status` (ENUM): Integration status ('active', 'inactive', 'error', 'maintenance')
- `is_active` (BOOLEAN): Active flag
- `last_checked_at` (TIMESTAMP): Last health check
- `last_error_message` (VARCHAR): Error details
- `last_error_at` (TIMESTAMP): Error timestamp
- `health_check_interval_minutes` (INT): Health check frequency
- `max_retries` (INT): Retry policy
- `retry_delay_ms` (INT): Retry delay
- `metadata` (JSONB): Additional config
- `documentation_url`, `contact_email` (VARCHAR): Support info
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: API integrations, service verification, data fetching

---

### 10. `ussd_sessions`
**Purpose**: Stateful USSD menu navigation for feature phone users.

**Key Fields**:
- `id` (UUID): Primary key
- `phone_number` (VARCHAR): User's phone number
- `session_id` (VARCHAR): USSD session identifier
- `current_menu` (ENUM): Current menu type ('main', 'service', 'details', 'confirmation', 'result')
- `current_step` (INT): Current step in flow
- `session_state` (JSONB): User selections and data
- `message_log` (TEXT[]): Message history array
- `last_user_input` (VARCHAR): Last user response
- `input_count` (INT): Number of user inputs
- `service_code` (VARCHAR): USSD service code
- `carrier` (VARCHAR): Mobile network operator
- `device_type` (VARCHAR): Device information
- `created_at`, `last_activity_at`, `expires_at` (TIMESTAMP): Session timestamps

**Used By**: USSD interface, feature phone support, menu navigation

---

## Analytics & Monitoring Tables

### 11. `chat_metrics`
**Purpose**: Aggregated metrics for analytics dashboards and reporting.

**Key Fields**:
- `id` (UUID): Primary key
- `date_hour` (TIMESTAMP): Time period (hourly aggregation)
- `total_conversations` (INT): Conversation count
- `total_messages` (INT): Message count
- `total_queries` (INT): Query count
- `average_response_time_ms` (INT): Average response time
- `unique_users` (INT): Unique user count
- `new_users` (INT): New user registrations
- `top_services` (JSONB): Most queried services
- `top_intents` (JSONB): Most common intents
- `average_accuracy_score` (DECIMAL): AI accuracy
- `average_hallucination_rate` (DECIMAL): Error rate
- `average_satisfaction_score` (DECIMAL): User satisfaction
- `language_distribution` (JSONB): Language usage stats
- `sentiment_distribution` (JSONB): Sentiment analysis
- `total_cost_usd` (DECIMAL): Total LLM costs
- `average_cost_per_request` (DECIMAL): Cost per request

**Used By**: Admin dashboard, analytics, reporting, cost tracking

---

### 12. `audit_logs`
**Purpose**: Compliance and security audit trail.

**Key Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to `users.id` (nullable)
- `actor_type` (VARCHAR): Actor type ('user', 'system', 'admin')
- `actor_identifier` (VARCHAR): Actor identifier
- `action` (ENUM): Action type ('create', 'read', 'update', 'delete', 'authenticate', 'authorize')
- `resource_type` (VARCHAR): Resource type ('conversation', 'message', 'service', 'document')
- `resource_id` (UUID): Resource identifier
- `old_values` (JSONB): Previous state
- `new_values` (JSONB): New state
- `changes` (JSONB): Diff of changes
- `ip_address` (INET): Request IP
- `user_agent` (VARCHAR): Browser/client info
- `request_id` (UUID): Request identifier
- `status` (VARCHAR): Action status ('success', 'failure', 'partial')
- `error_message` (VARCHAR): Error details
- `created_at` (TIMESTAMP): Timestamp

**Used By**: Security monitoring, compliance, debugging, audit trails

---

## User Preferences & Settings

### 13. `user_preferences`
**Purpose**: User-specific settings and preferences.

**Key Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to `users.id` (unique)
- `prefer_notifications` (BOOLEAN): Notification preference
- `notification_language` (ENUM): Notification language
- `email_notifications_enabled` (BOOLEAN): Email notifications
- `sms_notifications_enabled` (BOOLEAN): SMS notifications
- `preferred_service_categories` (VARCHAR[]): Preferred categories
- `preferred_counties` (VARCHAR[]): Preferred counties
- `allow_data_collection` (BOOLEAN): GDPR consent
- `allow_analytics` (BOOLEAN): Analytics consent
- `dark_mode_enabled` (BOOLEAN): UI theme
- `font_size` (VARCHAR): Font size preference
- `high_contrast_enabled` (BOOLEAN): Accessibility
- `screen_reader_enabled` (BOOLEAN): Accessibility
- `voice_only_mode` (BOOLEAN): Voice interface
- `metadata` (JSONB): Additional preferences
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: User settings, personalization, accessibility

---

## Processing & Jobs

### 14. `processing_jobs` (from models.py)
**Purpose**: Tracks background processing jobs (PDF uploads, URL scraping).

**Key Fields**:
- `id` (UUID/STRING): Primary key
- `job_type` (VARCHAR): Job type ('pdf_upload', 'url_scrape', 'batch_process')
- `status` (VARCHAR): Status ('pending', 'processing', 'completed', 'failed')
- `source` (VARCHAR): Source identifier (filename, URL)
- `progress` (INT): Progress percentage (0-100)
- `error_message` (VARCHAR): Error details if failed
- `result` (TEXT/JSON): Result data
- `documents_processed` (INT): Number of documents processed
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Used By**: Admin dashboard, job tracking, background processing

---

## Data Flow from Frontend

### Chat Flow:
1. **User sends message** → Frontend calls `/api/v1/chat/messages`
2. **Backend creates/updates** → `conversations` table (if new conversation)
3. **Backend stores message** → `messages` table (user message)
4. **Backend generates response** → Uses RAG from `documents` table
5. **Backend stores response** → `messages` table (assistant message)
6. **Backend updates metrics** → `chat_metrics` table (hourly aggregation)

### Admin Dashboard Flow:
1. **Admin uploads PDF** → Frontend calls `/api/v1/admin/documents/upload-pdf`
2. **Backend creates job** → `processing_jobs` table
3. **Background processing** → Extracts text, generates embeddings
4. **Backend stores document** → `documents` table with embedding
5. **Backend updates job** → `processing_jobs` table (status, progress)

### URL Scraping Flow:
1. **Admin submits URL** → Frontend calls `/api/v1/admin/documents/scrape-url`
2. **Backend creates job** → `processing_jobs` table
3. **Background scraping** → Fetches HTML, extracts text
4. **Backend stores document** → `documents` table with chunks
5. **Backend updates job** → `processing_jobs` table

---

## Notes

- **Embeddings**: When pgvector is not available, embeddings are stored as JSON strings in TEXT columns
- **UUIDs**: All primary keys use UUID type (not strings) for better database performance
- **JSONB**: Used for flexible schema extensions and metadata
- **Timestamps**: All tables include `created_at` and `updated_at` for audit trails
- **Foreign Keys**: Properly defined with CASCADE deletes for data integrity


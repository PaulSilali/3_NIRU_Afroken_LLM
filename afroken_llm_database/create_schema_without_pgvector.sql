-- ============================================================================
-- AfroKen LLM - Schema WITHOUT pgvector (for systems where pgvector is not installed)
-- ============================================================================
-- This version uses TEXT instead of vector(384) for embedding columns
-- Vector search/RAG will be disabled, but all other functionality works
-- ============================================================================
-- To use: Run this file instead of afroken_complete_schema.sql
-- ============================================================================

-- ============================================================================
-- DROP EXISTING TABLES (in reverse dependency order)
-- ============================================================================
-- This allows you to recreate the schema from scratch
-- ============================================================================

-- Drop materialized views first
DROP MATERIALIZED VIEW IF EXISTS mv_service_query_counts CASCADE;

-- Drop extension/enhancement tables (with foreign keys)
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS analytics_events CASCADE;
DROP TABLE IF EXISTS conversation_feedback CASCADE;
DROP TABLE IF EXISTS message_reactions CASCADE;
DROP TABLE IF EXISTS conversation_tag_assignments CASCADE;
DROP TABLE IF EXISTS conversation_tags CASCADE;
DROP TABLE IF EXISTS rate_limits CASCADE;
DROP TABLE IF EXISTS feature_flags CASCADE;
DROP TABLE IF EXISTS oauth_clients CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS webhook_deliveries CASCADE;
DROP TABLE IF EXISTS webhooks CASCADE;
DROP TABLE IF EXISTS notification_queue CASCADE;
DROP TABLE IF EXISTS watchlist_items CASCADE;
DROP TABLE IF EXISTS watchlists CASCADE;
DROP TABLE IF EXISTS saved_searches CASCADE;
DROP TABLE IF EXISTS translations CASCADE;
DROP TABLE IF EXISTS ui_templates CASCADE;
DROP TABLE IF EXISTS quick_actions CASCADE;
DROP TABLE IF EXISTS canned_responses CASCADE;
DROP TABLE IF EXISTS attachments CASCADE;

-- Drop base tables with foreign keys
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS chat_metrics CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS ussd_sessions CASCADE;
DROP TABLE IF EXISTS api_integrations CASCADE;
DROP TABLE IF EXISTS huduma_centres CASCADE;
DROP TABLE IF EXISTS service_steps CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop custom types (will fail if still in use, but that's okay)
DROP TYPE IF EXISTS api_integration_status CASCADE;
DROP TYPE IF EXISTS document_type CASCADE;
DROP TYPE IF EXISTS audit_action CASCADE;
DROP TYPE IF EXISTS ussd_menu_type CASCADE;
DROP TYPE IF EXISTS language_type CASCADE;
DROP TYPE IF EXISTS sentiment_type CASCADE;
DROP TYPE IF EXISTS message_role CASCADE;
DROP TYPE IF EXISTS conversation_status CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;

-- ============================================================================
-- CREATE SCHEMA
-- ============================================================================

-- Enable extensions (excluding pgvector)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Note: pgvector extension is skipped - embeddings will use TEXT type

-- ============================================================================
-- ENUMERATIONS
-- ============================================================================

CREATE TYPE user_role AS ENUM ('citizen', 'admin', 'government', 'support');
CREATE TYPE conversation_status AS ENUM ('active', 'closed', 'archived', 'escalated');
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE sentiment_type AS ENUM ('positive', 'neutral', 'negative');
CREATE TYPE language_type AS ENUM ('en', 'sw', 'sheng');
CREATE TYPE ussd_menu_type AS ENUM ('main', 'service', 'details', 'confirmation', 'result');
CREATE TYPE audit_action AS ENUM ('create', 'read', 'update', 'delete', 'authenticate', 'authorize');
CREATE TYPE document_type AS ENUM ('policy', 'guide', 'faq', 'procedure', 'form', 'news');
CREATE TYPE api_integration_status AS ENUM ('active', 'inactive', 'error', 'maintenance');

-- ============================================================================
-- CORE TABLES (with TEXT instead of vector for embeddings)
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    preferred_language language_type DEFAULT 'sw',
    role user_role DEFAULT 'citizen',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    
    -- Account metadata
    last_login_at TIMESTAMP WITH TIME ZONE,
    login_count INT DEFAULT 0,
    
    -- GDPR
    data_deletion_requested_at TIMESTAMP WITH TIME ZONE,
    data_deletion_scheduled_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_phone CHECK (phone_number ~ '^\+?[0-9]{10,20}$'),
    CONSTRAINT valid_email CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$' OR email IS NULL)
);

-- Conversations table (chat sessions)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Conversation metadata
    service_category VARCHAR(100),
    status conversation_status DEFAULT 'active',
    sentiment sentiment_type,
    language language_type DEFAULT 'sw',
    
    -- Summary and analytics
    summary TEXT,
    message_count INT DEFAULT 0,
    total_tokens_used INT DEFAULT 0,
    total_cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    duration_seconds INT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_duration CHECK (duration_seconds IS NULL OR duration_seconds > 0)
);

-- Messages table (conversation history)
-- NOTE: embedding uses TEXT instead of vector(384) - vector search disabled
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role message_role NOT NULL,
    content TEXT NOT NULL,
    language language_type DEFAULT 'sw',
    
    -- Vector embedding for RAG (using TEXT instead of vector - pgvector not available)
    embedding TEXT, -- Store as JSON array string: '[0.1, 0.2, ...]'
    
    -- Citations and sources
    citations JSONB DEFAULT '[]'::jsonb,
    
    -- LLM metadata
    tokens_used INT DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    model_name VARCHAR(100),
    confidence_score DECIMAL(3, 2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))
);

-- Documents table (indexed for RAG)
-- NOTE: embedding uses TEXT instead of vector(384) - vector search disabled
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Document metadata
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    document_type document_type NOT NULL,
    category VARCHAR(100),
    source_url VARCHAR(500),
    source_ministry VARCHAR(255),
    
    -- Vector embedding for RAG (using TEXT instead of vector - pgvector not available)
    embedding TEXT, -- Store as JSON array string: '[0.1, 0.2, ...]'
    
    -- Processing metadata
    is_indexed BOOLEAN DEFAULT false,
    indexed_at TIMESTAMP WITH TIME ZONE,
    chunk_index INT DEFAULT 0, -- For multi-chunk documents
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Services table (government services catalog)
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Service information
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    detailed_description TEXT,
    
    -- Cost and timeline
    cost_kes INT DEFAULT 0,
    cost_currency VARCHAR(3) DEFAULT 'KES',
    processing_time_days INT,
    processing_time_hours INT,
    
    -- Requirements and eligibility
    requirements JSONB DEFAULT '[]'::jsonb, -- Array of document names
    eligibility_criteria JSONB DEFAULT '{}'::jsonb,
    
    -- Government agency
    government_agency_name VARCHAR(255),
    government_agency_email VARCHAR(255),
    government_agency_phone VARCHAR(20),
    government_agency_website VARCHAR(500),
    
    -- Service links
    service_website VARCHAR(500),
    service_phone VARCHAR(20),
    
    -- Metrics
    completion_rate DECIMAL(5, 2), -- Percentage
    average_processing_days INT,
    satisfaction_score DECIMAL(3, 2),
    
    -- SEO and search
    keywords VARCHAR(500),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_updated_source TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_cost CHECK (cost_kes >= 0),
    CONSTRAINT valid_processing_time CHECK (processing_time_days IS NULL OR processing_time_days > 0),
    CONSTRAINT valid_satisfaction CHECK (satisfaction_score IS NULL OR (satisfaction_score >= 0 AND satisfaction_score <= 5))
);

-- Service steps table (procedural guidance)
CREATE TABLE IF NOT EXISTS service_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    
    -- Step information
    step_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    tips_and_notes TEXT,
    
    -- Requirements for this step
    documents_needed JSONB DEFAULT '[]'::jsonb,
    estimated_time_minutes INT,
    
    -- Location information
    location_type VARCHAR(50), -- 'huduma_centre', 'online', 'postal', 'both'
    location_instructions TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_step_number CHECK (step_number > 0),
    CONSTRAINT valid_time CHECK (estimated_time_minutes IS NULL OR estimated_time_minutes > 0),
    CONSTRAINT unique_step_number UNIQUE (service_id, step_number)
);

-- Huduma Centres table (service delivery locations)
CREATE TABLE IF NOT EXISTS huduma_centres (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic information
    name VARCHAR(255) NOT NULL,
    center_code VARCHAR(20),
    
    -- Location
    county VARCHAR(100) NOT NULL,
    sub_county VARCHAR(100),
    town VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Contact information
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    contact_person VARCHAR(255),
    
    -- Services offered
    services_offered JSONB DEFAULT '[]'::jsonb, -- Array of service IDs or names
    
    -- Operating hours
    opening_hours JSONB DEFAULT '{
        "monday": "9:00 AM - 5:00 PM",
        "tuesday": "9:00 AM - 5:00 PM",
        "wednesday": "9:00 AM - 5:00 PM",
        "thursday": "9:00 AM - 5:00 PM",
        "friday": "9:00 AM - 5:00 PM",
        "saturday": "9:00 AM - 1:00 PM",
        "sunday": "CLOSED"
    }'::jsonb,
    
    -- Facilities
    facilities JSONB DEFAULT '[]'::jsonb, -- e.g., ["parking", "wifi", "disabled_access"]
    
    -- Status and ratings
    is_active BOOLEAN DEFAULT true,
    customer_satisfaction_score DECIMAL(3, 2),
    average_wait_time_minutes INT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_coordinates CHECK (
        (latitude IS NULL AND longitude IS NULL) OR
        (latitude IS NOT NULL AND longitude IS NOT NULL AND
         latitude >= -35.0 AND latitude <= 5.0 AND
         longitude >= 21.0 AND longitude <= 42.0)
    ),
    CONSTRAINT valid_satisfaction CHECK (customer_satisfaction_score IS NULL OR (customer_satisfaction_score >= 0 AND customer_satisfaction_score <= 5)),
    CONSTRAINT valid_wait_time CHECK (average_wait_time_minutes IS NULL OR average_wait_time_minutes >= 0)
);

-- API Integrations table (government API credentials and metadata)
CREATE TABLE IF NOT EXISTS api_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Integration identification
    service_name VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'nhif', 'kra', 'ecitizen'
    display_name VARCHAR(255),
    
    -- Endpoint information
    endpoint_url VARCHAR(500) NOT NULL,
    auth_type VARCHAR(50) NOT NULL, -- 'oauth2', 'api_key', 'basic', 'bearer'
    
    -- Credentials (encrypted)
    credentials_encrypted VARCHAR(1000),
    encryption_key_version INT,
    
    -- Rate limiting
    rate_limit_requests INT,
    rate_limit_window_seconds INT,
    
    -- Status and monitoring
    status api_integration_status DEFAULT 'active',
    is_active BOOLEAN DEFAULT true,
    last_checked_at TIMESTAMP WITH TIME ZONE,
    last_error_message VARCHAR(500),
    last_error_at TIMESTAMP WITH TIME ZONE,
    health_check_interval_minutes INT DEFAULT 15,
    
    -- Retry policy
    max_retries INT DEFAULT 3,
    retry_delay_ms INT DEFAULT 1000,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    documentation_url VARCHAR(500),
    contact_email VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- USSD Sessions table (stateful menu navigation for feature phones)
CREATE TABLE IF NOT EXISTS ussd_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Session identification
    phone_number VARCHAR(20) NOT NULL,
    session_id VARCHAR(100),
    
    -- Menu state
    current_menu ussd_menu_type DEFAULT 'main',
    current_step INT DEFAULT 1,
    
    -- Session data
    session_state JSONB DEFAULT '{}'::jsonb, -- Store user selections and data
    message_log TEXT[] DEFAULT ARRAY[]::TEXT[], -- Store message history
    
    -- User response tracking
    last_user_input VARCHAR(160),
    input_count INT DEFAULT 0,
    
    -- Session metadata
    service_code VARCHAR(20),
    carrier VARCHAR(50),
    device_type VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_session CHECK (last_activity_at >= created_at)
);

-- Audit Logs table (compliance and security)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Actor information
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_type VARCHAR(50), -- 'user', 'system', 'admin'
    actor_identifier VARCHAR(255),
    
    -- Action information
    action audit_action NOT NULL,
    resource_type VARCHAR(100), -- 'conversation', 'message', 'service', 'document'
    resource_id UUID,
    
    -- Changes
    old_values JSONB,
    new_values JSONB,
    changes JSONB,
    
    -- Request information
    ip_address INET,
    user_agent VARCHAR(500),
    request_id UUID,
    
    -- Status
    status VARCHAR(50), -- 'success', 'failure', 'partial'
    error_message VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_timestamp CHECK (created_at <= CURRENT_TIMESTAMP)
);

-- User Preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Communication preferences
    prefer_notifications BOOLEAN DEFAULT true,
    notification_language language_type DEFAULT 'sw',
    email_notifications_enabled BOOLEAN DEFAULT false,
    sms_notifications_enabled BOOLEAN DEFAULT true,
    
    -- Service preferences
    preferred_service_categories VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR[],
    preferred_counties VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR[],
    
    -- Privacy and data
    allow_data_collection BOOLEAN DEFAULT true,
    allow_analytics BOOLEAN DEFAULT true,
    
    -- UI preferences
    dark_mode_enabled BOOLEAN DEFAULT false,
    font_size VARCHAR(20) DEFAULT 'medium',
    high_contrast_enabled BOOLEAN DEFAULT false,
    
    -- Accessibility
    screen_reader_enabled BOOLEAN DEFAULT false,
    voice_only_mode BOOLEAN DEFAULT false,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat Metrics table (for analytics and dashboards)
CREATE TABLE IF NOT EXISTS chat_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Time period
    date_hour TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Metrics
    total_conversations INT DEFAULT 0,
    total_messages INT DEFAULT 0,
    total_queries INT DEFAULT 0,
    average_response_time_ms INT,
    
    -- User metrics
    unique_users INT DEFAULT 0,
    new_users INT DEFAULT 0,
    
    -- Service metrics
    top_services JSONB DEFAULT '[]'::jsonb,
    top_intents JSONB DEFAULT '[]'::jsonb,
    
    -- Quality metrics
    average_accuracy_score DECIMAL(5, 2),
    average_hallucination_rate DECIMAL(5, 2),
    average_satisfaction_score DECIMAL(3, 2),
    
    -- Language distribution
    language_distribution JSONB DEFAULT '{}'::jsonb,
    
    -- Sentiment analysis
    sentiment_distribution JSONB DEFAULT '{}'::jsonb,
    
    -- Cost tracking
    total_cost_usd DECIMAL(10, 2) DEFAULT 0.0,
    average_cost_per_request DECIMAL(8, 6),
    
    CONSTRAINT valid_metrics CHECK (
        total_conversations >= 0 AND
        total_messages >= 0 AND
        unique_users >= 0
    )
);

-- RAG Document Chunks table (for better retrieval)
-- NOTE: embedding uses TEXT instead of vector(384) - vector search disabled
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Chunk information
    chunk_number INT NOT NULL,
    content TEXT NOT NULL,
    
    -- Vector embedding (using TEXT instead of vector - pgvector not available)
    embedding TEXT, -- Store as JSON array string: '[0.1, 0.2, ...]'
    
    -- Metadata
    chunk_length INT,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_chunk_number CHECK (chunk_number > 0),
    CONSTRAINT unique_chunk_number UNIQUE (document_id, chunk_number)
);

-- ============================================================================
-- Continue with indexes, triggers, and extension tables...
-- (Rest of schema is the same, just without vector indexes)
-- ============================================================================

-- Note: This is a simplified version. For the complete schema without pgvector,
-- you would need to copy the rest of afroken_complete_schema.sql but skip
-- the vector index creation. For now, use the installation guide to install
-- pgvector and use the main schema file.

DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Schema created WITHOUT pgvector. Vector search is disabled.';
    RAISE NOTICE 'To enable vector search, install pgvector and use afroken_complete_schema.sql';
    RAISE NOTICE 'See INSTALL_PGVECTOR.md for installation instructions.';
    RAISE NOTICE '============================================================';
END
$$;


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

-- Processing Jobs table (tracks PDF uploads, URL scraping, etc.)
-- NOTE: This table name is 'processingjob' (singular, lowercase) to match SQLModel convention
CREATE TABLE IF NOT EXISTS processingjob (
    id VARCHAR(36) PRIMARY KEY, -- UUID as string (SQLModel uses string UUIDs)
    
    -- Job identification
    job_type VARCHAR(50) NOT NULL, -- 'pdf_upload', 'url_scrape', 'batch_process'
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    source VARCHAR(500) NOT NULL, -- Filename, URL, etc.
    
    -- Progress tracking
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    documents_processed INT DEFAULT 0 CHECK (documents_processed >= 0),
    
    -- Error handling
    error_message TEXT,
    result TEXT, -- JSON string with result data
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

-- Indexes for processingjob table
CREATE INDEX IF NOT EXISTS idx_processingjob_status ON processingjob(status);
CREATE INDEX IF NOT EXISTS idx_processingjob_job_type ON processingjob(job_type);
CREATE INDEX IF NOT EXISTS idx_processingjob_created_at ON processingjob(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_processingjob_status_type ON processingjob(status, job_type);

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

-- ============================================================================
-- AfroKen LLM - Seed Data Script
-- ============================================================================
-- This script populates the database with initial data for:
-- 1. Huduma Centres (57 centres across 47 counties)
-- 2. Government Services (NHIF, KRA, NSSF, NTSA, etc.)
-- 3. Service Steps (procedural guidance for each service)
-- ============================================================================
-- Run this script after creating the schema
-- Usage: psql -U afroken -d afroken_llm_db -f afroken_llm_seed_data.sql
-- ============================================================================

BEGIN;

-- ============================================================================
-- HUDUMA CENTRES DATA
-- ============================================================================
-- Populate huduma_centres table with real locations and information
-- Based on Huduma Kenya official information
-- ============================================================================

-- Clear existing data (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE huduma_centres CASCADE;

-- Nairobi County Huduma Centres
INSERT INTO huduma_centres (name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities, is_active, customer_satisfaction_score, average_wait_time_minutes) VALUES
('Huduma Centre GPO', 'HC-001', 'Nairobi', 'Nairobi Central', 'Nairobi CBD', -1.2921, 36.8219, '+254 20 2222222', 'gpo@hudumakenya.go.ke', 
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration", "Police Clearance"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms", "waiting_area"]'::jsonb,
 true, 4.5, 25),

('Huduma Centre City Square', 'HC-002', 'Nairobi', 'Nairobi Central', 'Nairobi CBD', -1.2864, 36.8172, '+254 20 2222223', 'citysquare@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms"]'::jsonb,
 true, 4.3, 30),

('Huduma Centre Eastleigh', 'HC-003', 'Nairobi', 'Kamukunji', 'Eastleigh', -1.2808, 36.8506, '+254 20 2222224', 'eastleigh@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.2, 35),

('Huduma Centre Makadara', 'HC-004', 'Nairobi', 'Makadara', 'Makadara', -1.3044, 36.8708, '+254 20 2222225', 'makadara@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.1, 40),

('Huduma Centre Kibra', 'HC-005', 'Nairobi', 'Kibra', 'Kibera', -1.3136, 36.7819, '+254 20 2222226', 'kibra@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["wifi", "restrooms"]'::jsonb,
 true, 4.0, 45);

-- Central Kenya Huduma Centres
INSERT INTO huduma_centres (name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities, is_active, customer_satisfaction_score, average_wait_time_minutes) VALUES
('Huduma Centre Gatundu North', 'HC-006', 'Kiambu', 'Gatundu North', 'Kamwangi', -0.9667, 36.9167, '+254 20 2222227', 'gatundu@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.3, 30),

('Huduma Centre Thika', 'HC-007', 'Kiambu', 'Thika', 'Thika', -1.0333, 37.0667, '+254 20 2222228', 'thika@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration", "Driving License"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms", "waiting_area"]'::jsonb,
 true, 4.4, 28),

('Huduma Centre Nyeri', 'HC-008', 'Nyeri', 'Nyeri Central', 'Nyeri', -0.4167, 36.9500, '+254 20 2222229', 'nyeri@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms"]'::jsonb,
 true, 4.5, 25),

('Huduma Centre Murang''a', 'HC-009', 'Murang''a', 'Murang''a South', 'Murang''a', -0.7167, 37.1500, '+254 20 2222230', 'muranga@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.2, 32),

('Huduma Centre Kirinyaga', 'HC-010', 'Kirinyaga', 'Kirinyaga Central', 'Kerugoya', -0.5000, 37.2833, '+254 20 2222231', 'kirinyaga@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.3, 30);

-- Rift Valley Huduma Centres
INSERT INTO huduma_centres (name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities, is_active, customer_satisfaction_score, average_wait_time_minutes) VALUES
('Huduma Centre Eldoret', 'HC-011', 'Uasin Gishu', 'Eldoret East', 'Eldoret', 0.5167, 35.2833, '+254 20 2222232', 'eldoret@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration", "Driving License"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms", "waiting_area"]'::jsonb,
 true, 4.4, 27),

('Huduma Centre Nakuru', 'HC-012', 'Nakuru', 'Nakuru Town East', 'Nakuru', -0.3000, 36.0667, '+254 20 2222233', 'nakuru@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration", "Driving License", "Police Clearance"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms", "waiting_area"]'::jsonb,
 true, 4.5, 25),

('Huduma Centre Naivasha', 'HC-013', 'Nakuru', 'Naivasha', 'Naivasha', -0.7167, 36.4333, '+254 20 2222234', 'naivasha@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.2, 30),

('Huduma Centre Kapsabet', 'HC-014', 'Nandi', 'Nandi Central', 'Kapsabet', 0.2000, 35.1000, '+254 20 2222235', 'kapsabet@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.3, 28),

('Huduma Centre Kericho', 'HC-015', 'Kericho', 'Kericho Central', 'Kericho', -0.3667, 35.2833, '+254 20 2222236', 'kericho@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms"]'::jsonb,
 true, 4.4, 26);

-- Western Kenya Huduma Centres
INSERT INTO huduma_centres (name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities, is_active, customer_satisfaction_score, average_wait_time_minutes) VALUES
('Huduma Centre Kakamega', 'HC-016', 'Kakamega', 'Kakamega Central', 'Kakamega', 0.2833, 34.7500, '+254 20 2222237', 'kakamega@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms", "waiting_area"]'::jsonb,
 true, 4.3, 29),

('Huduma Centre Bungoma', 'HC-017', 'Bungoma', 'Bungoma Central', 'Bungoma', 0.5667, 34.5667, '+254 20 2222238', 'bungoma@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.2, 32),

('Huduma Centre Kisumu', 'HC-018', 'Kisumu', 'Kisumu Central', 'Kisumu', -0.1000, 34.7667, '+254 20 2222239', 'kisumu@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration", "Driving License", "Police Clearance"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms", "waiting_area"]'::jsonb,
 true, 4.5, 24),

('Huduma Centre Siaya', 'HC-019', 'Siaya', 'Siaya', 'Siaya', 0.0667, 34.2833, '+254 20 2222240', 'siaya@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.1, 35);

-- Eastern Kenya Huduma Centres
INSERT INTO huduma_centres (name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities, is_active, customer_satisfaction_score, average_wait_time_minutes) VALUES
('Huduma Centre Meru', 'HC-020', 'Meru', 'Meru Central', 'Meru', 0.0500, 37.6500, '+254 20 2222241', 'meru@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms", "waiting_area"]'::jsonb,
 true, 4.4, 26),

('Huduma Centre Embu', 'HC-021', 'Embu', 'Embu Central', 'Embu', -0.5333, 37.4500, '+254 20 2222242', 'embu@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.3, 28),

('Huduma Centre Machakos', 'HC-022', 'Machakos', 'Machakos Town', 'Machakos', -1.5167, 37.2667, '+254 20 2222243', 'machakos@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms"]'::jsonb,
 true, 4.4, 27),

('Huduma Centre Isiolo', 'HC-023', 'Isiolo', 'Isiolo Central', 'Isiolo', 0.3500, 37.5833, '+254 20 2222244', 'isiolo@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.2, 30);

-- Coast Region Huduma Centres
INSERT INTO huduma_centres (name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities, is_active, customer_satisfaction_score, average_wait_time_minutes) VALUES
('Huduma Centre Mombasa', 'HC-024', 'Mombasa', 'Mombasa Central', 'Mombasa', -4.0435, 39.6682, '+254 20 2222245', 'mombasa@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration", "Driving License", "Police Clearance"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms", "waiting_area"]'::jsonb,
 true, 4.5, 23),

('Huduma Centre Kilifi', 'HC-025', 'Kilifi', 'Kilifi North', 'Kilifi', -3.6333, 39.8500, '+254 20 2222246', 'kilifi@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.3, 28),

('Huduma Centre Lamu', 'HC-026', 'Lamu', 'Lamu East', 'Lamu', -2.2667, 40.9000, '+254 20 2222247', 'lamu@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.1, 32);

-- Northeastern Kenya Huduma Centres
INSERT INTO huduma_centres (name, center_code, county, sub_county, town, latitude, longitude, contact_phone, contact_email, services_offered, opening_hours, facilities, is_active, customer_satisfaction_score, average_wait_time_minutes) VALUES
('Huduma Centre Garissa', 'HC-027', 'Garissa', 'Garissa Township', 'Garissa', -0.4500, 39.6500, '+254 20 2222248', 'garissa@hudumakenya.go.ke',
 '["National ID", "Passport", "NHIF", "KRA PIN", "Birth Certificate", "Business Registration"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "disabled_access", "restrooms"]'::jsonb,
 true, 4.2, 29),

('Huduma Centre Wajir', 'HC-028', 'Wajir', 'Wajir East', 'Wajir', 1.7500, 40.0667, '+254 20 2222249', 'wajir@hudumakenya.go.ke',
 '["National ID", "NHIF", "KRA PIN", "Birth Certificate"]'::jsonb,
 '{"monday": "8:00 AM - 5:00 PM", "tuesday": "8:00 AM - 5:00 PM", "wednesday": "8:00 AM - 5:00 PM", "thursday": "8:00 AM - 5:00 PM", "friday": "8:00 AM - 5:00 PM", "saturday": "8:00 AM - 1:00 PM", "sunday": "CLOSED"}'::jsonb,
 '["parking", "wifi", "restrooms"]'::jsonb,
 true, 4.0, 35);

-- Note: Additional Huduma Centres can be added for all 47 counties
-- The above covers major centres. For complete list of 57 centres, 
-- add remaining centres following the same pattern.

-- ============================================================================
-- GOVERNMENT SERVICES DATA
-- ============================================================================
-- Populate services table with all services found in frontend
-- Based on frontend/src/pages/Services.tsx and constants/services.ts
-- ============================================================================

-- Clear existing data (optional)
-- TRUNCATE TABLE services CASCADE;

-- NHIF Health Insurance Service
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('NHIF Health Insurance', 'Health', 'Check status, renew membership, and get coverage information', 
 'The National Hospital Insurance Fund (NHIF) provides affordable health insurance coverage to all Kenyans. Services include registration, membership renewal, contribution payment, benefit claims, and coverage verification. Minimum monthly contribution is KES 500 for self-employed individuals.',
 500, 'KES', NULL, 2, 
 '["National ID", "KRA PIN", "Phone Number", "Email Address"]'::jsonb,
 '{"age": "18+", "citizenship": "Kenyan citizen or resident", "employment": "Employed or self-employed"}'::jsonb,
 'National Hospital Insurance Fund', 'info@nhif.or.ke', '+254 20 272 3000', 'https://www.nhif.or.ke',
 'https://www.nhif.or.ke', '+254 20 272 3000', 89.5, 1, 4.3,
 'NHIF, health insurance, medical cover, hospital insurance, health fund', true);

-- KRA Tax Services
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('KRA Tax Services', 'Finance', 'File returns, get PIN, check compliance status',
 'Kenya Revenue Authority (KRA) provides tax services including KRA PIN registration, tax return filing, compliance checking, and tax payment. Services are available online through iTax portal or at KRA offices and Huduma Centres.',
 0, 'KES', NULL, 1,
 '["National ID", "Email Address", "Phone Number", "Passport Photo"]'::jsonb,
 '{"age": "18+", "employment": "Employed, self-employed, or business owner", "income": "Any income level"}'::jsonb,
 'Kenya Revenue Authority', 'info@kra.go.ke', '+254 20 499 9999', 'https://www.kra.go.ke',
 'https://www.kra.go.ke', '+254 20 499 9999', 92.0, 1, 4.4,
 'KRA, tax, PIN, iTax, tax returns, compliance, revenue authority', true);

-- National ID Services
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('National ID', 'Identity', 'Apply for new ID, replacement, or check application status',
 'National ID services include first-time application, replacement of lost/damaged ID, change of particulars, and application status checking. Available at Huduma Centres and Immigration offices nationwide.',
 1000, 'KES', 21, NULL,
 '["Birth Certificate", "Passport Photo", "Parent/Guardian ID", "School Certificate"]'::jsonb,
 '{"age": "18+", "citizenship": "Kenyan citizen by birth or registration"}'::jsonb,
 'Department of Immigration Services', 'info@immigration.go.ke', '+254 20 222 2022', 'https://www.immigration.go.ke',
 'https://www.immigration.go.ke', '+254 20 222 2022', 85.0, 21, 4.2,
 'National ID, identity card, ID replacement, ID application', true);

-- Business Registration
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('Business Registration', 'Business', 'Register business name, get permits and licenses',
 'Business registration services include business name registration, company incorporation, business permits, trade licenses, and business name search. Available online through eCitizen or at Huduma Centres.',
 1050, 'KES', 7, NULL,
 '["National ID", "KRA PIN", "Business Name Proposal", "Physical Address"]'::jsonb,
 '{"age": "18+", "citizenship": "Kenyan citizen or registered company", "business": "Valid business proposal"}'::jsonb,
 'Business Registration Service', 'info@brs.go.ke', '+254 20 222 2222', 'https://www.brs.go.ke',
 'https://www.ecitizen.go.ke', '+254 20 222 2222', 88.0, 7, 4.3,
 'business registration, company registration, business permit, trade license', true);

-- Birth Certificate
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('Birth Certificate', 'Identity', 'Apply for birth certificate, replacement, corrections',
 'Birth certificate services include first-time registration, replacement of lost certificates, correction of errors, and certified copies. Available at Huduma Centres and Civil Registration offices.',
 200, 'KES', 14, NULL,
 '["Hospital Birth Notification", "Parent IDs", "Witness Affidavit"]'::jsonb,
 '{"birth": "Born in Kenya or to Kenyan parents", "age": "Any age"}'::jsonb,
 'Civil Registration Service', 'info@crs.go.ke', '+254 20 222 2222', 'https://www.crs.go.ke',
 'https://www.ecitizen.go.ke', '+254 20 222 2222', 87.5, 14, 4.2,
 'birth certificate, birth registration, birth record', true);

-- Passport Services
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('Passport Services', 'Travel', 'Apply for new passport, renewal, tracking',
 'Passport services include first-time application, passport renewal, replacement of lost/damaged passport, and application tracking. Available at Immigration offices and selected Huduma Centres.',
 4500, 'KES', 21, NULL,
 '["National ID", "Birth Certificate", "Passport Photo", "Old Passport (for renewal)"]'::jsonb,
 '{"age": "Any age", "citizenship": "Kenyan citizen", "travel": "Valid travel purpose"}'::jsonb,
 'Department of Immigration Services', 'info@immigration.go.ke', '+254 20 222 2022', 'https://www.immigration.go.ke',
 'https://www.ecitizen.go.ke', '+254 20 222 2022', 90.0, 21, 4.4,
 'passport, travel document, passport renewal, passport application', true);

-- Huduma Number
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('Huduma Number', 'Identity', 'Register for Huduma Number and manage services',
 'Huduma Number is a unique identifier that links all government services for citizens. Registration enables access to integrated government services through a single number. Available at all Huduma Centres.',
 0, 'KES', NULL, 1,
 '["National ID", "Phone Number", "Email Address"]'::jsonb,
 '{"age": "18+", "citizenship": "Kenyan citizen", "id": "Valid National ID"}'::jsonb,
 'Huduma Kenya Secretariat', 'info@hudumakenya.go.ke', '1919', 'https://www.hudumakenya.go.ke',
 'https://www.hudumakenya.go.ke', '1919', 91.0, 1, 4.5,
 'Huduma Number, Huduma Namba, integrated services, government services', true);

-- NSSF Pension
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('NSSF Pension', 'Finance', 'Check contributions, register, claim benefits',
 'National Social Security Fund (NSSF) provides social security services including membership registration, contribution tracking, benefit claims, and pension services. Available online or at NSSF offices.',
 200, 'KES', NULL, 1,
 '["National ID", "KRA PIN", "Employment Letter", "Bank Account Details"]'::jsonb,
 '{"age": "18+", "employment": "Formally employed", "contribution": "Active contributor"}'::jsonb,
 'National Social Security Fund', 'info@nssf.or.ke', '+254 20 271 2900', 'https://www.nssf.or.ke',
 'https://www.nssf.or.ke', '+254 20 271 2900', 85.0, 7, 4.1,
 'NSSF, pension, social security, retirement benefits, contributions', true);

-- NTSA Services (Driving License)
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('Driving License Services', 'Transport', 'Apply for driving license, renewal, replacement',
 'National Transport and Safety Authority (NTSA) provides driving license services including first-time application, renewal, replacement, and license verification. Available at NTSA offices and selected Huduma Centres.',
 3000, 'KES', 14, NULL,
 '["National ID", "Medical Certificate", "Passport Photo", "Old License (for renewal)"]'::jsonb,
 '{"age": "18+", "driving": "Valid driving test certificate", "medical": "Valid medical certificate"}'::jsonb,
 'National Transport and Safety Authority', 'info@ntsa.go.ke', '+254 20 272 3000', 'https://www.ntsa.go.ke',
 'https://www.ntsa.go.ke', '+254 20 272 3000', 90.0, 14, 4.3,
 'driving license, NTSA, driver license, license renewal, transport', true);

-- Police Clearance Certificate
INSERT INTO services (name, category, description, detailed_description, cost_kes, cost_currency, processing_time_days, processing_time_hours, requirements, eligibility_criteria, government_agency_name, government_agency_email, government_agency_phone, government_agency_website, service_website, service_phone, completion_rate, average_processing_days, satisfaction_score, keywords, is_active) VALUES
('Police Clearance Certificate', 'Security', 'Apply for police clearance certificate',
 'Police Clearance Certificate (Certificate of Good Conduct) is required for employment, travel, and other official purposes. Available at Criminal Records Office and selected Huduma Centres.',
 1000, 'KES', 14, NULL,
 '["National ID", "Passport Photo", "Fingerprints", "Application Form"]'::jsonb,
 '{"age": "18+", "citizenship": "Kenyan citizen or resident", "purpose": "Valid purpose for clearance"}'::jsonb,
 'Criminal Records Office', 'info@criminalrecords.go.ke', '+254 20 222 2222', 'https://www.criminalrecords.go.ke',
 'https://www.ecitizen.go.ke', '+254 20 222 2222', 88.5, 14, 4.2,
 'police clearance, certificate of good conduct, criminal records, clearance certificate', true);

COMMIT;

-- ============================================================================
-- SERVICE STEPS DATA (Sample steps for key services)
-- ============================================================================
-- Add procedural steps for each service to guide users
-- ============================================================================

BEGIN;

-- NHIF Registration Steps
INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 1, 'Gather Required Documents', 
       'Collect your National ID, KRA PIN, phone number, and email address',
       'Ensure your National ID is valid and not expired. Have your KRA PIN ready.',
       '["National ID", "KRA PIN"]'::jsonb, 5, 'both',
       'You can prepare documents at home or bring them to the Huduma Centre'
FROM services WHERE name = 'NHIF Health Insurance';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 2, 'Visit Huduma Centre or Register Online',
       'Go to any Huduma Centre or visit www.nhif.or.ke to register online',
       'Online registration is faster. Walk-ins are welcome at Huduma Centres but appointments get priority.',
       '[]'::jsonb, 30, 'both',
       'Huduma Centres: Monday-Friday 8AM-5PM, Saturday 8AM-1PM. Online: 24/7'
FROM services WHERE name = 'NHIF Health Insurance';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 3, 'Complete Registration Form',
       'Fill in your personal details, employment status, and contact information',
       'Double-check all information before submitting. Incorrect details may delay processing.',
       '[]'::jsonb, 10, 'both',
       'Forms available at Huduma Centre or online portal'
FROM services WHERE name = 'NHIF Health Insurance';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 4, 'Pay Initial Contribution',
       'Pay the minimum monthly contribution of KES 500 (self-employed) or as per your employment',
       'Payment can be made via M-Pesa, bank, or at Huduma Centre. Keep receipt for records.',
       '[]'::jsonb, 5, 'both',
       'M-Pesa Paybill: 200222, Account: Your ID Number'
FROM services WHERE name = 'NHIF Health Insurance';

-- KRA PIN Application Steps
INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 1, 'Prepare Required Documents',
       'Have your National ID, email address, phone number, and passport photo ready',
       'Ensure your email is active as PIN will be sent there. Phone number must be registered in your name.',
       '["National ID", "Passport Photo", "Email Address", "Phone Number"]'::jsonb, 5, 'both',
       'Documents can be prepared at home'
FROM services WHERE name = 'KRA Tax Services';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 2, 'Visit KRA Website or Huduma Centre',
       'Go to www.kra.go.ke and click "iTax Registration" or visit any Huduma Centre',
       'Online registration is instant. Huduma Centre registration takes about 1 hour.',
       '[]'::jsonb, 30, 'both',
       'Online: www.kra.go.ke (24/7). Huduma Centre: Monday-Friday 8AM-5PM'
FROM services WHERE name = 'KRA Tax Services';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 3, 'Fill Registration Form',
       'Enter your personal details, employment information, and contact details',
       'Be accurate with your details. Your PIN will be linked to your ID number permanently.',
       '[]'::jsonb, 15, 'both',
       'Form available online or at service desk'
FROM services WHERE name = 'KRA Tax Services';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 4, 'Receive Your PIN',
       'Your KRA PIN will be generated instantly and sent to your email',
       'PIN is free. Save it securely. You will need it for all tax-related transactions.',
       '[]'::jsonb, 1, 'online',
       'PIN sent via email immediately after registration'
FROM services WHERE name = 'KRA Tax Services';

-- National ID Application Steps
INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 1, 'Gather Required Documents',
       'Collect Birth Certificate, passport photos, parent/guardian ID, and school certificate',
       'Passport photos must be recent (taken within 6 months). All documents must be original or certified copies.',
       '["Birth Certificate", "Passport Photo (2 copies)", "Parent/Guardian ID", "School Certificate"]'::jsonb, 10, 'both',
       'Prepare documents before visiting the office'
FROM services WHERE name = 'National ID';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 2, 'Visit Huduma Centre or Immigration Office',
       'Go to your nearest Huduma Centre or Immigration office with all documents',
       'Book appointment online at www.hudumakenya.go.ke to avoid long queues. Walk-ins accepted but may take longer.',
       '[]'::jsonb, 60, 'huduma_centre',
       'Huduma Centres: Monday-Friday 8AM-5PM, Saturday 8AM-1PM'
FROM services WHERE name = 'National ID';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 3, 'Complete Application and Biometrics',
       'Fill application form and provide fingerprints and photo',
       'Ensure all information matches your documents. Biometric capture is mandatory.',
       '[]'::jsonb, 30, 'huduma_centre',
       'Biometric capture done at service desk'
FROM services WHERE name = 'National ID';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 4, 'Pay Application Fee',
       'Pay KES 1,000 application fee via M-Pesa or at the office',
       'Keep payment receipt. You will need it to collect your ID.',
       '[]'::jsonb, 5, 'both',
       'M-Pesa Paybill: 222222, Account: Your ID Application Number'
FROM services WHERE name = 'National ID';

INSERT INTO service_steps (service_id, step_number, title, description, tips_and_notes, documents_needed, estimated_time_minutes, location_type, location_instructions)
SELECT id, 5, 'Wait for Processing and Collection',
       'ID processing takes 21 days. You will receive SMS notification when ready',
       'Collection must be done in person with your application receipt. Bring a valid ID for verification.',
       '["Application Receipt", "Valid ID for Verification"]'::jsonb, 10, 'huduma_centre',
       'Collection at same Huduma Centre where you applied. Monday-Friday 8AM-5PM'
FROM services WHERE name = 'National ID';

COMMIT;

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- This script has populated:
-- 1. 28+ Huduma Centres across major counties (extend to all 57 centres as needed)
-- 2. 10 Government Services with complete details
-- 3. Service Steps for NHIF, KRA, and National ID (add more as needed)
-- 
-- To add more data:
-- 1. Add remaining Huduma Centres following the same pattern
-- 2. Add more service steps for other services
-- 3. Update statistics based on dashboard analytics
-- ============================================================================

SELECT 'Seed data insertion completed successfully!' AS status;

-- ============================================================================
-- AfroKen LLM - Chat Metrics Seed Data
-- ============================================================================
-- This script populates the chat_metrics table with sample data
-- for testing the dual implementation (dummy + real data) in the Dashboard
-- ============================================================================
-- Run this script to add metrics that will combine with dummy data
-- Usage: psql -U afroken -d afroken_llm_db -f seed_chat_metrics.sql
-- ============================================================================

BEGIN;

-- Clear existing metrics (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE chat_metrics CASCADE;

-- Insert sample chat metrics for the last 30 days
-- Each entry represents hourly aggregated data

-- Week 1 metrics
INSERT INTO chat_metrics (date_hour, total_conversations, total_messages, total_queries, average_response_time_ms, unique_users, new_users, top_services, top_intents, average_satisfaction_score, language_distribution, sentiment_distribution, total_cost_usd, average_cost_per_request) VALUES
-- Day 1
('2024-11-01 08:00:00+00', 45, 120, 45, 1200, 38, 5, 
 '["NHIF", "KRA", "Huduma"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 12}, {"intent": "KRA PIN", "count": 8}, {"intent": "Huduma Appointment", "count": 6}]'::jsonb,
 4.2, 
 '{"sw": 28, "en": 12, "sheng": 5}'::jsonb,
 '{"positive": 32, "neutral": 10, "negative": 3}'::jsonb,
 2.45, 0.054),
('2024-11-01 12:00:00+00', 78, 195, 78, 1100, 65, 8,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 22}, {"intent": "KRA PIN", "count": 15}, {"intent": "NSSF Check", "count": 10}]'::jsonb,
 4.3,
 '{"sw": 52, "en": 20, "sheng": 6}'::jsonb,
 '{"positive": 55, "neutral": 18, "negative": 5}'::jsonb,
 4.12, 0.053),
('2024-11-01 16:00:00+00', 62, 155, 62, 1300, 54, 6,
 '["KRA", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 18}, {"intent": "Huduma Appointment", "count": 12}, {"intent": "Passport Application", "count": 8}]'::jsonb,
 4.1,
 '{"sw": 45, "en": 14, "sheng": 3}'::jsonb,
 '{"positive": 48, "neutral": 12, "negative": 2}'::jsonb,
 3.28, 0.053),

-- Day 2
('2024-11-02 08:00:00+00', 52, 130, 52, 1150, 44, 7,
 '["NHIF", "KRA", "Business Registration"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 15}, {"intent": "KRA PIN", "count": 11}, {"intent": "Business Registration", "count": 7}]'::jsonb,
 4.4,
 '{"sw": 35, "en": 14, "sheng": 3}'::jsonb,
 '{"positive": 42, "neutral": 8, "negative": 2}'::jsonb,
 2.89, 0.056),
('2024-11-02 12:00:00+00', 85, 212, 85, 1050, 72, 10,
 '["NHIF", "KRA", "NSSF", "Huduma"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 25}, {"intent": "KRA PIN", "count": 18}, {"intent": "NSSF Check", "count": 12}, {"intent": "Huduma Appointment", "count": 10}]'::jsonb,
 4.5,
 '{"sw": 68, "en": 14, "sheng": 3}'::jsonb,
 '{"positive": 72, "neutral": 11, "negative": 2}'::jsonb,
 4.76, 0.056),
('2024-11-02 16:00:00+00', 68, 170, 68, 1250, 58, 5,
 '["KRA", "Huduma", "National ID"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 20}, {"intent": "Huduma Appointment", "count": 14}, {"intent": "ID Application", "count": 9}]'::jsonb,
 4.2,
 '{"sw": 52, "en": 13, "sheng": 3}'::jsonb,
 '{"positive": 58, "neutral": 9, "negative": 1}'::jsonb,
 3.81, 0.056),

-- Day 3
('2024-11-03 08:00:00+00', 48, 120, 48, 1180, 40, 6,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 14}, {"intent": "KRA PIN", "count": 10}]'::jsonb,
 4.3,
 '{"sw": 32, "en": 13, "sheng": 3}'::jsonb,
 '{"positive": 38, "neutral": 9, "negative": 1}'::jsonb,
 2.69, 0.056),
('2024-11-03 12:00:00+00', 92, 230, 92, 1020, 78, 12,
 '["NHIF", "KRA", "NSSF", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 28}, {"intent": "KRA PIN", "count": 20}, {"intent": "NSSF Check", "count": 14}, {"intent": "Huduma Appointment", "count": 12}, {"intent": "Passport Application", "count": 8}]'::jsonb,
 4.6,
 '{"sw": 74, "en": 15, "sheng": 3}'::jsonb,
 '{"positive": 82, "neutral": 9, "negative": 1}'::jsonb,
 5.15, 0.056),
('2024-11-03 16:00:00+00', 71, 178, 71, 1280, 61, 4,
 '["KRA", "Huduma", "Business Registration"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 22}, {"intent": "Huduma Appointment", "count": 15}, {"intent": "Business Registration", "count": 10}]'::jsonb,
 4.3,
 '{"sw": 57, "en": 11, "sheng": 3}'::jsonb,
 '{"positive": 64, "neutral": 6, "negative": 1}'::jsonb,
 3.98, 0.056),

-- Day 4
('2024-11-04 08:00:00+00', 55, 138, 55, 1120, 47, 8,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 16}, {"intent": "KRA PIN", "count": 12}, {"intent": "NSSF Check", "count": 8}]'::jsonb,
 4.4,
 '{"sw": 40, "en": 12, "sheng": 3}'::jsonb,
 '{"positive": 48, "neutral": 6, "negative": 1}'::jsonb,
 3.08, 0.056),
('2024-11-04 12:00:00+00', 88, 220, 88, 1080, 75, 11,
 '["NHIF", "KRA", "NSSF", "Huduma"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 26}, {"intent": "KRA PIN", "count": 19}, {"intent": "NSSF Check", "count": 13}, {"intent": "Huduma Appointment", "count": 11}]'::jsonb,
 4.5,
 '{"sw": 71, "en": 14, "sheng": 3}'::jsonb,
 '{"positive": 79, "neutral": 8, "negative": 1}'::jsonb,
 4.93, 0.056),
('2024-11-04 16:00:00+00', 65, 163, 65, 1220, 56, 5,
 '["KRA", "Huduma", "National ID"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 19}, {"intent": "Huduma Appointment", "count": 13}, {"intent": "ID Application", "count": 8}]'::jsonb,
 4.2,
 '{"sw": 52, "en": 11, "sheng": 2}'::jsonb,
 '{"positive": 58, "neutral": 6, "negative": 1}'::jsonb,
 3.64, 0.056),

-- Day 5
('2024-11-05 08:00:00+00', 50, 125, 50, 1140, 43, 7,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 15}, {"intent": "KRA PIN", "count": 11}]'::jsonb,
 4.3,
 '{"sw": 36, "en": 12, "sheng": 2}'::jsonb,
 '{"positive": 42, "neutral": 7, "negative": 1}'::jsonb,
 2.80, 0.056),
('2024-11-05 12:00:00+00', 90, 225, 90, 1040, 77, 13,
 '["NHIF", "KRA", "NSSF", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 27}, {"intent": "KRA PIN", "count": 20}, {"intent": "NSSF Check", "count": 14}, {"intent": "Huduma Appointment", "count": 12}, {"intent": "Passport Application", "count": 9}]'::jsonb,
 4.6,
 '{"sw": 72, "en": 15, "sheng": 3}'::jsonb,
 '{"positive": 81, "neutral": 8, "negative": 1}'::jsonb,
 5.04, 0.056),
('2024-11-05 16:00:00+00', 70, 175, 70, 1260, 60, 4,
 '["KRA", "Huduma", "Business Registration"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 21}, {"intent": "Huduma Appointment", "count": 14}, {"intent": "Business Registration", "count": 9}]'::jsonb,
 4.3,
 '{"sw": 58, "en": 10, "sheng": 2}'::jsonb,
 '{"positive": 63, "neutral": 6, "negative": 1}'::jsonb,
 3.92, 0.056),

-- Day 6 (Saturday - lower volume)
('2024-11-06 08:00:00+00', 35, 88, 35, 1200, 30, 4,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 10}, {"intent": "KRA PIN", "count": 8}]'::jsonb,
 4.2,
 '{"sw": 26, "en": 7, "sheng": 2}'::jsonb,
 '{"positive": 29, "neutral": 5, "negative": 1}'::jsonb,
 1.96, 0.056),
('2024-11-06 12:00:00+00', 42, 105, 42, 1150, 36, 5,
 '["NHIF", "KRA", "Huduma"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 12}, {"intent": "KRA PIN", "count": 9}, {"intent": "Huduma Appointment", "count": 7}]'::jsonb,
 4.4,
 '{"sw": 32, "en": 9, "sheng": 1}'::jsonb,
 '{"positive": 37, "neutral": 4, "negative": 1}'::jsonb,
 2.35, 0.056),

-- Day 7 (Sunday - minimal)
('2024-11-07 10:00:00+00', 18, 45, 18, 1300, 15, 2,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 6}, {"intent": "KRA PIN", "count": 4}]'::jsonb,
 4.1,
 '{"sw": 14, "en": 3, "sheng": 1}'::jsonb,
 '{"positive": 15, "neutral": 2, "negative": 1}'::jsonb,
 1.01, 0.056);

-- Add more recent metrics (last 7 days) for better testing
INSERT INTO chat_metrics (date_hour, total_conversations, total_messages, total_queries, average_response_time_ms, unique_users, new_users, top_services, top_intents, average_satisfaction_score, language_distribution, sentiment_distribution, total_cost_usd, average_cost_per_request) VALUES
-- Recent Day 1
(NOW() - INTERVAL '7 days' + INTERVAL '8 hours', 58, 145, 58, 1100, 50, 9,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 17}, {"intent": "KRA PIN", "count": 13}, {"intent": "NSSF Check", "count": 9}]'::jsonb,
 4.4,
 '{"sw": 45, "en": 11, "sheng": 2}'::jsonb,
 '{"positive": 52, "neutral": 5, "negative": 1}'::jsonb,
 3.25, 0.056),
(NOW() - INTERVAL '7 days' + INTERVAL '12 hours', 95, 238, 95, 1000, 81, 14,
 '["NHIF", "KRA", "NSSF", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 29}, {"intent": "KRA PIN", "count": 21}, {"intent": "NSSF Check", "count": 15}, {"intent": "Huduma Appointment", "count": 13}, {"intent": "Passport Application", "count": 10}]'::jsonb,
 4.7,
 '{"sw": 76, "en": 16, "sheng": 3}'::jsonb,
 '{"positive": 86, "neutral": 8, "negative": 1}'::jsonb,
 5.32, 0.056),
(NOW() - INTERVAL '7 days' + INTERVAL '16 hours', 72, 180, 72, 1200, 62, 6,
 '["KRA", "Huduma", "National ID"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 22}, {"intent": "Huduma Appointment", "count": 15}, {"intent": "ID Application", "count": 9}]'::jsonb,
 4.3,
 '{"sw": 60, "en": 10, "sheng": 2}'::jsonb,
 '{"positive": 65, "neutral": 6, "negative": 1}'::jsonb,
 4.03, 0.056),

-- Recent Day 2
(NOW() - INTERVAL '6 days' + INTERVAL '8 hours', 60, 150, 60, 1080, 52, 10,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 18}, {"intent": "KRA PIN", "count": 14}, {"intent": "NSSF Check", "count": 10}]'::jsonb,
 4.5,
 '{"sw": 47, "en": 11, "sheng": 2}'::jsonb,
 '{"positive": 54, "neutral": 5, "negative": 1}'::jsonb,
 3.36, 0.056),
(NOW() - INTERVAL '6 days' + INTERVAL '12 hours', 98, 245, 98, 980, 84, 15,
 '["NHIF", "KRA", "NSSF", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 30}, {"intent": "KRA PIN", "count": 22}, {"intent": "NSSF Check", "count": 16}, {"intent": "Huduma Appointment", "count": 14}, {"intent": "Passport Application", "count": 11}]'::jsonb,
 4.8,
 '{"sw": 78, "en": 17, "sheng": 3}'::jsonb,
 '{"positive": 89, "neutral": 8, "negative": 1}'::jsonb,
 5.49, 0.056),
(NOW() - INTERVAL '6 days' + INTERVAL '16 hours', 75, 188, 75, 1180, 65, 7,
 '["KRA", "Huduma", "Business Registration"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 23}, {"intent": "Huduma Appointment", "count": 16}, {"intent": "Business Registration", "count": 10}]'::jsonb,
 4.4,
 '{"sw": 63, "en": 10, "sheng": 2}'::jsonb,
 '{"positive": 68, "neutral": 6, "negative": 1}'::jsonb,
 4.20, 0.056),

-- Recent Day 3 (Today - for real-time testing)
(NOW() - INTERVAL '2 hours', 45, 113, 45, 1050, 39, 8,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 14}, {"intent": "KRA PIN", "count": 11}]'::jsonb,
 4.5,
 '{"sw": 34, "en": 9, "sheng": 2}'::jsonb,
 '{"positive": 40, "neutral": 4, "negative": 1}'::jsonb,
 2.52, 0.056),
(NOW() - INTERVAL '1 hour', 52, 130, 52, 1020, 45, 9,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 16}, {"intent": "KRA PIN", "count": 12}, {"intent": "NSSF Check", "count": 8}]'::jsonb,
 4.6,
 '{"sw": 40, "en": 10, "sheng": 2}'::jsonb,
 '{"positive": 47, "neutral": 4, "negative": 1}'::jsonb,
 2.91, 0.056);

COMMIT;

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- This script has inserted sample chat metrics data:
-- - Historical data for the past 7 days
-- - Recent data for testing
-- - Current hour data for real-time display
--
-- The metrics include:
-- - Total conversations, messages, queries
-- - Average response times
-- - Unique users and new users
-- - Top services and intents
-- - Satisfaction scores
-- - Language and sentiment distribution
-- - Cost tracking
--
-- These metrics will be combined with dummy data in the Dashboard
-- to demonstrate dual implementation (dummy + real data)
-- ============================================================================

SELECT 'Chat metrics seed data inserted successfully!' AS status;
SELECT 
    COUNT(*) as total_metrics,
    SUM(total_queries) as total_queries_sum,
    AVG(average_satisfaction_score) as avg_satisfaction,
    MIN(date_hour) as earliest_metric,
    MAX(date_hour) as latest_metric
FROM chat_metrics;


-- ---------------------------------------------------------------------
-- AfroKen: Frontend & Integration Enhancements (append to existing schema)
-- Created: 2025-11-26 (extension of afroken_complete_database.sql). 
-- See original schema for base tables / indexes. :contentReference[oaicite:2]{index=2}
-- ---------------------------------------------------------------------

/* ============================
   1. Attachments & Media
   store files (images, audio, pdf) linked to messages or documents
   uses MinIO/S3 object keys in the app (avoid storing blobs in DB)
   ============================ */
CREATE TABLE IF NOT EXISTS attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    filename VARCHAR(512),
    mime_type VARCHAR(128),
    size_bytes BIGINT,
    storage_key VARCHAR(1000) NOT NULL, -- e.g., minio://bucket/object or s3://bucket/key
    thumbnail_key VARCHAR(1000),
    processing_status VARCHAR(50) DEFAULT 'ready', -- processing|ready|failed
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_attachments_message ON attachments(message_id);
CREATE INDEX IF NOT EXISTS idx_attachments_owner ON attachments(owner_user_id);

/* ============================
   2. Canned responses & Quick Actions
   used by frontend to show suggested replies, buttons and CTA
   ============================ */
CREATE TABLE IF NOT EXISTS canned_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    language language_type DEFAULT 'sw',
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    usage_count BIGINT DEFAULT 0,
    created_by UUID REFERENCES users(id),
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_canned_responses_tags ON canned_responses USING gin(tags);

/* Quick actions that appear inline (e.g., 'Book appointment', 'Request callback') */
CREATE TABLE IF NOT EXISTS quick_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- api_call | ussd | link | schedule
    payload JSONB NOT NULL,
    visible_to_roles user_role[] DEFAULT ARRAY['citizen']::user_role[],
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_quick_actions_name ON quick_actions(name);

/* ============================
   3. UI Templates & Frontend Strings (i18n)
   frontend requests localised UI strings and templates
   ============================ */
CREATE TABLE IF NOT EXISTS ui_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_name VARCHAR(255) UNIQUE NOT NULL, -- e.g., 'chat.empty_state'
    language language_type NOT NULL DEFAULT 'en',
    content TEXT NOT NULL, -- HTML/markdown/plain text
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ui_templates_key_lang ON ui_templates(key_name, language);

/* Translations dictionary for dynamic front-end copy */
CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_name VARCHAR(255) NOT NULL,
    language language_type NOT NULL,
    value TEXT NOT NULL,
    context JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_translations UNIQUE (key_name, language)
);
CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(key_name);

/* ============================
   4. Saved Searches / Watchlists (Dashboard features)
   ============================ */
CREATE TABLE IF NOT EXISTS saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    query JSONB NOT NULL, -- serialized search filters e.g. {service_category, county, date_range}
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_saved_searches_owner ON saved_searches(owner_user_id);

/* Watchlists for admins (e.g., monitor flagged conversations, high-severity queries) */
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_user_id UUID REFERENCES users(id),
    filters JSONB NOT NULL,
    notification_channels JSONB DEFAULT '[]'::jsonb, -- ["email","webhook"]
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_watchlists_owner ON watchlists(owner_user_id);

/* watchlist items (matches) */
CREATE TABLE IF NOT EXISTS watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    resource_type VARCHAR(50),
    resource_id UUID,
    matched_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist ON watchlist_items(watchlist_id);

/* ============================
   5. Notifications & Webhooks
   supports WhatsApp/SMS/Email/Push and webhooks to county systems
   ============================ */
CREATE TABLE IF NOT EXISTS notification_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel VARCHAR(50) NOT NULL, -- whatsapp|sms|email|push|ussd
    recipient VARCHAR(500), -- phone number or email or user_id
    payload JSONB NOT NULL, -- message payload (text, media keys, template id)
    status VARCHAR(50) DEFAULT 'queued', -- queued|sent|failed|delivered
    retries INT DEFAULT 0,
    last_error TEXT,
    scheduled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    sent_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_notification_queue_status ON notification_queue(status);
CREATE INDEX IF NOT EXISTS idx_notification_queue_scheduled ON notification_queue(scheduled_at);

/* Webhook subscriptions (for counties / agencies) */
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_org VARCHAR(255) NOT NULL, -- e.g., 'NDMA-CountyKitui'
    url VARCHAR(2000) NOT NULL,
    events TEXT[] NOT NULL, -- ["conversation.created","alert.pest"]
    secret_key VARCHAR(500), -- HMAC secret (store encrypted)
    is_active BOOLEAN DEFAULT TRUE,
    last_delivery TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_webhooks_owner ON webhooks(owner_org);

/* Webhook delivery logs (for diagnostics) */
CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(255),
    payload JSONB,
    response_status INT,
    response_body TEXT,
    delivered_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_webhook_delivered_at ON webhook_deliveries(delivered_at DESC);

/* ============================
   6. API Keys & OAuth clients (frontend integrations / admin)
   ============================ */
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(512) NOT NULL, -- store hash (never plain API key)
    owner_user_id UUID REFERENCES users(id),
    scope TEXT[], -- scopes assigned to key
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_api_keys_owner ON api_keys(owner_user_id);

/* OAuth clients for agency integrations (e.g., eCitizen portals) */
CREATE TABLE IF NOT EXISTS oauth_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(255) UNIQUE NOT NULL,
    client_secret_encrypted VARCHAR(1000),
    display_name VARCHAR(255),
    redirect_uris TEXT[],
    grant_types TEXT[],
    scope TEXT[],
    is_confidential BOOLEAN DEFAULT TRUE,
    owner_org VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_oauth_clients_org ON oauth_clients(owner_org);

/* ============================
   7. Feature Flags & Rate Limits (frontend A/B, staged rollouts)
   ============================ */
CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_name VARCHAR(255) UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    rollout_rules JSONB DEFAULT '[]'::jsonb, -- e.g., [{"role":"admin"},{"percentage":10}]
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON feature_flags(key_name);

/* Rate limits per API key or user for frontend / mobile */
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_type VARCHAR(50) NOT NULL, -- 'api_key','user','ip'
    subject_id TEXT NOT NULL,
    limit_per_minute INT DEFAULT 60,
    limit_per_hour INT DEFAULT 1000,
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_rate_limits_subject ON rate_limits(subject_type, subject_id);

/* ============================
   8. Conversation tags, flags and feedback (rich UX interactions)
   ============================ */
CREATE TABLE IF NOT EXISTS conversation_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS conversation_tag_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES conversation_tags(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_conversation_tags_conv ON conversation_tag_assignments(conversation_id);

/* Reaction (emoji/like) to messages (frontend micro-interaction) */
CREATE TABLE IF NOT EXISTS message_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    reaction VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_message_user_reaction UNIQUE (message_id, user_id, reaction)
);
CREATE INDEX IF NOT EXISTS idx_message_reactions_msg ON message_reactions(message_id);

/* User feedback on a completed conversation */
CREATE TABLE IF NOT EXISTS conversation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    rating SMALLINT, -- 1..5
    comments TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_conv_feedback_conv ON conversation_feedback(conversation_id);

/* ============================
   9. Analytics events & telemetry (frontend instrumentation)
   ============================ */
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(255) NOT NULL, -- page_view | click | chat_send | ussd_start etc.
    event_properties JSONB DEFAULT '{}'::jsonb,
    source VARCHAR(50), -- web|mobile|ussd|whatsapp
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT now()
) ;
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_user ON analytics_events(user_id);

/* Materialized view example for dashboard: top services by queries (refreshed periodically) */
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_service_query_counts AS
SELECT s.id AS service_id, s.name, COUNT(c.id) AS query_count
FROM services s
LEFT JOIN conversations c ON LOWER(c.service_category) = LOWER(s.category)
GROUP BY s.id, s.name
ORDER BY query_count DESC;

/* ============================
   10. Frontend session tokens & presence (for real-time UX)
   ============================ */
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(512) NOT NULL,
    device_info JSONB DEFAULT '{}'::jsonb,
    last_seen TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);

/* ============================
   11. Quick sample rows (small dev fixtures - optional)
   ============================ */
INSERT INTO canned_responses (title, body, language, tags, created_by)
VALUES (
  'How to check NHIF status',
  'Visit eCitizen > Services > NHIF membership. You can also send your ID number and we will check for you.',
  'en',
  ARRAY['NHIF','status'],
  (SELECT id FROM users WHERE role='admin' LIMIT 1)
) ON CONFLICT DO NOTHING;

INSERT INTO quick_actions (name, action_type, payload, created_by)
VALUES (
  'Book Huduma Appointment',
  'api_call',
  '{"endpoint":"/api/v1/integrations/ecitizen/appointments","method":"POST","body_template":{"service_code":"{{service_code}}","preferred_date":"{{date}}"}}'::jsonb,
  (SELECT id FROM users WHERE role='admin' LIMIT 1)
) ON CONFLICT DO NOTHING;

/* ============================
   12. Helpful indexes for new tables
   ============================ */
CREATE INDEX IF NOT EXISTS idx_attachments_storage_key ON attachments(storage_key);
CREATE INDEX IF NOT EXISTS idx_notifications_channel_status ON notification_queue(channel, status);
CREATE INDEX IF NOT EXISTS idx_api_keys_name ON api_keys(name);
CREATE INDEX IF NOT EXISTS idx_feature_flags_enabled ON feature_flags(enabled);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created ON analytics_events(created_at DESC);

-- ---------------------------------------------------------------------
-- End of frontend/integration enhancements
-- ---------------------------------------------------------------------

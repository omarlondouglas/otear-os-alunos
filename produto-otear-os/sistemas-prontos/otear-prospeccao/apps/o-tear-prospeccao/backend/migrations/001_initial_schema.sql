-- ============================================================
-- O Tear Prospecção — Schema Inicial
-- Executar no Supabase SQL Editor
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- LEADS (importados do ProspectPro)
-- ============================================================
CREATE TABLE leads (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prospect_pro_id     VARCHAR(16),

    -- Google Maps
    name                VARCHAR(500) NOT NULL,
    category            VARCHAR(255),
    phone               VARCHAR(50),
    website             VARCHAR(500),
    address             TEXT,
    rating              DECIMAL(2,1),
    reviews_count       INTEGER,
    maps_url            TEXT,
    latitude            DECIMAL(10,7),
    longitude           DECIMAL(10,7),

    -- Instagram
    instagram_handle        VARCHAR(255),
    instagram_url           VARCHAR(500),
    instagram_bio           TEXT,
    instagram_bio_link      VARCHAR(500),
    instagram_followers     INTEGER,
    instagram_following     INTEGER,
    instagram_posts         INTEGER,
    instagram_is_business   BOOLEAN DEFAULT false,
    instagram_is_verified   BOOLEAN DEFAULT false,
    engagement_rate         DECIMAL(5,2),
    avg_likes               DECIMAL(10,1),
    avg_comments            DECIMAL(10,1),
    posting_frequency_days  DECIMAL(5,1),
    last_post_date          TIMESTAMPTZ,

    -- Scoring
    score_total             INTEGER DEFAULT 0,
    score_classification    VARCHAR(10) CHECK (score_classification IN ('hot', 'warm', 'cold')),
    score_no_website        INTEGER DEFAULT 0,
    score_no_instagram      INTEGER DEFAULT 0,
    score_low_engagement    INTEGER DEFAULT 0,
    score_irregular_posting INTEGER DEFAULT 0,
    score_few_reviews       INTEGER DEFAULT 0,
    score_low_rating        INTEGER DEFAULT 0,
    score_no_professional_bio INTEGER DEFAULT 0,
    score_no_bio_link       INTEGER DEFAULT 0,

    -- Outreach
    approach_script     TEXT,
    outreach_status     VARCHAR(20) DEFAULT 'imported'
                        CHECK (outreach_status IN (
                            'imported', 'queued', 'contacted',
                            'replied', 'converted', 'opted_out', 'archived'
                        )),
    tags                TEXT[] DEFAULT '{}',
    notes               TEXT,

    -- WhatsApp
    whatsapp_number     VARCHAR(20),
    whatsapp_valid      BOOLEAN,

    -- Metadata
    import_batch_id     UUID,
    imported_at         TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_leads_classification ON leads(score_classification);
CREATE INDEX idx_leads_outreach_status ON leads(outreach_status);
CREATE INDEX idx_leads_tags ON leads USING GIN(tags);
CREATE INDEX idx_leads_name_trgm ON leads USING GIN(name gin_trgm_ops);
CREATE INDEX idx_leads_import_batch ON leads(import_batch_id);

-- ============================================================
-- CAMPAIGNS
-- ============================================================
CREATE TABLE campaigns (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    status              VARCHAR(20) DEFAULT 'draft'
                        CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')),

    -- Targeting
    target_filters      JSONB DEFAULT '{}',

    -- Schedule
    start_date          DATE,
    end_date            DATE,
    time_window_start   TIME DEFAULT '09:00',
    time_window_end     TIME DEFAULT '18:00',
    daily_limit         INTEGER DEFAULT 50,

    -- Anti-ban
    min_delay_seconds   INTEGER DEFAULT 45,
    max_delay_seconds   INTEGER DEFAULT 120,

    -- Stats (denormalized)
    total_leads         INTEGER DEFAULT 0,
    total_sent          INTEGER DEFAULT 0,
    total_delivered     INTEGER DEFAULT 0,
    total_read          INTEGER DEFAULT 0,
    total_replied       INTEGER DEFAULT 0,
    total_failed        INTEGER DEFAULT 0,

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CAMPAIGN MESSAGES (templates A/B)
-- ============================================================
CREATE TABLE campaign_messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id     UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

    variant_name    VARCHAR(50) DEFAULT 'A',
    template_body   TEXT NOT NULL,
    weight          INTEGER DEFAULT 100,

    times_sent      INTEGER DEFAULT 0,
    times_delivered INTEGER DEFAULT 0,
    times_read      INTEGER DEFAULT 0,
    times_replied   INTEGER DEFAULT 0,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_campaign_messages_campaign ON campaign_messages(campaign_id);

-- ============================================================
-- CAMPAIGN LEADS (M:N)
-- ============================================================
CREATE TABLE campaign_leads (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id     UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    lead_id         UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    status          VARCHAR(20) DEFAULT 'pending'
                    CHECK (status IN ('pending', 'queued', 'sent', 'delivered',
                                      'read', 'replied', 'failed', 'skipped')),
    variant_id      UUID REFERENCES campaign_messages(id),
    queued_at       TIMESTAMPTZ,
    sent_at         TIMESTAMPTZ,

    UNIQUE(campaign_id, lead_id)
);

CREATE INDEX idx_campaign_leads_campaign ON campaign_leads(campaign_id);
CREATE INDEX idx_campaign_leads_lead ON campaign_leads(lead_id);
CREATE INDEX idx_campaign_leads_status ON campaign_leads(status);

-- ============================================================
-- MESSAGE QUEUE
-- ============================================================
CREATE TABLE message_queue (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id         UUID REFERENCES campaigns(id),
    campaign_lead_id    UUID REFERENCES campaign_leads(id),
    lead_id             UUID NOT NULL REFERENCES leads(id),

    whatsapp_to         VARCHAR(20) NOT NULL,
    message_body        TEXT NOT NULL,

    status              VARCHAR(20) DEFAULT 'pending'
                        CHECK (status IN ('pending', 'processing', 'sent', 'failed', 'cancelled')),
    priority            INTEGER DEFAULT 0,

    scheduled_for       TIMESTAMPTZ,
    assigned_number_id  UUID,

    attempts            INTEGER DEFAULT 0,
    max_attempts        INTEGER DEFAULT 3,
    last_error          TEXT,

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    processed_at        TIMESTAMPTZ
);

CREATE INDEX idx_message_queue_status ON message_queue(status, scheduled_for);
CREATE INDEX idx_message_queue_number ON message_queue(assigned_number_id);

-- ============================================================
-- MESSAGE LOG
-- ============================================================
CREATE TABLE message_log (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    queue_id                UUID REFERENCES message_queue(id),
    campaign_id             UUID REFERENCES campaigns(id),
    lead_id                 UUID NOT NULL REFERENCES leads(id),

    whatsapp_from           VARCHAR(20) NOT NULL,
    whatsapp_to             VARCHAR(20) NOT NULL,
    message_body            TEXT NOT NULL,

    external_message_id     VARCHAR(255),

    status                  VARCHAR(20) DEFAULT 'sent'
                            CHECK (status IN ('sent', 'delivered', 'read', 'failed')),

    sent_at                 TIMESTAMPTZ DEFAULT NOW(),
    delivered_at            TIMESTAMPTZ,
    read_at                 TIMESTAMPTZ,
    failed_at               TIMESTAMPTZ,
    error_message           TEXT
);

CREATE INDEX idx_message_log_lead ON message_log(lead_id);
CREATE INDEX idx_message_log_campaign ON message_log(campaign_id);
CREATE INDEX idx_message_log_status ON message_log(status);
CREATE INDEX idx_message_log_sent_at ON message_log(sent_at);

-- ============================================================
-- WHATSAPP NUMBERS (remetentes)
-- ============================================================
CREATE TABLE whatsapp_numbers (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    label               VARCHAR(100) NOT NULL,
    phone_number        VARCHAR(20) NOT NULL UNIQUE,

    status              VARCHAR(20) DEFAULT 'warming_up'
                        CHECK (status IN ('warming_up', 'active', 'resting', 'banned', 'disabled')),

    -- Warm-up tracking
    warmup_started_at   TIMESTAMPTZ DEFAULT NOW(),
    warmup_day          INTEGER DEFAULT 0,
    daily_limit         INTEGER DEFAULT 20,
    current_daily_sent  INTEGER DEFAULT 0,

    -- Health
    ban_risk_score      INTEGER DEFAULT 0,
    total_sent_today    INTEGER DEFAULT 0,
    total_sent_week     INTEGER DEFAULT 0,
    total_sent_month    INTEGER DEFAULT 0,
    last_sent_at        TIMESTAMPTZ,
    last_error          TEXT,
    consecutive_errors  INTEGER DEFAULT 0,

    -- Rotation
    is_available        BOOLEAN DEFAULT true,
    rest_until          TIMESTAMPTZ,

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CONVERSATIONS
-- ============================================================
CREATE TABLE conversations (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id             UUID NOT NULL REFERENCES leads(id),
    whatsapp_number     VARCHAR(20) NOT NULL,

    last_message_at     TIMESTAMPTZ,
    last_message_preview TEXT,
    unread_count        INTEGER DEFAULT 0,
    is_archived         BOOLEAN DEFAULT false,
    sentiment           VARCHAR(20),
    auto_tags           TEXT[] DEFAULT '{}',

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_lead ON conversations(lead_id);
CREATE INDEX idx_conversations_unread ON conversations(unread_count) WHERE unread_count > 0;

-- ============================================================
-- CONVERSATION MESSAGES
-- ============================================================
CREATE TABLE conversation_messages (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    direction           VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    message_body        TEXT NOT NULL,
    message_type        VARCHAR(20) DEFAULT 'text',
    media_url           TEXT,

    external_message_id VARCHAR(255),
    status              VARCHAR(20) DEFAULT 'sent',

    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conv_messages_conversation ON conversation_messages(conversation_id, created_at);

-- ============================================================
-- OPT-OUTS
-- ============================================================
CREATE TABLE opt_outs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number    VARCHAR(20) NOT NULL UNIQUE,
    lead_id         UUID REFERENCES leads(id),
    reason          TEXT,
    opted_out_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_opt_outs_phone ON opt_outs(phone_number);

-- ============================================================
-- APP SETTINGS
-- ============================================================
CREATE TABLE app_settings (
    key         VARCHAR(100) PRIMARY KEY,
    value       JSONB NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO app_settings (key, value) VALUES
    ('business_hours', '{"start": "09:00", "end": "18:00", "timezone": "America/Sao_Paulo"}'),
    ('warmup_schedule', '{"day1_limit": 20, "day7_limit": 40, "day14_limit": 60, "day30_limit": 80}'),
    ('anti_ban', '{"min_delay_sec": 45, "max_delay_sec": 120, "max_daily_per_number": 80, "rest_hours_after_limit": 4}'),
    ('opt_out_keywords', '["parar", "sair", "cancelar", "stop", "remover", "nao quero", "nao desejo"]');

-- ============================================================
-- TRIGGERS: updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_leads_updated BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_campaigns_updated BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_whatsapp_numbers_updated BEFORE UPDATE ON whatsapp_numbers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_conversations_updated BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- FUNCTION: Reset daily counters (pg_cron à meia-noite)
-- ============================================================
CREATE OR REPLACE FUNCTION reset_daily_counters()
RETURNS void AS $$
BEGIN
    UPDATE whatsapp_numbers SET
        current_daily_sent = 0,
        total_sent_today = 0,
        is_available = true,
        rest_until = NULL
    WHERE status IN ('active', 'resting');
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- RLS (single-tenant: authenticated = full access)
-- ============================================================
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_numbers ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE opt_outs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "auth_full_access" ON leads FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON campaigns FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON campaign_messages FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON campaign_leads FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON message_queue FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON message_log FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON whatsapp_numbers FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON conversations FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON conversation_messages FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "auth_full_access" ON opt_outs FOR ALL USING (auth.role() = 'authenticated');

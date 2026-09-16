-- ============================================================
-- O Tear Prospeccao - Diagnostico de site dos leads
-- ============================================================

ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS site_status VARCHAR(20),
    ADD COLUMN IF NOT EXISTS site_score INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS site_final_url TEXT,
    ADD COLUMN IF NOT EXISTS site_problems TEXT[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS site_missing_items TEXT[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS site_present_items TEXT[] DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS site_response_time_seconds DECIMAL(6,2),
    ADD COLUMN IF NOT EXISTS site_http_status INTEGER,
    ADD COLUMN IF NOT EXISTS site_audit JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS score_bad_website INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_leads_site_status ON leads(site_status);
CREATE INDEX IF NOT EXISTS idx_leads_site_score ON leads(site_score);

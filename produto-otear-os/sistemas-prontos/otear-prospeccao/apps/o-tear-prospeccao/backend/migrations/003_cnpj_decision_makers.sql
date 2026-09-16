-- ============================================================
-- O Tear Prospeccao - CNPJ e decisores dos leads
-- ============================================================

ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS cnpj VARCHAR(14),
    ADD COLUMN IF NOT EXISTS razao_social TEXT,
    ADD COLUMN IF NOT EXISTS nome_fantasia TEXT,
    ADD COLUMN IF NOT EXISTS decision_maker_name TEXT,
    ADD COLUMN IF NOT EXISTS decision_maker_role TEXT,
    ADD COLUMN IF NOT EXISTS cnpj_owners JSONB DEFAULT '[]'::jsonb;

CREATE INDEX IF NOT EXISTS idx_leads_cnpj ON leads(cnpj);
CREATE INDEX IF NOT EXISTS idx_leads_decision_maker_name_trgm ON leads USING GIN(decision_maker_name gin_trgm_ops);

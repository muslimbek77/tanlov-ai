-- PostgreSQL uchun PGVector kengaytmasi
CREATE EXTENSION IF NOT EXISTS vector;

-- Tanlov AI ma'lumotlar bazasi uchun initial skript

-- Foydalanuvchi yaratish (agar kerak bo'lsa)
-- CREATE USER tanlov_ai WITH PASSWORD 'password';
-- GRANT ALL PRIVILEGES ON DATABASE tanlov_ai TO tanlov_ai;

-- Indekslar yaratish
-- Tenderlar uchun indekslar
CREATE INDEX IF NOT EXISTS idx_tenders_status ON tenders_tender(status);
CREATE INDEX IF NOT EXISTS idx_tenders_start_date ON tenders_tender(start_date);
CREATE INDEX IF NOT EXISTS idx_tenders_end_date ON tenders_tender(end_date);
CREATE INDEX IF NOT EXISTS idx_tenders_created_at ON tenders_tender(created_at);

-- Ishtirokchilar uchun indekslar
CREATE INDEX IF NOT EXISTS idx_participants_company_name ON participants_participant(company_name);
CREATE INDEX IF NOT EXISTS idx_participants_tax_id ON participants_participant(tax_identification_number);
CREATE INDEX IF NOT EXISTS idx_participants_status ON participants_participant(status);

-- Tender ishtirokchilari uchun indekslar
CREATE INDEX IF NOT EXISTS idx_tender_participants_tender ON participants_tenderparticipant(tender_id);
CREATE INDEX IF NOT EXISTS idx_tender_participants_participant ON participants_tenderparticipant(participant_id);
CREATE INDEX IF NOT EXISTS idx_tender_participants_status ON participants_tenderparticipant(status);
CREATE INDEX IF NOT EXISTS idx_tender_participants_registration_date ON participants_tenderparticipant(registration_date);

-- Baholashlar uchun indekslar
CREATE INDEX IF NOT EXISTS idx_evaluations_tender ON evaluations_evaluation(tender_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_status ON evaluations_evaluation(status);
CREATE INDEX IF NOT EXISTS idx_evaluations_created_at ON evaluations_evaluation(created_at);

-- Participant scores uchun indekslar
CREATE INDEX IF NOT EXISTS idx_participant_scores_evaluation ON evaluations_participantscore(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_participant_scores_participant ON evaluations_participantscore(tender_participant_id);
CREATE INDEX IF NOT EXISTS idx_participant_scores_total_score ON evaluations_participantscore(total_score DESC);

-- Korrupsiya aniqlash uchun indekslar
CREATE INDEX IF NOT EXISTS idx_fraud_detections_tender ON anti_fraud_frauddetection(tender_id);
CREATE INDEX IF NOT EXISTS idx_fraud_detections_severity ON anti_fraud_frauddetection(severity);
CREATE INDEX IF NOT EXISTS idx_fraud_detections_created_at ON anti_fraud_frauddetection(created_at);

-- Compliance tekshiruvlari uchun indekslar
CREATE INDEX IF NOT EXISTS idx_compliance_checks_tender ON compliance_compliancecheck(tender_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_participant ON compliance_compliancecheck(tender_participant_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_status ON compliance_compliancecheck(status);

-- Vektorli indekslar (PGVector)
CREATE INDEX IF NOT EXISTS idx_tender_requirements_vector ON tenders_tenderrequirement USING ivfflat (requirement_vector vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_tender_vector ON tenders_tender USING ivfflat (requirements_vector vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_participant_proposal_vector ON participants_tenderparticipant USING ivfflat (proposal_vector vector_cosine_ops);

-- Full text search indekslari
CREATE INDEX IF NOT EXISTS idx_tender_title_search ON tenders_tender USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_tender_description_search ON tenders_tender USING gin(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_participant_company_search ON participants_participant USING gin(to_tsvector('english', company_name));

-- Trigerlar (agar kerak bo'lsa)
-- Tender statusini avtomatik yangilash
CREATE OR REPLACE FUNCTION update_tender_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Tender muddati tugagan bo'lsa, statusni yangilash
    IF NEW.end_date < CURRENT_TIMESTAMP AND NEW.status = 'active' THEN
        NEW.status := 'completed';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tender_status
    BEFORE UPDATE ON tenders_tender
    FOR EACH ROW
    EXECUTE FUNCTION update_tender_status();

-- Log jadvali (audit uchun)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    user_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

-- Statistik view lar
CREATE OR REPLACE VIEW tender_statistics AS
SELECT 
    COUNT(*) as total_tenders,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_tenders,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tenders,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_tenders,
    AVG(estimated_budget) as avg_budget,
    SUM(estimated_budget) as total_budget
FROM tenders_tender;

CREATE OR REPLACE VIEW participant_statistics AS
SELECT 
    COUNT(*) as total_participants,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_participants,
    COUNT(CASE WHEN status = 'blacklisted' THEN 1 END) as blacklisted_participants,
    AVG(trust_score) as avg_trust_score
FROM participants_participant;

-- Performance monitoring uchun funksiyalar
CREATE OR REPLACE FUNCTION get_slow_queries()
RETURNS TABLE(query_text TEXT, calls INTEGER, total_time DOUBLE PRECISION, mean_time DOUBLE PRECISION) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        query,
        calls,
        total_time,
        mean_time
    FROM pg_stat_statements
    WHERE mean_time > 1000 -- 1 sekunddan ko'proq
    ORDER BY mean_time DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- Ma'lumotlarni tozalash uchun funksiyalar
CREATE OR REPLACE FUNCTION cleanup_old_data(days_old INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Eski loglarni tozalash
    DELETE FROM core_celery_taskresult 
    WHERE date_created < CURRENT_TIMESTAMP - INTERVAL '1 day';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Eski audit loglarni tozalash
    DELETE FROM audit_log 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '%s days' % days_old;
    
    GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON DATABASE tanlov_ai IS 'Tanlov AI - Avtomatlashtirilgan Multi-Agent tender tizimi';

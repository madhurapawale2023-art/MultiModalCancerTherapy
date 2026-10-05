-- ============================================================
-- MultiModalCancerTherapy
-- Clinical + Ultrasound Database Schema
-- PostgreSQL
-- ============================================================

CREATE SCHEMA IF NOT EXISTS multimodal;

-- ============================================================
-- 1. Roles
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. Users
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE,
    password_hash TEXT NOT NULL,

    role_id INTEGER
        REFERENCES multimodal.roles(id)
        ON DELETE SET NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. Patients
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.patients (
    id BIGSERIAL PRIMARY KEY,

    patient_code VARCHAR(50) NOT NULL UNIQUE,

    full_name VARCHAR(150) NOT NULL,

    age INTEGER,

    sex VARCHAR(10),

    phone VARCHAR(30),

    email VARCHAR(150),

    address TEXT,

    status VARCHAR(50)
        NOT NULL DEFAULT 'registered',

    created_by INTEGER
        REFERENCES multimodal.users(id)
        ON DELETE SET NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. Clinical Records
-- Based on thyroidDF.csv / Clinical Notebook
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.clinical_records (
    id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES multimodal.patients(id)
        ON DELETE CASCADE,

    -- Source dataset identifier
    source_patient_id BIGINT,

    age INTEGER,

    sex VARCHAR(10),

    -- --------------------------------------------------------
    -- Clinical binary features
    -- --------------------------------------------------------

    on_thyroxine BOOLEAN,

    query_on_thyroxine BOOLEAN,

    on_antithyroid_meds BOOLEAN,

    sick BOOLEAN,

    pregnant BOOLEAN,

    thyroid_surgery BOOLEAN,

    i131_treatment BOOLEAN,

    query_hypothyroid BOOLEAN,

    query_hyperthyroid BOOLEAN,

    lithium BOOLEAN,

    goitre BOOLEAN,

    tumor BOOLEAN,

    hypopituitary BOOLEAN,

    psych BOOLEAN,

    -- --------------------------------------------------------
    -- Measurement indicators
    -- --------------------------------------------------------

    tsh_measured BOOLEAN,

    t3_measured BOOLEAN,

    tt4_measured BOOLEAN,

    t4u_measured BOOLEAN,

    fti_measured BOOLEAN,

    tbg_measured BOOLEAN,

    -- --------------------------------------------------------
    -- Laboratory values
    -- --------------------------------------------------------

    tsh NUMERIC,

    t3 NUMERIC,

    tt4 NUMERIC,

    t4u NUMERIC,

    fti NUMERIC,

    tbg NUMERIC,

    -- --------------------------------------------------------
    -- Other clinical information
    -- --------------------------------------------------------

    referral_source VARCHAR(50),

    -- Original dataset target / diagnosis code
    target_code VARCHAR(20),

    clinical_notes TEXT,

    entered_by INTEGER
        REFERENCES multimodal.users(id)
        ON DELETE SET NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. Ultrasound Cases
-- Based on Ultrasound XML data
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.ultrasound_cases (
    id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT
        REFERENCES multimodal.patients(id)
        ON DELETE SET NULL,

    -- Dataset XML case number
    case_number INTEGER NOT NULL UNIQUE,

    age INTEGER,

    sex VARCHAR(10),

    -- --------------------------------------------------------
    -- Ultrasound XML clinical descriptors
    -- --------------------------------------------------------

    composition VARCHAR(100),

    echogenicity VARCHAR(100),

    margins VARCHAR(100),

    calcifications VARCHAR(100),

    tirads VARCHAR(20),

    reportbacaf TEXT,

    reporteco TEXT,

    case_notes TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. Ultrasound Images + Annotation Information
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.ultrasound_images (
    id BIGSERIAL PRIMARY KEY,

    ultrasound_case_id BIGINT NOT NULL
        REFERENCES multimodal.ultrasound_cases(id)
        ON DELETE CASCADE,

    image_number INTEGER NOT NULL,

    image_filename VARCHAR(255) NOT NULL,

    image_path TEXT NOT NULL,

    mask_filename VARCHAR(255),

    mask_path TEXT,

    width INTEGER,

    height INTEGER,

    has_annotation BOOLEAN NOT NULL DEFAULT FALSE,

    annotation_points JSONB,

    region_type VARCHAR(50),

    number_of_annotation_points INTEGER,

    -- Model generated segmentation evidence
    segmentation_pixels INTEGER,

    segmentation_area_ratio NUMERIC,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (
        ultrasound_case_id,
        image_number
    )
);

-- ============================================================
-- 7. AI Analyses
-- Clinical + Ultrasound Decision-Support Results
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.ai_analyses (
    id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES multimodal.patients(id)
        ON DELETE CASCADE,

    clinical_record_id BIGINT
        REFERENCES multimodal.clinical_records(id)
        ON DELETE SET NULL,

    ultrasound_image_id BIGINT
        REFERENCES multimodal.ultrasound_images(id)
        ON DELETE SET NULL,

    -- --------------------------------------------------------
    -- Clinical model result
    -- --------------------------------------------------------

    clinical_top_prediction VARCHAR(20),

    clinical_top_probability NUMERIC,

    clinical_predictions JSONB,

    -- --------------------------------------------------------
    -- Ultrasound model result
    -- --------------------------------------------------------

    ultrasound_segmentation_area NUMERIC,

    ultrasound_evidence JSONB,

    -- --------------------------------------------------------
    -- Multimodal result
    -- --------------------------------------------------------

    fusion_method VARCHAR(100)
        DEFAULT 'Late Evidence Integration',

    multimodal_summary JSONB,

    model_version VARCHAR(100),

    status VARCHAR(30)
        NOT NULL DEFAULT 'completed',

    requires_doctor_review BOOLEAN
        NOT NULL DEFAULT TRUE,

    created_by INTEGER
        REFERENCES multimodal.users(id)
        ON DELETE SET NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 8. AI Recommendations
-- AI is decision support only
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.ai_recommendations (
    id BIGSERIAL PRIMARY KEY,

    patient_id BIGINT NOT NULL
        REFERENCES multimodal.patients(id)
        ON DELETE CASCADE,

    ai_analysis_id BIGINT
        REFERENCES multimodal.ai_analyses(id)
        ON DELETE SET NULL,

    recommendation_text TEXT,

    evidence_summary TEXT,

    confidence NUMERIC,

    doctor_status VARCHAR(30)
        NOT NULL DEFAULT 'pending_review',

    doctor_notes TEXT,

    reviewed_by INTEGER
        REFERENCES multimodal.users(id)
        ON DELETE SET NULL,

    reviewed_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 9. Audit Logs
-- ============================================================

CREATE TABLE IF NOT EXISTS multimodal.audit_logs (
    id BIGSERIAL PRIMARY KEY,

    user_id INTEGER
        REFERENCES multimodal.users(id)
        ON DELETE SET NULL,

    action VARCHAR(100) NOT NULL,

    entity_type VARCHAR(100),

    entity_id BIGINT,

    description TEXT,

    ip_address VARCHAR(100),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_users_role
ON multimodal.users(role_id);

CREATE INDEX IF NOT EXISTS idx_patients_code
ON multimodal.patients(patient_code);

CREATE INDEX IF NOT EXISTS idx_clinical_patient
ON multimodal.clinical_records(patient_id);

CREATE INDEX IF NOT EXISTS idx_clinical_source_patient
ON multimodal.clinical_records(source_patient_id);

CREATE INDEX IF NOT EXISTS idx_clinical_target
ON multimodal.clinical_records(target_code);

CREATE INDEX IF NOT EXISTS idx_ultrasound_patient
ON multimodal.ultrasound_cases(patient_id);

CREATE INDEX IF NOT EXISTS idx_ultrasound_case_number
ON multimodal.ultrasound_cases(case_number);

CREATE INDEX IF NOT EXISTS idx_ultrasound_images_case
ON multimodal.ultrasound_images(ultrasound_case_id);

CREATE INDEX IF NOT EXISTS idx_ultrasound_tirads
ON multimodal.ultrasound_cases(tirads);

CREATE INDEX IF NOT EXISTS idx_ai_patient
ON multimodal.ai_analyses(patient_id);

CREATE INDEX IF NOT EXISTS idx_ai_recommendation_patient
ON multimodal.ai_recommendations(patient_id);

CREATE INDEX IF NOT EXISTS idx_audit_user
ON multimodal.audit_logs(user_id);

-- ============================================================
-- END OF SCHEMA
-- ============================================================
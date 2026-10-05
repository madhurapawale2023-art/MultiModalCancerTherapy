-- ============================================================
-- MultiModalCancerTherapy
-- Seed Data
-- PostgreSQL
-- ============================================================

-- ============================================================
-- 1. Insert Roles
-- ============================================================

INSERT INTO multimodal.roles (
    role_name,
    description
)
VALUES
(
    'Senior Doctor',
    'Final clinical decision authority and treatment approval'
),
(
    'Assistant Doctor',
    'Supports clinical assessment and patient management'
),
(
    'Pathologist',
    'Manages pathology-related information and reports'
),
(
    'Radiologist',
    'Manages imaging and ultrasound-related information'
),
(
    'Lab Staff',
    'Manages laboratory test information and reports'
),
(
    'Admin',
    'Manages users, system access and administration'
)
ON CONFLICT (role_name)
DO NOTHING;


-- ============================================================
-- 2. Enable pgcrypto for password hashing
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ============================================================
-- 3. Insert Demo Users
-- ============================================================
-- Demo passwords are hashed before storage.
--
-- IMPORTANT:
-- Change these demo passwords before production use.
-- ============================================================


-- ------------------------------------------------------------
-- Admin
-- Username: admin
-- Password: Admin@123
-- ------------------------------------------------------------

INSERT INTO multimodal.users (
    username,
    full_name,
    email,
    password_hash,
    role_id,
    is_active
)
SELECT
    'admin',
    'System Administrator',
    'admin@multimodalcancer.local',
    crypt(
        'Admin@123',
        gen_salt('bf')
    ),
    id,
    TRUE
FROM multimodal.roles
WHERE role_name = 'Admin'
ON CONFLICT (username)
DO NOTHING;


-- ------------------------------------------------------------
-- Senior Doctor
-- Username: senior.doctor
-- Password: Doctor@123
-- ------------------------------------------------------------

INSERT INTO multimodal.users (
    username,
    full_name,
    email,
    password_hash,
    role_id,
    is_active
)
SELECT
    'senior.doctor',
    'Senior Doctor',
    'senior.doctor@multimodalcancer.local',
    crypt(
        'Doctor@123',
        gen_salt('bf')
    ),
    id,
    TRUE
FROM multimodal.roles
WHERE role_name = 'Senior Doctor'
ON CONFLICT (username)
DO NOTHING;


-- ------------------------------------------------------------
-- Assistant Doctor
-- Username: assistant.doctor
-- Password: Doctor@123
-- ------------------------------------------------------------

INSERT INTO multimodal.users (
    username,
    full_name,
    email,
    password_hash,
    role_id,
    is_active
)
SELECT
    'assistant.doctor',
    'Assistant Doctor',
    'assistant.doctor@multimodalcancer.local',
    crypt(
        'Doctor@123',
        gen_salt('bf')
    ),
    id,
    TRUE
FROM multimodal.roles
WHERE role_name = 'Assistant Doctor'
ON CONFLICT (username)
DO NOTHING;


-- ------------------------------------------------------------
-- Pathologist
-- Username: pathologist
-- Password: Staff@123
-- ------------------------------------------------------------

INSERT INTO multimodal.users (
    username,
    full_name,
    email,
    password_hash,
    role_id,
    is_active
)
SELECT
    'pathologist',
    'Pathologist',
    'pathologist@multimodalcancer.local',
    crypt(
        'Staff@123',
        gen_salt('bf')
    ),
    id,
    TRUE
FROM multimodal.roles
WHERE role_name = 'Pathologist'
ON CONFLICT (username)
DO NOTHING;


-- ------------------------------------------------------------
-- Radiologist
-- Username: radiologist
-- Password: Staff@123
-- ------------------------------------------------------------

INSERT INTO multimodal.users (
    username,
    full_name,
    email,
    password_hash,
    role_id,
    is_active
)
SELECT
    'radiologist',
    'Radiologist',
    'radiologist@multimodalcancer.local',
    crypt(
        'Staff@123',
        gen_salt('bf')
    ),
    id,
    TRUE
FROM multimodal.roles
WHERE role_name = 'Radiologist'
ON CONFLICT (username)
DO NOTHING;


-- ------------------------------------------------------------
-- Lab Staff
-- Username: lab.staff
-- Password: Staff@123
-- ------------------------------------------------------------

INSERT INTO multimodal.users (
    username,
    full_name,
    email,
    password_hash,
    role_id,
    is_active
)
SELECT
    'lab.staff',
    'Lab Staff',
    'lab.staff@multimodalcancer.local',
    crypt(
        'Staff@123',
        gen_salt('bf')
    ),
    id,
    TRUE
FROM multimodal.roles
WHERE role_name = 'Lab Staff'
ON CONFLICT (username)
DO NOTHING;


-- ============================================================
-- 4. Verification
-- ============================================================

SELECT
    r.id,
    r.role_name,
    r.description
FROM multimodal.roles AS r
ORDER BY r.id;


SELECT
    u.id,
    u.username,
    u.full_name,
    u.email,
    r.role_name,
    u.is_active
FROM multimodal.users AS u
LEFT JOIN multimodal.roles AS r
    ON r.id = u.role_id
ORDER BY u.id;


-- ============================================================
-- END OF SEED
-- ============================================================
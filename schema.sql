CREATE TABLE IF NOT EXISTS H2FPEF (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name VARCHAR(255) ,
    age INTEGER ,
    bmi REAL ,
    E_e REAL ,
    pasp REAL ,
    af INTEGER,
    date_of_echo Date
);

CREATE TABLE IF NOT EXISTS qrisk3_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name VARCHAR(255),
    age INTEGER NOT NULL,
    sex VARCHAR(10) NOT NULL CHECK (sex IN ('male', 'female')),
    ethnicity INTEGER DEFAULT 0, -- default: white
    smoker_status INTEGER DEFAULT 0, -- 0: non-smoker to 4: heavy smoker
    bmi FLOAT DEFAULT NULL,
    systolic_bp FLOAT DEFAULT NULL,
    bp_variability FLOAT DEFAULT 0,
    cholesterol_ratio FLOAT DEFAULT NULL,
    townsend_index FLOAT DEFAULT 0,

    -- boolean medical history flags
    has_af BOOLEAN DEFAULT FALSE,
    has_atypical_antipsy BOOLEAN DEFAULT FALSE,
    on_corticosteroids BOOLEAN DEFAULT FALSE,
    has_impotence BOOLEAN DEFAULT FALSE,
    has_migraine BOOLEAN DEFAULT FALSE,
    has_ra BOOLEAN DEFAULT FALSE,
    has_ckd BOOLEAN DEFAULT FALSE,
    has_learning_disability BOOLEAN DEFAULT FALSE,
    has_sle BOOLEAN DEFAULT FALSE,
    on_hypertension_treatment BOOLEAN DEFAULT FALSE,
    has_type1_diabetes BOOLEAN DEFAULT FALSE,
    has_type2_diabetes BOOLEAN DEFAULT FALSE,
    has_family_history BOOLEAN DEFAULT FALSE,
    survival_period INTEGER DEFAULT 10, -- typically 10 years
    date_of_echo Date
);


CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    sex VARCHAR(10) NOT NULL CHECK (sex IN ('male', 'female')),
    bmi FLOAT DEFAULT NULL,
    systolic_bp FLOAT DEFAULT NULL,
    cholesterol_ratio FLOAT DEFAULT NULL,
    E_e REAL ,
    pasp REAL ,
    af integer,
    qrisk3_score FLOAT DEFAULT NULL,
    H2FPEF_score,
    date_of_echo Date
);


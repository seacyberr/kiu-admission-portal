-- KIU Admission Portal Database Schema
-- Comprehensive system for certificate to PhD level admissions

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Campuses
CREATE TABLE campuses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schools/Faculties
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    campus_id UUID REFERENCES campuses(id),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Academic Levels
CREATE TABLE academic_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level_name VARCHAR(50) NOT NULL, -- Certificate, Diploma, Bachelor, PGD, Masters, PhD
    level_code VARCHAR(10) NOT NULL UNIQUE,
    duration_years INTEGER NOT NULL,
    minimum_entry_points INTEGER, -- UACE points required
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Programs
CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_code VARCHAR(20) NOT NULL UNIQUE,
    program_name VARCHAR(200) NOT NULL,
    school_id UUID REFERENCES schools(id),
    academic_level_id UUID REFERENCES academic_levels(id),
    description TEXT,
    duration_years INTEGER NOT NULL,
    minimum_uace_points INTEGER,
    minimum_uce_aggregate INTEGER,
    specific_requirements TEXT, -- Subject combinations, etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UNEB Grading Systems
CREATE TABLE uace_grading (
    grade CHAR(1) PRIMARY KEY,
    points INTEGER NOT NULL,
    description VARCHAR(50),
    is_principal_pass BOOLEAN DEFAULT false
);

CREATE TABLE subsidiary_grading (
    grade VARCHAR(5) PRIMARY KEY, -- D1, D2, C3-C6, P7-P8, F9
    points INTEGER NOT NULL,
    description VARCHAR(50)
);

CREATE TABLE uce_grading (
    grade VARCHAR(2) PRIMARY KEY, -- D1-D9
    aggregate_range VARCHAR(20),
    description VARCHAR(50)
);

-- Qualification Types
CREATE TABLE qualification_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_name VARCHAR(100) NOT NULL, -- UCE, UACE, Diploma, Degree, etc.
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applicants
CREATE TABLE applicants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(10),
    nationality VARCHAR(50),
    district VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Academic Qualifications
CREATE TABLE academic_qualifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id UUID REFERENCES applicants(id),
    qualification_type_id UUID REFERENCES qualification_types(id),
    institution_name VARCHAR(200) NOT NULL,
    year_completed INTEGER NOT NULL,
    index_number VARCHAR(50),
    certificate_file_path VARCHAR(500), -- Path to uploaded certificate
    is_verified BOOLEAN DEFAULT false,
    verification_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UACE Results
CREATE TABLE uace_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    qualification_id UUID REFERENCES academic_qualifications(id),
    subject_name VARCHAR(100) NOT NULL,
    grade CHAR(1) NOT NULL,
    points INTEGER NOT NULL,
    is_principal BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UCE Results
CREATE TABLE uce_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    qualification_id UUID REFERENCES academic_qualifications(id),
    subject_name VARCHAR(100) NOT NULL,
    grade VARCHAR(2) NOT NULL,
    aggregate INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_number VARCHAR(20) UNIQUE NOT NULL,
    applicant_id UUID REFERENCES applicants(id),
    program_id UUID REFERENCES programs(id),
    intake_year INTEGER NOT NULL,
    intake_semester VARCHAR(20), -- January, May, August
    application_status VARCHAR(20) DEFAULT 'pending', -- pending, under_review, accepted, rejected
    total_uace_points INTEGER,
    total_uce_aggregate INTEGER,
    recommendation_score DECIMAL(5,2),
    admission_decision VARCHAR(20),
    decision_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application Documents
CREATE TABLE application_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID REFERENCES applications(id),
    document_type VARCHAR(50) NOT NULL, -- birth_cert, national_id, passport_photo, etc.
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Program Recommendations
CREATE TABLE program_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id UUID REFERENCES applicants(id),
    program_id UUID REFERENCES programs(id),
    match_score DECIMAL(5,2) NOT NULL,
    match_reason TEXT,
    based_on_qualifications TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Configuration
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial data
INSERT INTO campuses (name, location, description) VALUES
('Main Campus', 'Kansanga, Kampala', 'KIU Main Campus - Administration and Non-Health Programs'),
('Western Campus', 'Ishaka, Bushenyi District', 'KIU Western Campus - Health Sciences Hub');

INSERT INTO academic_levels (level_name, level_code, duration_years, minimum_entry_points) VALUES
('Certificate', 'CERT', 1, NULL),
('Diploma', 'DIP', 2, 4),
('Bachelor', 'BACH', 3, 8),
('Postgraduate Diploma', 'PGD', 1, 6),
('Masters', 'MAST', 2, 10),
('PhD', 'PHD', 3, 15);

INSERT INTO uace_grading (grade, points, description, is_principal_pass) VALUES
('A', 6, 'Excellent', true),
('B', 5, 'Very Good', true),
('C', 4, 'Good', true),
('D', 3, 'Fair', true),
('E', 2, 'Poor', true),
('O', 1, 'Subsidiary Pass', false),
('F', 0, 'Fail', false);

INSERT INTO subsidiary_grading (grade, points, description) VALUES
('D1', 1, 'Distinction 1'),
('D2', 1, 'Distinction 2'),
('C3', 1, 'Credit 3'),
('C4', 1, 'Credit 4'),
('C5', 1, 'Credit 5'),
('C6', 1, 'Credit 6'),
('P7', 1, 'Pass 7'),
('P8', 1, 'Pass 8'),
('F9', 0, 'Fail 9');

INSERT INTO uce_grading (grade, aggregate_range, description) VALUES
('D1', '8-12', 'Excellent'),
('D2', '13-23', 'Very Good'),
('C3', '24-27', 'Good'),
('C4', '28-30', 'Good'),
('C5', '31-33', 'Fair'),
('C6', '34-36', 'Fair'),
('P7', '37-38', 'Pass'),
('P8', '39-40', 'Pass'),
('P9', '41-42', 'Pass'),
('F9', '43+', 'Fail');

INSERT INTO qualification_types (type_name, description) VALUES
('UCE', 'Uganda Certificate of Education'),
('UACE', 'Uganda Advanced Certificate of Education'),
('Certificate', 'National Certificate'),
('Diploma', 'National Diploma'),
('Bachelor', 'Bachelor Degree'),
('Masters', 'Masters Degree'),
('PhD', 'Doctor of Philosophy');

-- Indexes for better performance
CREATE INDEX idx_applicants_email ON applicants(email);
CREATE INDEX idx_applications_applicant ON applications(applicant_id);
CREATE INDEX idx_applications_program ON applications(program_id);
CREATE INDEX idx_applications_status ON applications(application_status);
CREATE INDEX idx_applications_submission_date ON applications(submitted_at DESC);
CREATE INDEX idx_programs_school ON programs(school_id);
CREATE INDEX idx_programs_level ON programs(academic_level_id);
CREATE INDEX idx_programs_active ON programs(is_active);
CREATE INDEX idx_programs_code ON programs(program_code);
CREATE INDEX idx_schools_campus ON schools(campus_id);
CREATE INDEX idx_schools_active ON schools(is_active);
CREATE INDEX idx_academic_levels_active ON academic_levels(is_active);
CREATE INDEX idx_qualifications_applicant ON academic_qualifications(applicant_id);
CREATE INDEX idx_qualifications_type ON academic_qualifications(qualification_type_id);
CREATE INDEX idx_recommendations_applicant ON program_recommendations(applicant_id);
CREATE INDEX idx_recommendations_program ON program_recommendations(program_id);
CREATE INDEX idx_recommendations_score ON program_recommendations(match_score DESC);
CREATE INDEX idx_application_docs_app ON application_documents(application_id);
CREATE INDEX idx_application_docs_type ON application_documents(document_type);

-- Composite indexes for common queries
CREATE INDEX idx_applications_status_date ON applications(application_status, submitted_at DESC);
CREATE INDEX idx_programs_level_active ON programs(academic_level_id, is_active);
CREATE INDEX idx_applications_program_status ON applications(program_id, application_status);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_campuses_updated_at BEFORE UPDATE ON campuses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_schools_updated_at BEFORE UPDATE ON schools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_academic_levels_updated_at BEFORE UPDATE ON academic_levels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_applicants_updated_at BEFORE UPDATE ON applicants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_academic_qualifications_updated_at BEFORE UPDATE ON academic_qualifications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

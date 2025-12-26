-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) CHECK (role IN ('user', 'admin')) DEFAULT 'user'
);

-- 2. Create Lab Usage Table
CREATE TABLE IF NOT EXISTS lab_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lab_name VARCHAR(100) NOT NULL,
    staff_name VARCHAR(100) NOT NULL,
    class VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Insert Initial Data
INSERT INTO users (username, password, role) VALUES 
('admin', 'admin123', 'admin'),
('john', 'john123', 'user'),
('Nithya', 'Nithya001', 'user'),
('Rakshana', 'rakshana002', 'user'),
('Anitha', 'Anitha003', 'user'),
('Muruganandam', 'MuruAdmin01', 'admin'),
('Muthupondi', 'MuthuAdmin02', 'admin'),
('Nehru', 'NehruAdmin03', 'admin')
ON CONFLICT (username) DO NOTHING;

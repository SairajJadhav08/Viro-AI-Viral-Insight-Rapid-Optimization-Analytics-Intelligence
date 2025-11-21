-- Migration: Research News Feed
-- Created: 2025-11-20
-- Description: Create research news table for Explore page

CREATE TABLE IF NOT EXISTS research_news (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    source VARCHAR(200),
    date DATE,
    tags JSON,
    credibility VARCHAR(50) DEFAULT 'Peer-reviewed',
    relevance INT DEFAULT 50,
    url VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_credibility (credibility),
    INDEX idx_relevance (relevance)
);

-- Insert sample research news data
INSERT INTO research_news (title, summary, source, date, tags, credibility, relevance) VALUES
('Novel Antiviral Compound Shows Promise Against Multiple Coronaviruses', 
 'Researchers have identified a broad-spectrum antiviral that demonstrates efficacy against SARS-CoV-2 and related coronaviruses in preclinical studies.',
 'Nature Medicine', '2025-11-10', 
 '["Antiviral Discovery", "Coronaviruses"]', 
 'Peer-reviewed', 95),
 
('AI-Driven Protein Structure Prediction Accelerates Drug Design', 
 'Machine learning models are revolutionizing how scientists predict protein folding, reducing drug discovery timelines from years to months.',
 'Science', '2025-11-09', 
 '["Structural Biology", "AI"]', 
 'Peer-reviewed', 92),
 
('WHO Reports Emerging Viral Variant in Southeast Asia', 
 'New surveillance data indicates a viral mutation with enhanced transmissibility detected in multiple countries, prompting increased monitoring.',
 'WHO', '2025-11-08', 
 '["Outbreaks", "Genomics"]', 
 'Government Notice', 88);


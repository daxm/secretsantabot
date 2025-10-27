-- Secret Santa Bot - Database Seed Script
-- This script prepopulates the database with test participants
-- IMPORTANT: This file is in .gitignore and will NOT be committed to git
-- You can add real names and emails here for testing

-- Clear existing data first (reset everything)
DELETE FROM match;
DELETE FROM participant;
DELETE FROM settings;

-- Insert test participants
-- Modify these with your actual test users
INSERT INTO participant (name, email, gift_preference) VALUES
('Alice Johnson', 'alice@example.com', 'Books, coffee, or anything cozy'),
('Bob Smith', 'bob@example.com', 'Tech gadgets, gaming accessories'),
('Carol Davis', 'carol@example.com', 'Art supplies, craft materials'),
('David Wilson', 'david@example.com', 'Sports equipment, fitness gear'),
('Eve Martinez', 'eve@example.com', 'Plants, gardening tools, or home decor');

-- Add more participants as needed:
-- INSERT INTO participant (name, email, gift_preference) VALUES
-- ('Your Name', 'your.email@example.com', 'Your preferences here'),
-- ('Another Person', 'another@example.com', 'Their preferences');

-- Verify the inserts
SELECT COUNT(*) as total_participants FROM participant;
SELECT id, name, email FROM participant ORDER BY id;

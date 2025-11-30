-- ============================================================================
-- AfroKen LLM - Chat Metrics Seed Data
-- ============================================================================
-- This script populates the chat_metrics table with sample data
-- for testing the dual implementation (dummy + real data) in the Dashboard
-- ============================================================================
-- Run this script to add metrics that will combine with dummy data
-- Usage: psql -U afroken -d afroken_llm_db -f seed_chat_metrics.sql
-- ============================================================================

BEGIN;

-- Clear existing metrics (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE chat_metrics CASCADE;

-- Insert sample chat metrics for the last 30 days
-- Each entry represents hourly aggregated data

-- Week 1 metrics
INSERT INTO chat_metrics (date_hour, total_conversations, total_messages, total_queries, average_response_time_ms, unique_users, new_users, top_services, top_intents, average_satisfaction_score, language_distribution, sentiment_distribution, total_cost_usd, average_cost_per_request) VALUES
-- Day 1
('2024-11-01 08:00:00+00', 45, 120, 45, 1200, 38, 5, 
 '["NHIF", "KRA", "Huduma"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 12}, {"intent": "KRA PIN", "count": 8}, {"intent": "Huduma Appointment", "count": 6}]'::jsonb,
 4.2, 
 '{"sw": 28, "en": 12, "sheng": 5}'::jsonb,
 '{"positive": 32, "neutral": 10, "negative": 3}'::jsonb,
 2.45, 0.054),
('2024-11-01 12:00:00+00', 78, 195, 78, 1100, 65, 8,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 22}, {"intent": "KRA PIN", "count": 15}, {"intent": "NSSF Check", "count": 10}]'::jsonb,
 4.3,
 '{"sw": 52, "en": 20, "sheng": 6}'::jsonb,
 '{"positive": 55, "neutral": 18, "negative": 5}'::jsonb,
 4.12, 0.053),
('2024-11-01 16:00:00+00', 62, 155, 62, 1300, 54, 6,
 '["KRA", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 18}, {"intent": "Huduma Appointment", "count": 12}, {"intent": "Passport Application", "count": 8}]'::jsonb,
 4.1,
 '{"sw": 45, "en": 14, "sheng": 3}'::jsonb,
 '{"positive": 48, "neutral": 12, "negative": 2}'::jsonb,
 3.28, 0.053),

-- Day 2
('2024-11-02 08:00:00+00', 52, 130, 52, 1150, 44, 7,
 '["NHIF", "KRA", "Business Registration"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 15}, {"intent": "KRA PIN", "count": 11}, {"intent": "Business Registration", "count": 7}]'::jsonb,
 4.4,
 '{"sw": 35, "en": 14, "sheng": 3}'::jsonb,
 '{"positive": 42, "neutral": 8, "negative": 2}'::jsonb,
 2.89, 0.056),
('2024-11-02 12:00:00+00', 85, 212, 85, 1050, 72, 10,
 '["NHIF", "KRA", "NSSF", "Huduma"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 25}, {"intent": "KRA PIN", "count": 18}, {"intent": "NSSF Check", "count": 12}, {"intent": "Huduma Appointment", "count": 10}]'::jsonb,
 4.5,
 '{"sw": 68, "en": 14, "sheng": 3}'::jsonb,
 '{"positive": 72, "neutral": 11, "negative": 2}'::jsonb,
 4.76, 0.056),
('2024-11-02 16:00:00+00', 68, 170, 68, 1250, 58, 5,
 '["KRA", "Huduma", "National ID"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 20}, {"intent": "Huduma Appointment", "count": 14}, {"intent": "ID Application", "count": 9}]'::jsonb,
 4.2,
 '{"sw": 52, "en": 13, "sheng": 3}'::jsonb,
 '{"positive": 58, "neutral": 9, "negative": 1}'::jsonb,
 3.81, 0.056),

-- Day 3
('2024-11-03 08:00:00+00', 48, 120, 48, 1180, 40, 6,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 14}, {"intent": "KRA PIN", "count": 10}]'::jsonb,
 4.3,
 '{"sw": 32, "en": 13, "sheng": 3}'::jsonb,
 '{"positive": 38, "neutral": 9, "negative": 1}'::jsonb,
 2.69, 0.056),
('2024-11-03 12:00:00+00', 92, 230, 92, 1020, 78, 12,
 '["NHIF", "KRA", "NSSF", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 28}, {"intent": "KRA PIN", "count": 20}, {"intent": "NSSF Check", "count": 14}, {"intent": "Huduma Appointment", "count": 12}, {"intent": "Passport Application", "count": 8}]'::jsonb,
 4.6,
 '{"sw": 74, "en": 15, "sheng": 3}'::jsonb,
 '{"positive": 82, "neutral": 9, "negative": 1}'::jsonb,
 5.15, 0.056),
('2024-11-03 16:00:00+00', 71, 178, 71, 1280, 61, 4,
 '["KRA", "Huduma", "Business Registration"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 22}, {"intent": "Huduma Appointment", "count": 15}, {"intent": "Business Registration", "count": 10}]'::jsonb,
 4.3,
 '{"sw": 57, "en": 11, "sheng": 3}'::jsonb,
 '{"positive": 64, "neutral": 6, "negative": 1}'::jsonb,
 3.98, 0.056),

-- Day 4
('2024-11-04 08:00:00+00', 55, 138, 55, 1120, 47, 8,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 16}, {"intent": "KRA PIN", "count": 12}, {"intent": "NSSF Check", "count": 8}]'::jsonb,
 4.4,
 '{"sw": 40, "en": 12, "sheng": 3}'::jsonb,
 '{"positive": 48, "neutral": 6, "negative": 1}'::jsonb,
 3.08, 0.056),
('2024-11-04 12:00:00+00', 88, 220, 88, 1080, 75, 11,
 '["NHIF", "KRA", "NSSF", "Huduma"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 26}, {"intent": "KRA PIN", "count": 19}, {"intent": "NSSF Check", "count": 13}, {"intent": "Huduma Appointment", "count": 11}]'::jsonb,
 4.5,
 '{"sw": 71, "en": 14, "sheng": 3}'::jsonb,
 '{"positive": 79, "neutral": 8, "negative": 1}'::jsonb,
 4.93, 0.056),
('2024-11-04 16:00:00+00', 65, 163, 65, 1220, 56, 5,
 '["KRA", "Huduma", "National ID"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 19}, {"intent": "Huduma Appointment", "count": 13}, {"intent": "ID Application", "count": 8}]'::jsonb,
 4.2,
 '{"sw": 52, "en": 11, "sheng": 2}'::jsonb,
 '{"positive": 58, "neutral": 6, "negative": 1}'::jsonb,
 3.64, 0.056),

-- Day 5
('2024-11-05 08:00:00+00', 50, 125, 50, 1140, 43, 7,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 15}, {"intent": "KRA PIN", "count": 11}]'::jsonb,
 4.3,
 '{"sw": 36, "en": 12, "sheng": 2}'::jsonb,
 '{"positive": 42, "neutral": 7, "negative": 1}'::jsonb,
 2.80, 0.056),
('2024-11-05 12:00:00+00', 90, 225, 90, 1040, 77, 13,
 '["NHIF", "KRA", "NSSF", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 27}, {"intent": "KRA PIN", "count": 20}, {"intent": "NSSF Check", "count": 14}, {"intent": "Huduma Appointment", "count": 12}, {"intent": "Passport Application", "count": 9}]'::jsonb,
 4.6,
 '{"sw": 72, "en": 15, "sheng": 3}'::jsonb,
 '{"positive": 81, "neutral": 8, "negative": 1}'::jsonb,
 5.04, 0.056),
('2024-11-05 16:00:00+00', 70, 175, 70, 1260, 60, 4,
 '["KRA", "Huduma", "Business Registration"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 21}, {"intent": "Huduma Appointment", "count": 14}, {"intent": "Business Registration", "count": 9}]'::jsonb,
 4.3,
 '{"sw": 58, "en": 10, "sheng": 2}'::jsonb,
 '{"positive": 63, "neutral": 6, "negative": 1}'::jsonb,
 3.92, 0.056),

-- Day 6 (Saturday - lower volume)
('2024-11-06 08:00:00+00', 35, 88, 35, 1200, 30, 4,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 10}, {"intent": "KRA PIN", "count": 8}]'::jsonb,
 4.2,
 '{"sw": 26, "en": 7, "sheng": 2}'::jsonb,
 '{"positive": 29, "neutral": 5, "negative": 1}'::jsonb,
 1.96, 0.056),
('2024-11-06 12:00:00+00', 42, 105, 42, 1150, 36, 5,
 '["NHIF", "KRA", "Huduma"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 12}, {"intent": "KRA PIN", "count": 9}, {"intent": "Huduma Appointment", "count": 7}]'::jsonb,
 4.4,
 '{"sw": 32, "en": 9, "sheng": 1}'::jsonb,
 '{"positive": 37, "neutral": 4, "negative": 1}'::jsonb,
 2.35, 0.056),

-- Day 7 (Sunday - minimal)
('2024-11-07 10:00:00+00', 18, 45, 18, 1300, 15, 2,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 6}, {"intent": "KRA PIN", "count": 4}]'::jsonb,
 4.1,
 '{"sw": 14, "en": 3, "sheng": 1}'::jsonb,
 '{"positive": 15, "neutral": 2, "negative": 1}'::jsonb,
 1.01, 0.056);

-- Add more recent metrics (last 7 days) for better testing
INSERT INTO chat_metrics (date_hour, total_conversations, total_messages, total_queries, average_response_time_ms, unique_users, new_users, top_services, top_intents, average_satisfaction_score, language_distribution, sentiment_distribution, total_cost_usd, average_cost_per_request) VALUES
-- Recent Day 1
(NOW() - INTERVAL '7 days' + INTERVAL '8 hours', 58, 145, 58, 1100, 50, 9,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 17}, {"intent": "KRA PIN", "count": 13}, {"intent": "NSSF Check", "count": 9}]'::jsonb,
 4.4,
 '{"sw": 45, "en": 11, "sheng": 2}'::jsonb,
 '{"positive": 52, "neutral": 5, "negative": 1}'::jsonb,
 3.25, 0.056),
(NOW() - INTERVAL '7 days' + INTERVAL '12 hours', 95, 238, 95, 1000, 81, 14,
 '["NHIF", "KRA", "NSSF", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 29}, {"intent": "KRA PIN", "count": 21}, {"intent": "NSSF Check", "count": 15}, {"intent": "Huduma Appointment", "count": 13}, {"intent": "Passport Application", "count": 10}]'::jsonb,
 4.7,
 '{"sw": 76, "en": 16, "sheng": 3}'::jsonb,
 '{"positive": 86, "neutral": 8, "negative": 1}'::jsonb,
 5.32, 0.056),
(NOW() - INTERVAL '7 days' + INTERVAL '16 hours', 72, 180, 72, 1200, 62, 6,
 '["KRA", "Huduma", "National ID"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 22}, {"intent": "Huduma Appointment", "count": 15}, {"intent": "ID Application", "count": 9}]'::jsonb,
 4.3,
 '{"sw": 60, "en": 10, "sheng": 2}'::jsonb,
 '{"positive": 65, "neutral": 6, "negative": 1}'::jsonb,
 4.03, 0.056),

-- Recent Day 2
(NOW() - INTERVAL '6 days' + INTERVAL '8 hours', 60, 150, 60, 1080, 52, 10,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 18}, {"intent": "KRA PIN", "count": 14}, {"intent": "NSSF Check", "count": 10}]'::jsonb,
 4.5,
 '{"sw": 47, "en": 11, "sheng": 2}'::jsonb,
 '{"positive": 54, "neutral": 5, "negative": 1}'::jsonb,
 3.36, 0.056),
(NOW() - INTERVAL '6 days' + INTERVAL '12 hours', 98, 245, 98, 980, 84, 15,
 '["NHIF", "KRA", "NSSF", "Huduma", "Passport"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 30}, {"intent": "KRA PIN", "count": 22}, {"intent": "NSSF Check", "count": 16}, {"intent": "Huduma Appointment", "count": 14}, {"intent": "Passport Application", "count": 11}]'::jsonb,
 4.8,
 '{"sw": 78, "en": 17, "sheng": 3}'::jsonb,
 '{"positive": 89, "neutral": 8, "negative": 1}'::jsonb,
 5.49, 0.056),
(NOW() - INTERVAL '6 days' + INTERVAL '16 hours', 75, 188, 75, 1180, 65, 7,
 '["KRA", "Huduma", "Business Registration"]'::jsonb,
 '[{"intent": "KRA PIN", "count": 23}, {"intent": "Huduma Appointment", "count": 16}, {"intent": "Business Registration", "count": 10}]'::jsonb,
 4.4,
 '{"sw": 63, "en": 10, "sheng": 2}'::jsonb,
 '{"positive": 68, "neutral": 6, "negative": 1}'::jsonb,
 4.20, 0.056),

-- Recent Day 3 (Today - for real-time testing)
(NOW() - INTERVAL '2 hours', 45, 113, 45, 1050, 39, 8,
 '["NHIF", "KRA"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 14}, {"intent": "KRA PIN", "count": 11}]'::jsonb,
 4.5,
 '{"sw": 34, "en": 9, "sheng": 2}'::jsonb,
 '{"positive": 40, "neutral": 4, "negative": 1}'::jsonb,
 2.52, 0.056),
(NOW() - INTERVAL '1 hour', 52, 130, 52, 1020, 45, 9,
 '["NHIF", "KRA", "NSSF"]'::jsonb,
 '[{"intent": "NHIF Registration", "count": 16}, {"intent": "KRA PIN", "count": 12}, {"intent": "NSSF Check", "count": 8}]'::jsonb,
 4.6,
 '{"sw": 40, "en": 10, "sheng": 2}'::jsonb,
 '{"positive": 47, "neutral": 4, "negative": 1}'::jsonb,
 2.91, 0.056);

COMMIT;

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- This script has inserted sample chat metrics data:
-- - Historical data for the past 7 days
-- - Recent data for testing
-- - Current hour data for real-time display
--
-- The metrics include:
-- - Total conversations, messages, queries
-- - Average response times
-- - Unique users and new users
-- - Top services and intents
-- - Satisfaction scores
-- - Language and sentiment distribution
-- - Cost tracking
--
-- These metrics will be combined with dummy data in the Dashboard
-- to demonstrate dual implementation (dummy + real data)
-- ============================================================================

SELECT 'Chat metrics seed data inserted successfully!' AS status;
SELECT 
    COUNT(*) as total_metrics,
    SUM(total_queries) as total_queries_sum,
    AVG(average_satisfaction_score) as avg_satisfaction,
    MIN(date_hour) as earliest_metric,
    MAX(date_hour) as latest_metric
FROM chat_metrics;


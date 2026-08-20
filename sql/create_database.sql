-- Run in the Synapse serverless master database.
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = 'homecare_analytics')
BEGIN
    CREATE DATABASE homecare_analytics;
END;

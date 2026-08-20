/*
Public-safe example of the Synapse Serverless SQL serving layer.

Before running:
1. Replace <storage-account> with your own ADLS Gen2 account.
2. Run in the homecare_analytics database.
3. Ensure the Synapse workspace identity has Storage Blob Data Reader access.
*/

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'care')
    EXEC('CREATE SCHEMA care');

IF EXISTS (SELECT 1 FROM sys.external_data_sources WHERE name = 'care_gold')
    DROP EXTERNAL DATA SOURCE care_gold;

IF NOT EXISTS (SELECT 1 FROM sys.database_scoped_credentials WHERE name = 'WorkspaceIdentity')
    CREATE DATABASE SCOPED CREDENTIAL WorkspaceIdentity WITH IDENTITY = 'Managed Identity';

CREATE EXTERNAL DATA SOURCE care_gold
WITH (
    LOCATION = 'https://<storage-account>.dfs.core.windows.net/gold',
    CREDENTIAL = WorkspaceIdentity
);

CREATE OR ALTER VIEW care.dim_client AS
SELECT * FROM OPENROWSET(
    BULK 'dim_client/dim_client.parquet',
    DATA_SOURCE = 'care_gold',
    FORMAT = 'PARQUET'
) AS r;

CREATE OR ALTER VIEW care.dim_employee AS
SELECT * FROM OPENROWSET(
    BULK 'dim_employee/dim_employee.parquet',
    DATA_SOURCE = 'care_gold',
    FORMAT = 'PARQUET'
) AS r;

CREATE OR ALTER VIEW care.dim_service AS
SELECT * FROM OPENROWSET(
    BULK 'dim_service/dim_service.parquet',
    DATA_SOURCE = 'care_gold',
    FORMAT = 'PARQUET'
) AS r;

CREATE OR ALTER VIEW care.fact_visit_component AS
SELECT * FROM OPENROWSET(
    BULK 'fact_visit/year=*/month=*/*.parquet',
    DATA_SOURCE = 'care_gold',
    FORMAT = 'PARQUET'
) AS r;

CREATE OR ALTER VIEW care.fact_visit AS
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY schedule_id
               ORDER BY last_updated DESC, component_id DESC
           ) AS rn
    FROM OPENROWSET(
        BULK 'fact_visit/year=*/month=*/*.parquet',
        DATA_SOURCE = 'care_gold',
        FORMAT = 'PARQUET'
    ) AS r
)
SELECT * FROM ranked WHERE rn = 1;

CREATE OR ALTER VIEW care.fact_care_summary AS
SELECT * FROM OPENROWSET(
    BULK 'fact_care_summary/fact_care_summary.parquet',
    DATA_SOURCE = 'care_gold',
    FORMAT = 'PARQUET'
) AS r;

-- Representative additional Gold-layer contracts used by BI.
-- In the production-style design, these are created by the same pattern:
--   dim_client_history
--   xref_client_funding_history
--   fact_client_action
--   fact_client_note
--   fact_service_request
--   fact_visit_component_version
--   fact_care_allergy
--   fact_care_assessment
--   fact_care_condition
--   fact_care_goal
--   fact_care_referral
--   xref_careplan_section
--   xref_visit_schedule_component

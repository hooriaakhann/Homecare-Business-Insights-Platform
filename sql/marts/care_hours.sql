/*
Care-hours mart example.

This mart converts visit-level records into scheduled and delivered service hours.
It intentionally contains no production client identifiers or business-specific filters.
*/

CREATE OR ALTER VIEW care.mart_care_hours AS
WITH base AS (
    SELECT
        schedule_id,
        client_id,
        employee_id,
        service_id,
        status,
        TRY_CAST(scheduled_start AS datetime2) AS scheduled_start,
        TRY_CAST(scheduled_end AS datetime2) AS scheduled_end,
        TRY_CAST(actual_start AS datetime2) AS actual_start,
        TRY_CAST(actual_end AS datetime2) AS actual_end
    FROM care.fact_visit
),
hours AS (
    SELECT
        *,
        CASE
            WHEN scheduled_start IS NOT NULL AND scheduled_end IS NOT NULL
            THEN DATEDIFF(minute, scheduled_start, scheduled_end) / 60.0
        END AS scheduled_hours,
        CASE
            WHEN actual_start IS NOT NULL AND actual_end IS NOT NULL
            THEN DATEDIFF(minute, actual_start, actual_end) / 60.0
        END AS delivered_hours
    FROM base
)
SELECT
    schedule_id,
    client_id,
    employee_id,
    service_id,
    status,
    scheduled_start,
    scheduled_end,
    actual_start,
    actual_end,
    scheduled_hours,
    delivered_hours,
    COALESCE(delivered_hours, 0) - COALESCE(scheduled_hours, 0) AS variance_hours
FROM hours;

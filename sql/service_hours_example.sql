-- Synthetic example only. No production schema or business data is included.

CREATE OR ALTER VIEW analytics.vw_monthly_service_hours AS
SELECT
    client_id,
    DATEFROMPARTS(YEAR(scheduled_start), MONTH(scheduled_start), 1) AS service_month,
    SUM(DATEDIFF(MINUTE, scheduled_start, scheduled_end)) / 60.0 AS service_hours,
    COUNT(*) AS visit_count
FROM analytics.fact_visit
WHERE visit_status = 'Completed'
GROUP BY
    client_id,
    DATEFROMPARTS(YEAR(scheduled_start), MONTH(scheduled_start), 1);

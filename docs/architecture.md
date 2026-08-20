# Architecture Notes

## Design goal

The platform converts operational homecare-service API data into analytics-ready datasets while keeping source ingestion, curation, modeling, and reporting concerns separated.

## Orchestration

Durable orchestration coordinates endpoints sequentially or in controlled groups. Each logical entity can choose an ingestion strategy suited to the source behavior:

- **incremental** — request records changed after a stored watermark
- **full** — reload small reference datasets
- **date-range** — extract activity constrained by a time window
- **entity loop** — request child resources for each parent entity

## Storage zones

### Bronze
Immutable raw batches preserve what was returned by the source. Each batch is associated with an ingestion time and partition path.

### Silver
Silver datasets normalize source structures, enforce types, flatten selected nested objects, expand child arrays, and deduplicate records using stable business keys.

### Gold
Gold datasets organize information into facts, dimensions, historical tables, and reporting marts.

## Serving

Synapse Serverless SQL exposes SQL views over Parquet data so BI tooling can query the analytical layer without requiring a dedicated SQL warehouse for every dataset.

## Operational safety

- retries are bounded
- API rate limits are respected
- watermarks advance only after success
- raw data remains replayable
- secrets remain outside source control
- deployment paths are automated and reproducible

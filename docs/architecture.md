# Architecture Notes

This repository is a public-safe reimplementation of a professional homecare analytics architecture.

## Layers

- **Bronze:** immutable, batch-partitioned source snapshots in Parquet.
- **Silver:** normalized, typed and deduplicated entities.
- **Gold:** dimensions, facts, cross-reference tables and reporting marts.
- **Serving:** Synapse Serverless SQL views over Gold Parquet.
- **BI:** Power BI semantic models and dashboards.

## Incremental loading

Each endpoint has a persisted watermark. The next run subtracts a configurable overlap window before querying changes. This protects against late updates and boundary races. The Silver layer then deduplicates on endpoint-specific business keys.

## History

Client-style attributes use an SCD2 pattern when business reporting requires “as-of” history. Visit data can retain both latest state and version history.

## Operational design

The production-style architecture also separates:
- source acquisition from curation,
- source schema from analytical schema,
- infrastructure from application deployment,
- secrets from code,
- raw lineage from BI-facing views.

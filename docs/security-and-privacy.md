# Security and Privacy

This public repository intentionally does **not** contain production client or employee records, source API credentials, tenant/subscription identifiers, real Azure resource names, production endpoints, internal emails, private dashboards, or the original client-owned source repository.

The configuration and code use generic names and synthetic examples. Secrets are expected to come from environment variables or a secret manager such as Azure Key Vault.

For a real healthcare or homecare workload:
- use least-privilege RBAC,
- disable public blob access,
- keep secrets out of source control,
- protect logs from accidental PII,
- apply data-retention requirements,
- separate dev/test/prod resources,
- document lawful access and auditing requirements.

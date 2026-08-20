# Security & Privacy

Homecare and healthcare-service data can contain highly sensitive personal information. This public repository therefore contains **no production data and no client-identifying information**.

## Public-repository rules

- Do not commit secrets or connection strings.
- Do not publish source-system company identifiers.
- Do not publish real client, employee, visit, health, address, phone, or email data.
- Do not include production Azure resource names or subscription identifiers.
- Use synthetic examples for schemas and configuration.
- Keep real credentials in managed secret stores such as Azure Key Vault or GitHub encrypted secrets.

## Production pattern

A production implementation should combine least-privilege identities, managed secrets, encryption at rest and in transit, logging controls, auditability, and data-retention rules appropriate to the organization and jurisdiction.

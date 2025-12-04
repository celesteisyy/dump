

## Structure
```
Data Security
└── SIEM Framework
    ├── 1) Security Data Collection
    │    ├── Log Sources
    │    │    ├── Network: Firewall, IPS/IDS, DNS, VPN
    │    │    ├── Cloud: CloudTrail, VPC Flow Logs, Config, GuardDuty
    │    │    ├── Endpoints: EDR, OS logs, Sysmon
    │    │    ├── Applications: API gateway, Web Server, DB audit
    │    │    ├── Identity: IAM logs, SSO login, Directory events
    │    ├── Data Pipeline
    │    │    ├── Agent vs Agentless (Syslog, FluentBit…)
    │    │    ├── Streaming ingestion (Kafka/Kinesis)
    │    │    ├── Schema normalization (ECS, OCSF)
    │    │    └── Reliable delivery & retry
    │    ├── Security Requirements
    │    │    ├── Tamper-proof logs (immutability w/ object lock)
    │    │    ├── Minimum retention compliance (90/180/365 days)
    │    │    └── Zero data loss (buffering + ACK)
    │
    ├── 2) Security Data Protection
    │    ├── Access Control
    │    │    ├── RBAC + ABAC
    │    │    ├── Least privilege for analysts
    │    ├── Encryption
    │    │    ├── In transit (TLS 1.2+)
    │    │    ├── At rest (SSE-KMS or BYOK/CMK)
    │    ├── Data Quality & Governance
    │    │    ├── Data catalog (log type, owner, schema version)
    │    │    ├── Masking / Tokenization for PII
    │    │    ├── Hashing Trick for high-cardinality identifiers
    │    ├── Compliance & Auditability
    │         ├── Immutable logs + versioning
    │         ├── Encryption key lifecycle control
    │         └── Retention policy enforcement
    │
    ├── 3) Security Data Analytics
    │    ├── Alerting
    │    │    ├── Detection rules (MITRE ATT&CK mapping)
    │    │    ├── Statistical alerts (baseline anomalies)
    │    │    ├── ML-driven scoring (pipeline)
    │    ├── Context & Enrichment
    │    │    ├── IP → ASN/Geo/ORG enrichment
    │    │    ├── Asset & identity context (CMDB/IDP)
    │    │    └── Threat intel feeds (IOC ingest)
    │    ├── Correlation
    │    │    ├── Multi-log source joins (User, Host, IP)
    │    │    └── Timeline reconstruction
    │    ├── Investigation UX
    │         ├── Query interfaces (SIEM Search / SQL)
    │         ├── Case Management (SOAR integration)
    │         └── Visualization dashboards
    │
    ├── 4) Automation & Response
    │    ├── SOAR playbooks
    │    ├── Ticketing / Notification integration
    │    ├── Containment workflow (block IP, disable account)
    │
    └── 5) Observability & Metrics
         ├── Detection coverage map
         ├── MTTA / MTTR
         ├── False positive rate
         └── Pipeline health & SLA
```

### Breakdown
---
```
## 1️⃣ Security Data Collection
- CloudTrail (API events)
- VPC Flow Logs / DNS Logs / WAF / ELB Access logs
- GuardDuty / Inspector / Macie Findings
- OS / Syslog / EDR
- Third-party network security logs (Firewall / IDS / Proxy)
- Collection pattern
  - Multi-account ingest (Organizations)
  - Agentless / Syslog / Kinesis / Firehose
  - Schema normalization (OCSF)

## 2️⃣ Data Lake & Normalization
- Amazon Security Lake
  - Centralized S3 Data Lake
  - Data partition by source/region/time
  - Auto conversion → OCSF schema
- Glue Data Catalog metadata

## 3️⃣ Security Analytics (SIEM Functions)
### A) Real-time / Rule-based Detection
- Amazon OpenSearch Security Analytics
  - Sigma rules + MITRE ATT&CK mapping
  - Dashboards: login anomaly / API abuse / network threats
### B) Historical Analytics
- Athena
  - Ad-hoc investigation / long-term reports
  - Trend analysis / Compliance reporting

## 4️⃣ Findings Aggregation
- AWS Security Hub
  - Findings normalization & deduplication
  - Severity & compliance scoring
  - Multi-source feed (GuardDuty + OpenSearch + 3rd-party)

## 5️⃣ Automation & Response
- EventBridge → Lambda / SSM / SOAR
  - Auto disable IAM account
  - Block malicious IP / WAF update
  - Notification / Ticket creation

## 6️⃣ External SIEM Integration (Optional)
- Splunk / QRadar / Sumo Logic
  - Security Lake Subscriber Model
  - Pull OCSF logs from S3
  - Write enriched findings back to Security Hub

```

## 一句话：
> 构建并完善公司 **SIEM 体系**，实现核心安全日志集中与统一治理，上线基础检测与响应能力。


## Metrics
| 方向      | 简易指标         |
| ------- | -------------------- |
| 集中 & 治理 | ≥5核心日志源接入并统一管理       |
| 检测能力    | ≥5条真实有效的安全检测规则       |
| 响应能力    | ≥1个高优先级告警响应流程跑通      |
| 体系建设    | 顶层架构 + 数据目录 + 权限模型落地 |

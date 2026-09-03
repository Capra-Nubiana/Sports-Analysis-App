# Sports Analysis App — Privacy Policy & GDPR Compliance

## Data Controller
- **Controller:** Philip Kwimba (ikambili34@gmail.com)
- **Address:** Nairobi, Kenya
- **Purpose:** Sports video analysis, event detection, and highlight generation

## Data Categories Collected

| Category | Examples | Legal Basis | Retention |
|----------|---------|-------------|-----------|
| Video footage | Uploaded match recordings | Contract (Art. 6.1b) | 90 days |
| Detection results | Player positions, ball tracks | Legitimate interest (Art. 6.1f) | 30 days |
| Account data | Email, subscription tier | Contract (Art. 6.1b) | Until account deletion |
| Payment data | Stripe/M-Pesa transaction IDs | Legal obligation (Art. 6.1c) | 7 years |
| Analytics | Heatmaps, event timelines | Legitimate interest | 90 days |

## GDPR User Rights

### Right to Access (Art. 15)
Email `gdpr@sports-analysis.app` with your customer ID to receive:
- All stored personal data
- Processing purposes and legal basis
- Data retention schedule

### Right to Rectification (Art. 16)
Update your email or profile via the dashboard `/settings` page.

### Right to Erasure (Art. 17)
Request deletion by emailing `gdpr@sports-analysis.app`:
- All personal data deleted within 24 hours
- Match videos and detection results purged per RETENTION_DAYS
- Aggregated/anonymized analytics may be retained

### Right to Data Portability (Art. 20)
Download your data as JSON via dashboard `/export` endpoint, or request via email.

### Right to Restrict Processing (Art. 18)
Contact support to pause processing while a dispute is resolved.

### Right to Object (Art. 21)
Object to processing of detection results for analytics — email `gdpr@sports-analysis.app`.

## Data Storage & Security

### Local HDD Storage
- Videos stored at `STORAGE_PATH` (default: `/mnt/data/videos`)
- Processed outputs at `/mnt/data/processed`
- **Encryption:** Files encrypted at rest via filesystem-level encryption
- **Access:** Only backend service can read; frontend receives only WebSocket JSON streams
- **Backups:** Daily encrypted snapshots, retained for 7 days

### Database (Supabase PostgreSQL)
- Connection encrypted via TLS
- No raw video in database — only metadata and references
- Row-level security enabled for customer data isolation
- `refresh_tokens` hashed, never stored in plaintext

### Model Weights
- ONNX models hosted server-side only — never exposed to clients
- Models stored in `models/` directory, loaded into memory at startup
- Access restricted to authenticated, paid-tier customers

## Data Retention Schedule

| Data Type | Default Retention | Configurable |
|-----------|-------------------|--------------|
| Uploaded videos | 90 days | RETENTION_DAYS env var |
| Detection results | 30 days | Hard-coded |
| Account data | Until deletion | N/A |
| Payment records | 7 years | Legal requirement |
| Audit logs | 365 days | Hard-coded |

## California Privacy Rights (CCPA)
- Right to know what personal information is collected
- Right to delete personal information
- Right to opt-out of sale (no data sold — opt-out not applicable)
- Contact: `privacy@sports-analysis.app`

## Contact
- **DPO:** Philip Kwimba — `dpo@sports-analysis.app`
- **GDPR requests:** `gdpr@sports-analysis.app`
- **Mailing:** Nairobi, Kenya
- **Policy version:** 2026-09-02

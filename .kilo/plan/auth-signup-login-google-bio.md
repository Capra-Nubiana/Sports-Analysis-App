# Auth + Payments Implementation Plan

Based on kioskpay-backend patterns (Kotlin/Ktor → Python/FastAPI adaptation).

## Current State
- 6 tables in Supabase: customers, refresh_tokens, matches, events, transactions, match_tracks
- No auth routes exist. `rate_limiter.py` uses mock `X-Customer-ID` header.
- Payment services exist but are **mock implementations** (Phase 5 in-progress).
- Dependencies: FastAPI, SQLAlchemy async, Pydantic. **Missing**: JWT, bcrypt, google-auth, stripe.

## 1. New Dependencies

```txt
python-jose[cryptography]    # JWT token generation/verification
passlib[bcrypt]              # Password hashing
google-auth                  # Verify Google ID tokens
python-multipart             # OAuth callback form parsing
stripe                       # Stripe API (replace mock)
requests                     # HTTP for M-Pesa Daraja API
```

## 2. Schema Changes (New Migration)

Add columns to `customers`:
```sql
ALTER TABLE customers
  ADD COLUMN password_hash TEXT,
  ADD COLUMN google_id TEXT UNIQUE,
  ADD COLUMN full_name TEXT,
  ADD COLUMN phone_number TEXT,
  ADD COLUMN phone_hash TEXT UNIQUE,
  ADD COLUMN biometric_public_key TEXT,
  ADD COLUMN email_verified BOOLEAN DEFAULT FALSE,
  ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE;
```
Add `device_name` column to `refresh_tokens`.

## 3. Module Structure

```
src/core/auth/
├── __init__.py
├── jwt.py               # JWTService (access:15m, refresh:7d, SHA-256 hash)
├── password.py          # PasswordService (bcrypt, validation rules)
├── google.py            # GoogleAuthService (ID token verification)
├── biometric.py         # ChallengeStore (ECDSA-SHA256 challenge-response)
├── models.py            # Pydantic: RegisterRequest, LoginRequest, etc.
├── service.py           # AuthService (register, login, refresh, logout)
└── schemas.py           # Response models

src/api/routes/
├── auth.py              # /api/v1/auth/* endpoints
├── payments.py          # /api/v1/payments/* endpoints
```

## 4. Auth Routes (adapted from kioskpay AuthRoutes.kt)

### Public (rate-limited)
| Method | Endpoint | Body | Purpose |
|--------|----------|------|---------|
| POST | `/api/v1/auth/register` | email, password, full_name, phone, tier | Register new user |
| POST | `/api/v1/auth/login` | email, password | Login with password |
| POST | `/api/v1/auth/google` | id_token, role? | Google sign-in/up |
| POST | `/api/v1/auth/refresh` | refresh_token | Issue new access token |
| POST | `/api/v1/auth/forgot-password` | email | Send OTP (always 200) |
| POST | `/api/v1/auth/reset-password` | email, otp, new_password | Reset password |

### Authenticated (JWT required)
| Method | Endpoint | Body | Purpose |
|--------|----------|------|---------|
| POST | `/api/v1/auth/logout` | — | Revoke refresh token |
| GET | `/api/v1/auth/profile` | — | Get user profile |
| PUT | `/api/v1/auth/profile` | full_name, phone | Update profile |
| PUT | `/api/v1/auth/password` | current, new_password | Change password |
| DELETE | `/api/v1/auth/account` | password or confirm | Delete account |
| GET | `/api/v1/auth/biometric/challenge` | — (query: userId) | Generate challenge |
| POST | `/api/v1/auth/biometric/register` | public_key | Register biometric key |
| POST | `/api/v1/auth/biometric/login` | user_id, challenge, signature | Biometric login |
| POST | `/api/v1/auth/fcm-token` | token | Update device token |

## 5. AuthService Patterns (from kioskpay AuthService.kt)

### Token Issuance
```python
def issue_tokens(user):
    user = maybe_promote_to_admin(user)  # Check ADMIN_EMAILS
    access, refresh = jwt.generate_token_pair(user.customer_id, user.role)
    dao.save_refresh_token(user.customer_id, jwt.hash_token(refresh), jwt.refresh_expiry())
    return AuthTokens(access, refresh, ...)
```

### Register
1. Validate email format
2. Validate password (min 8, 1 uppercase, 1 digit)
3. Hash password with bcrypt
4. Check email uniqueness
5. Create customer record + save refresh token
6. Auto-promote to admin if email in `ADMIN_EMAILS`

### Login
1. Look up by email
2. Verify password with bcrypt
3. Check account not soft-deleted
4. Issue token pair

### Google Sign-In
1. Verify `id_token` with Google's public keys (`google-auth` library)
2. Extract: `google_uid`, `email`, `name`, `picture`
3. If Google UID exists → login existing user
4. If email matches existing account → link Google ID
5. Otherwise → create new customer with role (default 'user')

### Refresh
1. Decode refresh token (verify type='refresh', issuer, expiry)
2. Look up hashed refresh token in DB (SHA-256)
3. If not found or mismatched → reject
4. Check `replaced_by` chain for revocation
5. Issue new token pair

### Logout
1. Hash incoming refresh token, find in DB
2. Set `replaced_by` to signal revocation
3. Delete or mark as revoked

### Admin Auto-Promotion
- On **every** token issuance, check if user's email is in `ADMIN_EMAILS`
- If match and role is still 'user' → upgrade to 'admin'
- Mirrors kioskpay's `maybePromoteToAdmin()` pattern

### Biometric (adapted from BiometricChallengeStore)
- `GET /biometric/challenge` — generate random challenge, store with userId, return it
- `POST /biometric/register` — store ECDSA public key on user record
- `POST /biometric/login` — verify challenge signature with user's public key, issue tokens

Uses ECDSA-SHA256 (Python `cryptography` library):
```python
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import hashes, serialization

# Sign challenge
signature = ec.ECDSA(hashes.SHA256())
# Verify on server
public_key.verify(signature, challenge, ec.ECDSA(hashes.SHA256()))
```

## 6. Payments (replace mocks)

### StripeService → real implementation
```python
import stripe
stripe.Customer.create(email=..., ...)
stripe.checkout.Session.create(
    customer_email=...,
    line_items=[...],
    mode="payment" or "subscription",
    success_url=...,
    cancel_url=...,
)
```

### MPesaService → Daraja API STK Push
```python
# 1. Generate access token (base64 encode consumer_key:consumer_secret)
# 2. STK Push request
requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", ...)
# 3. Handle callback at /api/v1/payments/mpesa/callback
```

### Payment Routes
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/payments/stripe/checkout` | Create checkout session |
| POST | `/api/v1/payments/stripe/webhook` | Handle Stripe webhooks |
| POST | `/api/v1/payments/mpesa/stk-push` | Initiate M-Pesa STK Push |
| POST | `/api/v1/payments/mpesa/callback` | Handle M-Pesa callback |
| GET | `/api/v1/payments/matches` | List user's paid matches |

## 7. Rate Limiting (reuse existing)

Apply `src/api/dependencies/rate_limiter.py` to auth routes:
- **strict**: register, login, google, forgot-password (e.g., 5/min)
- **moderate**: refresh, logout, logout, biometric login (e.g., 20/min)

## 8. Admin Auto-Promotion (from kioskpay)

```python
def maybe_promote_to_admin(user):
    if user['role'] == 'admin' or not config.admin_emails:
        return user
    if user['email'].lower() in config.admin_emails:
        dao.update_role(user['id'], 'admin')
    return user
```

## 9. Environment Variables

```bash
# Existing
JWT_SECRET=<32+ char secret>
ADMIN_EMAILS=ikambili34@gmail.com,ikambili34@live.com

# New
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
GOOGLE_CLIENT_ID=<google-oauth-client-id>
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=
MPESA_PASSKEY=
```

## 10. Test Plan

| Test | Description |
|------|-------------|
| `test_register` | Email/password signup, password validation, duplicate email |
| `test_login` | Valid login, invalid password, non-existent user |
| `test_google_new_user` | New Google user created with role 'user' |
| `test_google_linking` | Google ID linked to existing email account |
| `test_refresh` | Valid refresh, revoked token rejected |
| `test_logout` | Refresh token revoked, cannot reuse |
| `test_admin_promotion` | Email in ADMIN_EMAILS auto-promoted |
| `test_biometric_challenge` | Challenge generated and validated |
| `test_biometric_login` | Valid signature, invalid signature, no key registered |
| `test_password_change` | Current password verified, validation applied |
| `test_account_deletion` | Soft delete, token revoked |
| `test_forgot_reset` | OTP flow, account not leaked |
| `test_payment_checkout` | Stripe checkout session created |
| `test_mpesa_stk_push` | STK Push request sent and callback handled |

## 11. Migration Order

1. Create new schema migration (`supabase/migrations/20240910_auth_payments.sql`)
2. Run `supabase db push` to apply schema changes
3. Implement auth module (`src/core/auth/`)
4. Implement payment routes (`src/api/routes/payments.py`)
5. Replace mock services (`src/core/payments/stripe_service.py`, `mpesa_service.py`)
6. Wire routes in `src/api/main.py`
7. Write tests
8. Update README with auth flow docs

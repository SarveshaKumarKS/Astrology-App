# Tamil / Vedic Astrology App — PRD & Status

## Product
Full-stack Tamil astrology app. Expo (React Native) frontend + FastAPI backend + MongoDB.
Generates horoscopes (Vakkiam & Thirukkanitham systems), Karu Udayam derived raasi charts,
marriage compatibility, daily panchangam, and PDF exports. Tamil + English support.

## Workflow
Reactive "pull, build, fix, verify" cycle. Agent pulls latest from the user's GitHub
repo (github.com/kishanguptab/Astrology-App), fixes breakages, verifies services for customer demos.

## Recurring Issue (fix after EVERY git pull)
- `frontend/app.json` on the remote contains `"expo-image"` and `"expo-sharing"` in the
  `plugins` array. These have no config plugins → Expo crashes on start.
  FIX: remove them from the `plugins` array (they can stay in dependencies). Restart expo.

## Current State (this session)
- Pulled from branch `Enhancements_PDF` (commit 1219642). Fixed app.json plugin crash.
- Reinstalled deps, restarted services. Verified:
  - Backend health HTTP 200; POST /api/horoscope 200 (incl. Karu Udayam derived chart).
  - Frontend renders home screen with all services + icons.
- Ran general security audit (read-only). Verdict: CONDITIONAL PASS.

## Security Audit Findings (Enhancements_PDF)
- No hardcoded secrets. .env git-ignored, non-secret config only. PDF gen in-memory (no path
  traversal). Queries not injectable (Pydantic-validated).
- SEC-001 (P1): /api/profiles is fully unauthenticated → anyone can read/write all saved
  birth-detail PII. App has NO auth by design. Acceptable for a throwaway demo; add auth
  before real production use.
- SEC-002 (P2): CPU-heavy PDF/horoscope endpoints unthrottled (DoS risk).
- SEC-003 (P3): raw exception text returned to clients; CORS wildcard; Mongo no auth (local).

## APK / Demo delivery
- Standalone Android .apk can be produced via Emergent **Publish** button (top-right).
  Customer installs the APK directly — no Expo Go, no setup. Agent cannot build APK from pod.

## Key API Endpoints
- POST /api/horoscope, /api/generate-pdf, /api/generate-palan-pdf, /api/compatibility
- GET/POST /api/profiles, GET /api/profiles/{id}, GET /api/panchangam/{date}

## Pending / Future
- BAMINI-Tamil14.ttf font verification for PDF (pending user confirmation).
- Backend cleanup: check obsolete pdf_generator_v2/v3/kuyil.py after refactor.
- Optional: add auth if profiles will hold real customer PII in production.

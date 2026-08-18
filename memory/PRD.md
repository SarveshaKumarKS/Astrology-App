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
- BAMINI font: RESOLVED — verified current PDF uses bundled `TSCu_SaiIndira.ttf`
  (Unicode Tamil), renders crisply and consistently for all users, no Hindi/Devanagari.
- Backend cleanup: check obsolete pdf_generator_v2/v3/kuyil.py after refactor.

## Responsive Phone UI Update
- Reworked the horoscope form for 320–430pt phone widths: compact vertical system
  selectors, fixed 52pt location button, stable two-column coordinate fields, safe-area
  bottom action, and consistent saffron design tokens.
- Reworked horoscope results into mobile-native cards. The former wide planetary table
  is now a stacked, readable card list with no horizontal page overflow.
- South Indian Kattam charts now scale to the available phone width and remain read-only.
- Explicitly preloads Ionicons so header, form, and action icons render reliably.
- Correction Mode UI is mounted only on the horoscope results screen. Editable values are
  limited to the basic Rasi/result cards, planetary-position cards, and Palan/Dasa cards;
  Kattam charts are never editable.
- Self-verified at 390pt and 320pt: body scroll width equals viewport width, location icon
  remains fully contained, coordinate fields remain contained, and Kattam is 264pt wide
  within a 320pt viewport. TypeScript and ESLint pass.

## Auth / Login (added this session)
- Emergent-managed Google Auth. Backend module: `/app/backend/auth.py`
  (POST /api/auth/session, GET /api/auth/me, POST /api/auth/logout, get_current_user dep).
- MongoDB: `users` + `user_sessions` collections (7-day session_token, TTL index).
- All /api/profiles endpoints now require auth and are scoped to the owner's user_id.
- Added missing DELETE /api/profiles/{id} (owner-only) — fixes the broken delete button.
- Frontend: `lib/auth.tsx` (AuthProvider/useAuth), `lib/api.ts` attaches Bearer token,
  `_layout.tsx` wraps app, `profiles.tsx` shows Google login gate when signed out,
  `horoscope-result.tsx` has a Save (bookmark) button that requires login.
- Save Profile feature: NEW — previously the app could list/delete profiles but had no
  way to create one (POST /api/profiles was never called). Now wired via the Save button.
- Verified: backend auth CRUD + user isolation + 401s + logout (manual curl). Login gate UI
  verified via screenshot. Google sign-in click-through requires a real Google account
  (cannot be automated).

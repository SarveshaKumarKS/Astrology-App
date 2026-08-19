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

## Deployment / Expo Go Compatibility Fix
- Root cause of the preview QR error: the frontend had been moved to Expo SDK 55 while
  this workspace and its Expo Go runtime use SDK 54.
- Aligned Expo, React Native, Expo Router, and all native modules to SDK 54-compatible
  versions using Expo's installer. The served Android manifest now reports `54.0.0`.
- Removed the duplicate npm lockfile so deployment consistently uses Yarn.
- Fixed invalid short hex colors and normalized app/adaptive/favicon artwork to 512x512.
- Removed startup creation of the MongoDB session TTL index; expired sessions remain
  rejected by application logic. Removed the historical preview DB TTL index once without
  deleting session records.
- Deployment scan: PASS. Expo Doctor: 18/18. Independent regression: frontend 100%,
  backend 23/23, health 200, no broken scoped flow or API.

## User-Friendly Correction Mode Entry
- Removed the hidden triple-tap gesture from the Home screen version label.
- Horoscope Results now shows a visible “Found a wrong value?” correction control.
- Tapping Correct opens a cross-platform confirmation modal explaining editable values
  and that Kattam charts remain read-only.
- Active mode has explicit Review and Exit controls; all existing correction logging and
  submission behavior remains unchanged.

## Grouped Correction Logging
- Each correction submission now creates exactly one MongoDB `corrections` document.
- The document includes `birth_details` with name, place of birth, date of birth, and
  time of birth; `corrections` is a JSON list containing every changed field.
- App/device/note/email context is grouped under `metadata`.
- Correction persistence now returns HTTP 503 if MongoDB cannot save the document instead
  of incorrectly reporting success.
- Backend regression includes the grouped schema and passes 24/24 tests.

## Global Language + Shared Date/Time
- Added one app-level Tamil/English language provider. The Home selection now propagates
  through Horoscope, Horoscope Results, Compatibility, Panchangam, Account, and Saved Charts.
- The selected language is persisted with SecureStore on Android/iOS and retained across
  navigation in preview web.
- Correction Mode functionality remains intact and intentionally stays English-only.
- Replaced the Horoscope legacy date/time modal with the shared cross-platform picker.
- Compatibility and Panchangam now use the same shared date/time picker behavior.
- Restored `/api/panchangam/{date}` with real Swiss Ephemeris calculations for Chennai/IST,
  including Panchangam elements, solar/lunar rise-set times, Rahu/Yama/Gulika periods,
  and Abhijit Muhurta; no placeholder data is used.

## Unified Saffron Calendar + Clock
- Replaced OS-native Android and iOS date/time dialogs with one branded React Native picker,
  so customers no longer see a blue Android Material dialog or a blank iOS spinner.
- Date mode uses a true month calendar with previous/next navigation, selected/today states,
  maximum-date handling, and Tamil/English month/week labels.
- Time mode uses a saffron clock control with hour/minute steppers, AM/PM selection, and
  quick :00/:15/:30/:45 minute actions while still allowing one-minute precision.
- The same picker is reused in Horoscope, Compatibility, and Panchangam at 320–430pt widths.

## Remote Backend Import — Enhancements_PDF
- Fetched remote commit `4a26c8e5a83e34b2a46893fdd0b908c5ddd4a0d3` from
  `github.com/kishanguptab/Astrology-App`, branch `Enhancements_PDF`.
- Imported its backend-only Vakyakarana change in `astrology/vakkiam_system.py`;
  no frontend/UI files were modified.
- Vakkiam Lagna now uses the Vakyakarana treatise ayanamsa rather than Lahiri:
  `(Kali year - 3600) × (120/121) ÷ 60` degrees.
- Added formula and tropical-to-sidereal ascendant regression coverage. Independent
  backend verification passes 29/29 tests plus health and live Vakkiam horoscope APIs.

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

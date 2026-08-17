# Tamil Astrology — Demo Build

A clean, testable build of the app on the `demo-build` branch: an **Expo / React
Native** Android client (`frontend/`) talking to the **FastAPI** backend
(`backend/`) that runs our Vakya (Vakkiyam) horoscope engine.

Package: `com.astronkv.tamilastrology` · App name: **Tamil Astrology**

---

## 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # optional
pip install -r requirements.txt
# MongoDB is OPTIONAL — see backend/.env.example
python -m uvicorn server:app --host 0.0.0.0 --port 8001
```

- `--host 0.0.0.0` so a phone on the same Wi-Fi can reach it.
- Health check: `GET http://<your-ip>:8001/api/health` → `{"status":"healthy"}`.
- MongoDB is not required: without it, horoscope / PDF / compatibility work
  normally; only history and saved profiles are skipped (logged as warnings).

## 2. Frontend config (point the app at the backend)

```bash
cd frontend
cp .env.example .env
# Edit .env — set EXPO_PUBLIC_BACKEND_URL to a URL the DEVICE can reach:
#   LAN IP:  http://192.168.1.50:8001   (NOT localhost — that's the phone itself)
#   ngrok:   https://<id>.ngrok-free.app
#   deploy:  https://api.yourhost.com
npm install
```

## 3. Run in development (fastest way to test)

```bash
cd frontend
npx expo start
```
Open in **Expo Go** on an Android device (same Wi-Fi as the backend), or press
`a` for an emulator.

## 4. Build the installable Android APK

The APK is built with EAS (`eas.json` → `preview` profile → APK). This needs an
Expo account login (interactive) and runs on Expo's cloud builders:

```bash
cd frontend
npm install -g eas-cli          # or: npx eas-cli@latest
eas login
eas build --platform android --profile preview
```
EAS returns a download link for the `.apk`. Install it on the device and test.

> The `EXPO_PUBLIC_BACKEND_URL` value is baked in at build time — set `.env`
> before building, or pass it: `EXPO_PUBLIC_BACKEND_URL=https://... eas build ...`.

### Local APK (alternative, needs Android SDK)

```bash
cd frontend
npx expo prebuild --platform android
cd android && ./gradlew assembleRelease
# APK at: android/app/build/outputs/apk/release/app-release.apk
```

---

## What was verified on this branch

- Backend imports cleanly and serves: `/api/health`, `/api/horoscope`,
  `/api/generate-pdf` (200, valid PDF), `/api/profiles` (works without Mongo).
- Horoscope via the API returns the corrected **Sukran (Venus) = Purva
  Bhadrapada (Poorattathi) p3** for the Coimbatore 13/04/2019 20:00 case.
- Frontend **TypeScript typechecks clean** (`npx tsc --noEmit`).
- Frontend **bundles for Android** (`npx expo export --platform android`, Hermes
  bundle produced with no errors).

## Known limitations (demo)

- **Daily Panchangam** (tithi/yoga/karana/muhurta) is not implemented in the
  backend; the `/api/panchangam/{date}` endpoint returns HTTP 501 and the
  Panchangam screen degrades gracefully. All other screens are functional.
- Persistence (history, saved profiles) requires MongoDB; without it those are
  best-effort no-ops.

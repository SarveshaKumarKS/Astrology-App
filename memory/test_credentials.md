# Test Credentials

## Authentication
- **Type**: Emergent-managed Google Auth (Google OAuth social login).
- No app-managed passwords. Users sign in with a real Google account via the
  "Sign in with Google" button on the Saved Profiles screen (or when tapping
  Save on a horoscope).
- There are NO seedable email/password test accounts for this flow — Google
  OAuth requires a real Google login through the browser.

## Auth-protected endpoints (require Bearer session_token)
- POST /api/profiles (create — bound to logged-in user)
- GET  /api/profiles (lists only the logged-in user's profiles)
- GET  /api/profiles/{id} (owner-only)
- DELETE /api/profiles/{id} (owner-only)
- GET  /api/auth/me, POST /api/auth/session, POST /api/auth/logout

## Manual backend testing (bypass Google)
To test protected routes without Google, seed a session row directly:
- Insert into `users`: { user_id, email, name }
- Insert into `user_sessions`: { session_token, user_id, expires_at (+7d) }
- Then call endpoints with header `Authorization: Bearer <session_token>`.
(Remember to clean up seeded rows afterwards.)

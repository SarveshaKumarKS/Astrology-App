import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { Platform } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import * as SecureStore from 'expo-secure-store';
import { fetchJson, fetchApi, setAuthToken } from './api';

WebBrowser.maybeCompleteAuthSession();

const TOKEN_KEY = 'astro_session_token';
const AUTH_URL = 'https://auth.emergentagent.com/';

export interface AuthUser {
  user_id: string;
  email: string;
  name?: string;
  picture?: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  signingIn: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// ---- token storage helpers (SecureStore on mobile, localStorage on web) ----
async function storeToken(token: string) {
  if (Platform.OS === 'web') {
    try { window.localStorage.setItem(TOKEN_KEY, token); } catch {}
  } else {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
  }
}

async function readToken(): Promise<string | null> {
  if (Platform.OS === 'web') {
    try { return window.localStorage.getItem(TOKEN_KEY); } catch { return null; }
  }
  return await SecureStore.getItemAsync(TOKEN_KEY);
}

async function clearToken() {
  if (Platform.OS === 'web') {
    try { window.localStorage.removeItem(TOKEN_KEY); } catch {}
  } else {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  }
}

function extractSessionId(url: string | null | undefined): string | null {
  if (!url) return null;
  const m = url.match(/[?#&]session_id=([^&#]+)/);
  return m ? decodeURIComponent(m[1]) : null;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [signingIn, setSigningIn] = useState(false);
  const processedIds = useRef<Set<string>>(new Set());
  const capturedUrl = useRef<string | null>(null);

  const exchangeSessionId = useCallback(async (sessionId: string): Promise<boolean> => {
    if (processedIds.current.has(sessionId)) return false;
    processedIds.current.add(sessionId);
    try {
      const data = await fetchJson<{ session_token: string; user: AuthUser }>(
        '/api/auth/session',
        { method: 'POST', body: JSON.stringify({ session_id: sessionId }) }
      );
      setAuthToken(data.session_token);
      await storeToken(data.session_token);
      setUser(data.user);
      return true;
    } catch (e) {
      console.error('Session exchange failed:', e);
      return false;
    }
  }, []);

  // Restore an existing session on mount; also handle web redirect session_id.
  useEffect(() => {
    let cancelled = false;

    const boot = async () => {
      // Web: process session_id from URL first (before checking stored token).
      if (Platform.OS === 'web') {
        const sid = extractSessionId(window.location.hash) || extractSessionId(window.location.search);
        if (sid) {
          const ok = await exchangeSessionId(sid);
          if (ok) {
            // Strip only the session_id, preserve the rest, keep history state.
            try {
              const clean = window.location.href
                .replace(/([?#&])session_id=[^&#]*/,'$1')
                .replace(/[?#&]$/, '');
              window.history.replaceState(window.history.state, '', clean);
            } catch {}
          }
          if (!cancelled) setLoading(false);
          return;
        }
      } else {
        // Mobile cold start: check initial URL for a session_id.
        const initial = await Linking.getInitialURL();
        const sid = extractSessionId(initial);
        if (sid) {
          await exchangeSessionId(sid);
          if (!cancelled) setLoading(false);
          return;
        }
      }

      // No session_id in URL — restore stored token.
      const token = await readToken();
      if (token) {
        setAuthToken(token);
        try {
          const data = await fetchJson<{ user: AuthUser }>('/api/auth/me', { method: 'GET' });
          if (!cancelled) setUser(data.user);
        } catch {
          setAuthToken(null);
          await clearToken();
        }
      }
      if (!cancelled) setLoading(false);
    };

    boot();
    return () => { cancelled = true; };
  }, [exchangeSessionId]);

  const login = useCallback(async () => {
    setSigningIn(true);
    try {
      if (Platform.OS === 'web') {
        const redirectUrl = window.location.origin + '/';
        window.location.href = `${AUTH_URL}?redirect=${encodeURIComponent(redirectUrl)}`;
        return; // page navigates away
      }

      const redirectUrl = Linking.createURL('');
      const authUrl = `${AUTH_URL}?redirect=${encodeURIComponent(redirectUrl)}`;

      // Capture the deep link even if the auth session returns dismiss with no URL.
      capturedUrl.current = null;
      const sub = Linking.addEventListener('url', ({ url }) => { capturedUrl.current = url; });

      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);

      let cbUrl: string | null = null;
      if (result.type === 'success' && (result as any).url) {
        cbUrl = (result as any).url;
      }
      if (!cbUrl) cbUrl = capturedUrl.current;
      if (!cbUrl) cbUrl = await Linking.getInitialURL();

      sub.remove();

      const sid = extractSessionId(cbUrl);
      if (sid) {
        await exchangeSessionId(sid);
      }
    } finally {
      setSigningIn(false);
    }
  }, [exchangeSessionId]);

  const logout = useCallback(async () => {
    try { await fetchApi('/api/auth/logout', { method: 'POST' }); } catch {}
    setAuthToken(null);
    await clearToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, signingIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(message: string, status: number, detail?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export function isAbortError(err: unknown): boolean {
  return (
    !!err &&
    typeof err === 'object' &&
    // @ts-expect-error DOMException name in RN/web
    (err.name === 'AbortError' || err.code === 20)
  );
}

export function getBaseUrl(): string {
  // Expo supports EXPO_PUBLIC_* at build/runtime without extra babel plugins.
  const url = process.env.EXPO_PUBLIC_BACKEND_URL;
  return (url && url.trim().length > 0) ? url.trim().replace(/\/+$/, '') : 'http://localhost:8001';
}

type FetchApiOptions = RequestInit & {
  timeoutMs?: number;
  retryOnceOnNetworkError?: boolean;
};

async function fetchOnce(path: string, options: FetchApiOptions = {}): Promise<Response> {
  const { timeoutMs = 30000, ...init } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const baseUrl = getBaseUrl();
    const url = `${baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
    return await fetch(url, {
      ...init,
      signal: controller.signal,
      headers: {
        ...(init.headers || {}),
      },
    });
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function fetchApi(path: string, options: FetchApiOptions = {}): Promise<Response> {
  const { retryOnceOnNetworkError = true } = options;
  try {
    return await fetchOnce(path, options);
  } catch (err) {
    if (!retryOnceOnNetworkError) throw err;
    // Retry once for transient network errors/timeouts.
    return await fetchOnce(path, { ...options, retryOnceOnNetworkError: false });
  }
}

export async function fetchJson<T>(path: string, options: FetchApiOptions = {}): Promise<T> {
  const res = await fetchApi(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  let body: any = undefined;
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    try {
      body = await res.json();
    } catch {
      body = undefined;
    }
  } else {
    try {
      body = await res.text();
    } catch {
      body = undefined;
    }
  }

  if (!res.ok) {
    const detail = body?.detail || (typeof body === 'string' ? body : undefined);
    throw new ApiError(detail || `Request failed with ${res.status}`, res.status, detail);
  }

  return body as T;
}


export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export interface ApiErrorBody {
  error: {
    message: string;
    type: string;
  };
}

export class ApiError extends Error {
  type: string;
  status: number;

  constructor(message: string, type: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.type = type;
    this.status = status;
  }
}

interface ApiFetchOptions {
  method?: string;
  body?: unknown;
  auth?: boolean;
  headers?: Record<string, string>;
}

// Lazily imported to avoid a hard circular-import cycle at module init time.
// (lib/auth.ts imports apiFetch/ApiError from this file.)
import { getToken } from './auth';

/**
 * Thin fetch wrapper around the Handelny API.
 *
 * `path` should be the route *after* the `/api/v1` prefix, e.g. `/auth/login`.
 */
export async function apiFetch<T = unknown>(
  path: string,
  options: ApiFetchOptions = {}
): Promise<T> {
  const { method = 'GET', body, auth = true, headers = {} } = options;

  const finalHeaders: Record<string, string> = {
    Accept: 'application/json',
    ...headers,
  };

  let finalBody: BodyInit | undefined;

  if (body instanceof FormData) {
    finalBody = body;
  } else if (body !== undefined) {
    finalHeaders['Content-Type'] = 'application/json';
    finalBody = JSON.stringify(body);
  }

  if (auth) {
    const token = getToken();
    if (token) {
      finalHeaders.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    method,
    headers: finalHeaders,
    body: finalBody,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') ?? '';
  const isJson = contentType.includes('application/json');
  const data: unknown = isJson ? await response.json() : undefined;

  if (!response.ok) {
    const errorBody = data as ApiErrorBody | undefined;
    throw new ApiError(
      errorBody?.error?.message ?? 'Something went wrong. Please try again.',
      errorBody?.error?.type ?? 'unknown_error',
      response.status
    );
  }

  return data as T;
}

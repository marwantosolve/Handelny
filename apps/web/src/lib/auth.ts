'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch, ApiError } from './api';

const TOKEN_KEY = 'handelny_token';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(TOKEN_KEY);
}

export interface CurrentUser {
  user: {
    id: string;
    email: string;
    full_name: string;
  };
  organization: {
    id: string;
    name: string;
    slug: string;
  };
  role: string;
}

/**
 * Fetches the current user on mount via GET /auth/me.
 * Redirects to /login if there's no token, or if the request 401s.
 */
export function useCurrentUser() {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      const token = getToken();
      if (!token) {
        router.replace('/login');
        return;
      }

      try {
        const data = await apiFetch<CurrentUser>('/auth/me');
        if (isMounted) {
          setUser(data);
          setIsLoading(false);
        }
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          clearToken();
          router.replace('/login');
          return;
        }
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadUser();

    return () => {
      isMounted = false;
    };
  }, [router]);

  return { user, isLoading };
}

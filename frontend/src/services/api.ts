/**
 * SuchnaSetu AI — Authentication & API Service
 * Interacts with FastAPI /api/auth endpoints with session cookie management.
 */

import type { UserProfile, GuestStatus } from '../types/api';

const getBaseUrl = (): string => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined' && window.location?.origin && window.location.origin !== 'null') {
    return '';
  }
  return 'http://127.0.0.1:8000';
};

const BASE_URL = getBaseUrl();
const AUTH_BASE = `${BASE_URL}/api/auth`;

export async function loginAccount(params: {
  email: string;
  password: string;
  rememberMe?: boolean;
}): Promise<{ status: string; message: string; user?: UserProfile }> {
  const resp = await fetch(`${AUTH_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      email: params.email,
      password: params.password,
      remember_me: !!params.rememberMe,
    }),
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || data.message || 'Invalid email or password.');
  }
  return data;
}

export async function registerAccount(params: {
  name: string;
  email: string;
  password: string;
  confirmPassword?: string;
}): Promise<{
  status: string;
  message: string;
  email_delivered?: boolean;
  already_verified?: boolean;
}> {
  const resp = await fetch(`${AUTH_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      name: params.name,
      email: params.email,
      password: params.password,
      confirm_password: params.confirmPassword,
    }),
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || data.message || 'Registration failed.');
  }
  return data;
}

export async function verifyEmailAddress(params: {
  token?: string;
  email?: string;
  code?: string;
}): Promise<{ status: string; message: string }> {
  const resp = await fetch(`${AUTH_BASE}/verify-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      token: params.token || undefined,
      email: params.email || undefined,
      code: params.code || undefined,
    }),
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || data.message || 'Email verification failed.');
  }
  return data;
}

export async function resendEmailVerification(email: string): Promise<{
  status: string;
  message: string;
  email_delivered?: boolean;
  already_verified?: boolean;
}> {
  const resp = await fetch(`${AUTH_BASE}/resend-verification`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email }),
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || data.message || 'Failed to resend verification email.');
  }
  return data;
}

export async function fetchAuthMe(): Promise<UserProfile | null> {
  try {
    const resp = await fetch(`${AUTH_BASE}/me`, {
      method: 'GET',
      credentials: 'include',
    });
    // Expected 401 for anonymous guests: handle gracefully without throwing or error logging
    if (resp.status === 401 || !resp.ok) {
      return null;
    }
    return resp.json();
  } catch {
    // Network error in guest context: consume gracefully and preserve guest state
    return null;
  }
}

export async function logoutAccount(): Promise<void> {
  try {
    await fetch(`${AUTH_BASE}/logout`, {
      method: 'POST',
      credentials: 'include',
    });
  } catch (err) {
    console.warn('Logout network error:', err);
  }
}

export async function requestPasswordReset(params: {
  email: string;
  method?: 'link' | 'code';
}): Promise<{ status: string; message: string }> {
  const resp = await fetch(`${AUTH_BASE}/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      email: params.email,
      method: params.method || 'link',
    }),
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || data.message || 'Password reset request failed.');
  }
  return data;
}

export async function completePasswordReset(params: {
  newPassword: string;
  confirmPassword?: string;
  token?: string;
  email?: string;
  code?: string;
}): Promise<{ status: string; message: string }> {
  const resp = await fetch(`${AUTH_BASE}/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      new_password: params.newPassword,
      confirm_password: params.confirmPassword,
      token: params.token || undefined,
      email: params.email || undefined,
      code: params.code || undefined,
    }),
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || data.message || 'Password reset failed.');
  }
  return data;
}

export async function fetchGuestStatus(): Promise<GuestStatus> {
  const resp = await fetch(`${AUTH_BASE}/guest-status`, {
    method: 'GET',
    credentials: 'include',
  });
  if (!resp.ok) {
    throw new Error('Failed to fetch guest status');
  }
  return resp.json();
}

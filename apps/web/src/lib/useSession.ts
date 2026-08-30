'use client';
import { useEffect, useState } from 'react';
import { getRole, getToken, getUsername } from './api';

export interface Session {
  ready: boolean;
  loggedIn: boolean;
  role: string | null;
  username: string | null;
}

/**
 * Reads the auth session from localStorage on the client. `ready` guards against
 * server/client hydration mismatch -- render neutral until it flips true.
 */
export function useSession(): Session {
  const [session, setSession] = useState<Session>({
    ready: false,
    loggedIn: false,
    role: null,
    username: null,
  });

  useEffect(() => {
    const sync = () =>
      setSession({
        ready: true,
        loggedIn: !!getToken(),
        role: getRole(),
        username: getUsername(),
      });
    sync();
    window.addEventListener('storage', sync);
    return () => window.removeEventListener('storage', sync);
  }, []);

  return session;
}

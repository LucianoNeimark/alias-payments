"use client";

import { createClient } from "@/lib/supabase/client";
import { useEffect, useState } from "react";

/** Current Supabase access token for `Authorization: Bearer` to FastAPI. */
export function useAccessToken(): string | null {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const supabase = createClient();
    let cancelled = false;

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!cancelled) setToken(session?.access_token ?? null);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setToken(session?.access_token ?? null);
    });

    return () => {
      cancelled = true;
      subscription.unsubscribe();
    };
  }, []);

  return token;
}

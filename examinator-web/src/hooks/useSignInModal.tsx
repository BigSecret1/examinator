"use client";

import { createContext, useCallback, useContext, useState } from "react";
import type { ReactNode } from "react";

interface SignInModalContextValue {
  isOpen: boolean;
  redirectTo: string | null;
  open: (redirectTo?: string) => void;
  close: () => void;
}

const SignInModalContext = createContext<SignInModalContextValue | null>(null);

export function SignInModalProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [redirectTo, setRedirectTo] = useState<string | null>(null);

  const open = useCallback((to?: string) => {
    setRedirectTo(to ?? null);
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  return (
    <SignInModalContext.Provider value={{ isOpen, redirectTo, open, close }}>
      {children}
    </SignInModalContext.Provider>
  );
}

export function useSignInModal() {
  const ctx = useContext(SignInModalContext);
  if (!ctx) {
    throw new Error("useSignInModal must be used within SignInModalProvider");
  }
  return ctx;
}


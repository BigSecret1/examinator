"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "@/hooks/useAuth";
import { SignInModalProvider } from "@/hooks/useSignInModal";
import SignInModal from "@/components/SignInModal";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <SignInModalProvider>
          {children}
          <SignInModal />
        </SignInModalProvider>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

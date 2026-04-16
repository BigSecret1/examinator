"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import { useAuth } from "@/hooks/useAuth";

export default function UserAvatar() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!user) return null;

  const initials = (user.first_name?.[0] || "") + (user.last_name?.[0] || "");

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-full focus:outline-none focus:ring-2 focus:ring-secondary/50"
      >
        {user.avatar_url ? (
          <Image
            src={user.avatar_url}
            alt={user.first_name}
            width={36}
            height={36}
            className="w-9 h-9 rounded-full border-2 border-surface-lighter"
          />
        ) : (
          <div className="w-9 h-9 rounded-full bg-secondary flex items-center justify-center text-sm font-semibold text-white">
            {initials || "?"}
          </div>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-56 bg-surface border border-surface-light/30 rounded-xl shadow-xl py-2 z-50">
          <div className="px-4 py-3 border-b border-surface-light/30">
            <p className="text-sm font-medium text-text-primary truncate">
              {user.first_name} {user.last_name}
            </p>
            <p className="text-xs text-text-muted truncate">{user.email}</p>
          </div>
          <button
            onClick={() => {
              logout();
              setOpen(false);
            }}
            className="w-full text-left px-4 py-2.5 text-sm text-text-secondary hover:bg-surface-light/50 hover:text-error transition-colors"
          >
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}

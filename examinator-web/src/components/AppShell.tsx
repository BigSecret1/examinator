// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import UserAvatar from "@/components/UserAvatar";

const NAV = [
  { href: "/library", label: "Library" },
  { href: "/feedback", label: "Feedback" },
];

export function AppHeader() {
  const pathname = usePathname() || "/";

  return (
    <header className="sticky top-0 z-40 border-b border-surface-light/30 bg-primary/80 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
        <Link href="/" className="flex items-center gap-3 shrink-0">
          <div className="w-9 h-9 rounded-xl bg-secondary flex items-center justify-center shadow-lg shadow-secondary/25">
            <Image
              src="/examinator-icon.png"
              alt=""
              width={38}
              height={50}
              className="w-6 h-6 object-contain"
              priority
            />
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-bold tracking-tight">Examinator</span>
            <span className="hidden sm:inline px-1.5 py-0.5 text-[10px] font-semibold rounded-full bg-secondary/20 text-secondary border border-secondary/30 leading-none">
              Beta
            </span>
          </div>
        </Link>

        <nav className="flex-1 flex items-center justify-start gap-2">
          {NAV.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                  active
                    ? "bg-surface-light text-text-primary"
                    : "text-text-secondary hover:text-text-primary hover:bg-surface-light/60"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <UserAvatar />
      </div>
    </header>
  );
}

export function AppFooter() {
  return (
    <footer className="border-t border-surface-light/30 py-8 text-xs text-text-muted">
      <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <span>Examinator © {new Date().getFullYear()} · Apache 2.0</span>
        <span>Made for learners who want to remember.</span>
      </div>
    </footer>
  );
}


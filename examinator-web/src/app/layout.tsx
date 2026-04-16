// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

import type { Metadata } from "next";
import "@/styles/globals.css";
import Providers from "@/components/Providers";

export const metadata: Metadata = {
  title: "Examinator",
  description: "Train your brain everyday with questions from various subjects & topics.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

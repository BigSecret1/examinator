// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

import type { Metadata } from "next";

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
      <body>{children}</body>
    </html>
  );
}

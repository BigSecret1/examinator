import AuthGuard from "@/components/AuthGuard";

export default function PracticeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard>{children}</AuthGuard>;
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "32 Flavors: Show My Work Alpha",
  description: "Human-model cognition loop with orchestrator and compyler",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100 antialiased">{children}</body>
    </html>
  );
}

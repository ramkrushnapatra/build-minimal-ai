import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "build-minimal-ai",
  description: "Document Q&A powered by RAG",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}

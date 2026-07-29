import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/lib/query-provider";
import { AuthGuard } from "@/components/AuthGuard";

export const metadata: Metadata = {
  title: "Tailr — AI-Powered Resume Intelligence Platform",
  description: "Optimize your resume for every job description using Multi-Agent AI, RAG, and LLMs while enforcing mandatory AI safety and formatting guardrails.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-sky-500/30 selection:text-sky-200">
        <QueryProvider>
          <AuthGuard>{children}</AuthGuard>
        </QueryProvider>
      </body>
    </html>
  );
}

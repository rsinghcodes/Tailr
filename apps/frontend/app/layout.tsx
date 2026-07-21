import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/lib/query-provider";

export const metadata: Metadata = {
  title: "Tailr — AI-Powered Resume Intelligence Platform",
  description: "Optimize your resume for every job description using Multi-Agent AI, RAG, and LLMs while enforcing mandatory AI safety and LaTeX formatting.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-sky-500/30 selection:text-sky-200">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}

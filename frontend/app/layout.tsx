import type { Metadata } from "next";
import { Inter, Roboto_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-ui"
});

const mono = Roboto_Mono({
  subsets: ["latin"],
  variable: "--font-mono"
});

export const metadata: Metadata = {
  title: "DontCollapse",
  description: "Modern EOC resilience dashboard with scenario simulation and trace logs"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning className={`${inter.variable} ${mono.variable} bg-slate-950 text-slate-200`}>
        {children}
      </body>
    </html>
  );
}

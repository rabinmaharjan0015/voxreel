import Header from "@/components/Header";
import { Toaster } from "@/components/Toaster";
import { AuthProvider } from "@/lib/auth";
import { ToastProvider } from "@/lib/toast";
import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const sans = Inter({ subsets: ["latin"], variable: "--font-sans" });
const display = Space_Grotesk({ subsets: ["latin"], variable: "--font-display" });

export const metadata: Metadata = {
  title: "VoxReel — AI videos with a human voice",
  description: "Pick a video type, bring your own keys, get a finished video.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${display.variable}`}>
      <body className="relative min-h-screen overflow-x-hidden">
        <div aria-hidden className="pointer-events-none fixed inset-0 -z-10">
          <div className="absolute -top-40 -left-32 h-[28rem] w-[28rem] rounded-full bg-violet-600/25 blur-[120px] animate-float" />
          <div className="absolute top-1/3 -right-40 h-[26rem] w-[26rem] rounded-full bg-fuchsia-500/20 blur-[120px] animate-float [animation-delay:-4s]" />
        </div>
        <AuthProvider>
          <ToastProvider>
            <Header />
            <main className="mx-auto max-w-6xl px-5 pb-24">{children}</main>
            <Toaster />
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

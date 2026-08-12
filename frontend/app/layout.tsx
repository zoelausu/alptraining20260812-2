import type { Metadata } from "next";
import { MyRuntimeProvider } from "@/app/MyRuntimeProvider";
import { TooltipProvider } from "@/components/ui/tooltip";

import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Chat",
  description: "Traditional Chinese agent chat (AG-UI + Agno)",
};

export const dynamic = "force-dynamic";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant" className="h-dvh">
      <body className="h-dvh font-sans">
        <TooltipProvider>
          <MyRuntimeProvider>{children}</MyRuntimeProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}

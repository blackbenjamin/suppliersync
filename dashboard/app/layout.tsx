
import "./globals.css";
import { ReactNode } from "react";

export const metadata = { title: "SupplierSync Console", description: "Agentic orchestration dashboard" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-neutral-50">
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}

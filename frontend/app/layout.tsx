import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "OCR Document Platform",
  description: "Secure OCR document extraction platform",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}


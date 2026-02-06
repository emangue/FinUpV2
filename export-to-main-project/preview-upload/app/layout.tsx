import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Preview de Importação",
  description: "Revise e classifique transações antes de importar",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-50">{children}</body>
    </html>
  );
}

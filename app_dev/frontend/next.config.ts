import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  // Desabilita TODOS os indicadores de desenvolvimento
  devIndicators: false,
  // Garante que o build use app_dev/frontend como root (evita conflito com package-lock na raiz)
  outputFileTracingRoot: path.join(__dirname),
  // Standalone output para Docker (imagem ~80MB vs ~300MB)
  output: 'standalone',
};

export default nextConfig;

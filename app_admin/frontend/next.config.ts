import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
  // Standalone output para Docker (imagem ~80MB vs ~300MB)
  output: 'standalone',
};

export default nextConfig;

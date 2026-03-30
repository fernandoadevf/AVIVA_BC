/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  /**
   * Em dev, o cache em disco do Webpack (PackFileCacheStrategy) costuma gerar
   * ENOENT ao renomear *.pack.gz — especialmente com hot reload / múltiplas abas.
   * Desligar o cache no modo desenvolvimento evita isso (rebuild um pouco mais lento).
   * Em produção (`next build`) o cache continua ativo.
   */
  webpack: (config, { dev }) => {
    if (dev) {
      config.cache = false;
    }
    return config;
  },
};

export default nextConfig;

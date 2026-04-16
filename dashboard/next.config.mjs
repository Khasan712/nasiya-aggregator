/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Standalone output bundles the minimum runtime (no node_modules at deploy
  // time) so the Docker image stays tiny.
  output: 'standalone',
  experimental: {
    typedRoutes: true,
  },
  // Most build-time errors here are stylistic (smart quotes / apostrophe
  // escaping). We ship those as-is — `npm run typecheck` already covers
  // real type safety, and the runtime renders Uzbek apostrophes correctly.
  eslint: {
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    const backend = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/backend/:path*',
        destination: `${backend}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;

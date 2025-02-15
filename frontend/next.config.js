/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL + '/api/:path*',
      },
      {
        source: '/ws/:path*',
        destination: process.env.NEXT_PUBLIC_WS_URL + '/ws/:path*',
      },
    ]
  },
  images: {
    domains: ['localhost', 'firstcourt.dev'],
  },
  webpack: (config) => {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    return config;
  },
}

import type { Metadata, Viewport } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
})

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
})

export const metadata: Metadata = {
  title: "Alias - El CVU de los agentes de IA",
  description:
    "Infraestructura financiera para la economía agéntica. Dales a tus agentes una cuenta real con CVU propio, saldo en pesos y transferencias autónomas.",
  keywords: [
    "Alias",
    "AI agents",
    "fintech",
    "Argentina",
    "CVU",
    "MCP",
    "autonomous payments",
    "agentic economy",
  ],
  authors: [{ name: "Alias" }],
  openGraph: {
    title: "Alias - El CVU de los agentes de IA",
    description:
      "Infraestructura financiera para la economía agéntica. Dales a tus agentes una cuenta real.",
    url: "https://alias.ar",
    siteName: "Alias",
    locale: "es_AR",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Alias - El CVU de los agentes de IA",
    description:
      "Infraestructura financiera para la economía agéntica. Dales a tus agentes una cuenta real.",
  },
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
}

export const viewport: Viewport = {
  themeColor: "#080808",
  width: "device-width",
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} font-sans antialiased bg-[#050505] text-[#FAFAFA] overflow-x-hidden grain-overlay`}
      >
        {children}
        <Analytics />
      </body>
    </html>
  )
}

"use client"

import Link from "next/link"

export function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-border">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Logo and tagline */}
          <div className="flex flex-col items-center md:items-start gap-2">
            <Link href="/" className="flex items-center gap-2">
              <svg
                width="24"
                height="24"
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-foreground"
              >
                <rect
                  x="2"
                  y="2"
                  width="28"
                  height="28"
                  rx="6"
                  stroke="currentColor"
                  strokeWidth="2"
                />
                <path
                  d="M10 16H22M16 10V22"
                  stroke="url(#gradient-footer)"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
                <circle cx="10" cy="10" r="2" fill="#7C3AED" />
                <circle cx="22" cy="10" r="2" fill="#06B6D4" />
                <circle cx="10" cy="22" r="2" fill="#06B6D4" />
                <circle cx="22" cy="22" r="2" fill="#7C3AED" />
                <defs>
                  <linearGradient
                    id="gradient-footer"
                    x1="10"
                    y1="10"
                    x2="22"
                    y2="22"
                    gradientUnits="userSpaceOnUse"
                  >
                    <stop stopColor="#7C3AED" />
                    <stop offset="1" stopColor="#06B6D4" />
                  </linearGradient>
                </defs>
              </svg>
              <span className="text-lg font-bold text-foreground">Alias</span>
            </Link>
            <p className="text-sm text-muted-foreground">
              Infraestructura financiera para la economía agéntica.
            </p>
          </div>

        </div>

        <div className="mt-12 pt-8 border-t border-border text-center">
          <p className="text-sm text-muted-foreground">
            © 2026 Alias · Buenos Aires, Argentina
          </p>
        </div>
      </div>
    </footer>
  )
}

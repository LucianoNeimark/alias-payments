"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { Menu, X } from "lucide-react"
import { useState } from "react"

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="fixed top-0 left-0 right-0 z-50"
    >
      <nav className="mx-auto max-w-7xl px-6 py-4">
        <div className="glass rounded-2xl px-6 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary rounded-lg blur-md opacity-50" />
              <svg
                width="32"
                height="32"
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="relative text-foreground"
              >
                <rect x="2" y="2" width="28" height="28" rx="6" stroke="currentColor" strokeWidth="2" />
                <path d="M10 16H22M16 10V22" stroke="url(#gradient)" strokeWidth="2" strokeLinecap="round" />
                <circle cx="10" cy="10" r="2" fill="#7C3AED" />
                <circle cx="22" cy="10" r="2" fill="#06B6D4" />
                <circle cx="10" cy="22" r="2" fill="#06B6D4" />
                <circle cx="22" cy="22" r="2" fill="#7C3AED" />
                <defs>
                  <linearGradient id="gradient" x1="10" y1="10" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#7C3AED" />
                    <stop offset="1" stopColor="#06B6D4" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <span className="text-xl font-bold text-foreground">Alias</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link href="#docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Docs
            </Link>
            <Link href="#pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
            <Link href="#github" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              GitHub
            </Link>
          </div>

          <div className="hidden md:block">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="relative px-5 py-2.5 rounded-xl text-sm font-medium text-white overflow-hidden group"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-secondary rounded-xl" />
              <span className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-secondary rounded-xl opacity-0 group-hover:opacity-100 blur-xl transition-opacity" />
              <span className="relative">Acceso temprano</span>
            </motion.button>
          </div>

          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-foreground p-2"
            aria-label="Toggle menu"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden mt-2 glass rounded-2xl p-4"
          >
            <div className="flex flex-col gap-4">
              <Link href="#docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Docs
              </Link>
              <Link href="#pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Pricing
              </Link>
              <Link href="#github" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                GitHub
              </Link>
              <button className="w-full px-5 py-2.5 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-primary via-accent to-secondary">
                Acceso temprano
              </button>
            </div>
          </motion.div>
        )}
      </nav>
    </motion.header>
  )
}

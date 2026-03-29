"use client"

import { motion, AnimatePresence } from "framer-motion"
import { ArrowRight } from "lucide-react"
import { TerminalWindow } from "./terminal-window"
import { useState, useEffect } from "react"

const rotatingWords = ["pagar.", "transferir.", "invertir.", "operar.", "cobrar."]

function RotatingWord() {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % rotatingWords.length)
    }, 2000)
    return () => clearInterval(timer)
  }, [])

  return (
    <span className="inline-block relative">
      <AnimatePresence mode="wait">
        <motion.span
          key={rotatingWords[index]}
          initial={{ y: 40, opacity: 0, rotateX: -90 }}
          animate={{ y: 0, opacity: 1, rotateX: 0 }}
          exit={{ y: -40, opacity: 0, rotateX: 90 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="shimmer-text inline-block"
        >
          {rotatingWords[index]}
        </motion.span>
      </AnimatePresence>
    </span>
  )
}

const letterVariants = {
  hidden: { opacity: 0, y: 80, rotateX: -90 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    rotateX: 0,
    transition: {
      delay: i * 0.04,
      duration: 0.6,
      ease: [0.215, 0.61, 0.355, 1],
    },
  }),
}

function AnimatedHeadline({ text, startDelay = 0 }: { text: string; startDelay?: number }) {
  return (
    <span className="inline-block overflow-hidden">
      {text.split("").map((char, i) => (
        <motion.span
          key={i}
          custom={i + startDelay}
          variants={letterVariants}
          initial="hidden"
          animate="visible"
          className="inline-block"
          style={{ display: char === " " ? "inline" : "inline-block" }}
        >
          {char === " " ? "\u00A0" : char}
        </motion.span>
      ))}
    </span>
  )
}

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center pt-24 pb-16 px-6 overflow-hidden">
      {/* Massive glow orb */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] lg:w-[900px] lg:h-[900px]">
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-primary/30 via-accent/20 to-secondary/30 blur-[120px] pulse-glow" />
      </div>

      <div className="mx-auto max-w-7xl w-full relative">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, filter: "blur(10px)" }}
              animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full animated-border mb-8"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-secondary" />
              </span>
              <span className="text-sm text-muted-foreground font-medium tracking-wide">
                Fintech Infrastructure · Argentina
              </span>
            </motion.div>

            {/* Headline */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-[5.5rem] font-bold leading-[1.1] tracking-tight mb-6">
              <span className="block">
                <AnimatedHeadline text="El CVU de los" />
              </span>
              <span className="block mt-[0.1em]">
                <AnimatedHeadline text="agentes que" startDelay={14} />
              </span>
              <span className="block mt-[0.1em] whitespace-nowrap">
                <AnimatedHeadline text="saben " startDelay={25} />
                <span className="inline-block translate-y-[-0.18em]">
                  <RotatingWord />
                </span>
              </span>
            </h1>

            {/* Subheadline */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1 }}
              className="text-lg sm:text-xl text-muted-foreground max-w-xl mb-10 leading-relaxed"
            >
              Dales a tus agentes una cuenta real. Saldo en pesos, CVU propio,
              transferencias autónomas. Dentro de los límites que vos definís.
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.2 }}
              className="flex flex-col sm:flex-row gap-4 mb-10"
            >
              <motion.button
                whileHover={{ scale: 1.03, boxShadow: "0 0 40px rgba(124,58,237,0.4)" }}
                whileTap={{ scale: 0.97 }}
                className="group relative px-8 py-4 rounded-xl text-base font-semibold text-foreground overflow-hidden"
              >
                <span className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-secondary rounded-xl" />
                <span className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-secondary rounded-xl opacity-0 group-hover:opacity-100 blur-2xl transition-opacity duration-700" />
                <span className="relative flex items-center justify-center gap-2">
                  Conectar mi agente
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1.5 transition-transform duration-300" />
                </span>
              </motion.button>

            </motion.div>

            {/* Stats instead of checkmarks */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.5 }}
              className="flex gap-8"
            >
              {[
                { value: "MCP", label: "Nativo" },
                { value: "CVU", label: "Real en ARS" },
                { value: "FCI", label: "Yield automático" },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.5 + i * 0.15 }}
                  className="flex flex-col"
                >
                  <span className="text-2xl font-bold gradient-text">{stat.value}</span>
                  <span className="text-xs text-muted-foreground mt-0.5">{stat.label}</span>
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* Terminal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8, rotateY: -15 }}
            animate={{ opacity: 1, scale: 1, rotateY: 0 }}
            transition={{ duration: 1, delay: 0.5, ease: [0.215, 0.61, 0.355, 1] }}
            className="relative hidden lg:block"
          >
            <div className="relative float-animation" style={{ perspective: "1000px" }}>
              <div className="absolute -inset-8 bg-gradient-to-r from-primary/20 via-accent/10 to-secondary/20 rounded-3xl blur-3xl pulse-glow" />
              <TerminalWindow />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

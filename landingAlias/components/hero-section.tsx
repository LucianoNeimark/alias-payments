"use client"

import { motion, AnimatePresence } from "framer-motion"
import { TerminalWindow } from "./terminal-window"
import { useState, useEffect } from "react"

const rotatingWords = ["pagar.", "transferir.", "invertir.", "operar.", "cobrar."]

function RotatingWord() {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % rotatingWords.length)
    }, 2200)
    return () => clearInterval(timer)
  }, [])

  return (
    <span className="relative inline-block overflow-hidden" style={{ minWidth: "12ch" }}>
      <AnimatePresence mode="wait">
        <motion.span
          key={rotatingWords[index]}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
          className="text-[#6B4C2A] leading-[inherit]"
        >
          {rotatingWords[index]}
        </motion.span>
      </AnimatePresence>
    </span>
  )
}

const letterVariants = {
  hidden: { opacity: 0, y: 60 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.03,
      duration: 0.5,
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
    <section className="relative h-screen flex flex-col justify-center px-6 sm:px-10 overflow-hidden">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse 55% 60% at 30% 50%, rgba(245,240,232,0.92) 0%, rgba(245,240,232,0) 100%)",
        }}
      />
      <div className="mx-auto max-w-[1400px] w-full relative">
        <div className="flex flex-col lg:flex-row lg:items-center gap-12 lg:gap-20">
          <div className="lg:flex-[1.1] lg:min-w-0">
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-sm font-mono text-[#8B8177] tracking-wider uppercase mb-6"
            >
              Infraestructura financiera para agentes
            </motion.p>

            <h1 className="text-[2.75rem] sm:text-[3.5rem] lg:text-[4.25rem] xl:text-[5rem] font-extrabold leading-[1.05] tracking-[-0.03em] mb-6 text-[#1A1A1A]">
              <span className="block">
                <AnimatedHeadline text="Agentes que" />
              </span>
              <span className="block whitespace-nowrap">
                <AnimatedHeadline text="saben " startDelay={12} />
                <RotatingWord />
              </span>
            </h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1 }}
              className="text-base sm:text-[1.125rem] text-[#6B6560] max-w-md mb-10 leading-[1.7]"
            >
              Dales a tus agentes una cuenta real. Saldo en pesos, CVU propio,
              transferencias autónomas. Dentro de los límites que vos definís.
            </motion.p>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.4 }}
              className="flex items-center gap-0"
            >
              {[
                { value: "MCP", label: "Nativo" },
                { value: "CVU", label: "Real en ARS" },
                { value: "FCI", label: "Yield automático" },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.4 + i * 0.1 }}
                  className="flex flex-col pr-8 last:pr-0 border-r border-[#1A1A1A]/10 last:border-r-0 mr-8 last:mr-0"
                >
                  <span className="text-lg sm:text-xl font-bold text-[#1A1A1A] font-mono">{stat.value}</span>
                  <span className="text-[11px] text-[#8B8177] mt-1 uppercase tracking-[0.15em]">{stat.label}</span>
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* Right: Terminal */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.6, ease: [0.215, 0.61, 0.355, 1] }}
            className="relative hidden lg:block lg:flex-1 lg:min-w-0"
          >
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 1.8 }}
              className="flex items-center gap-2 mb-3 ml-1"
            >
              <span className="text-[13px] font-mono text-[#8B8177]">
                Sos un agente? Instalá el skill
              </span>
              <motion.span
                animate={{ y: [0, 4, 0] }}
                transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
                className="text-[#A89880] text-sm"
              >
                ↓
              </motion.span>
            </motion.div>
            <div className="relative float-animation">
              <TerminalWindow />
            </div>
          </motion.div>
        </div>
      </div>

      {/* Bottom line */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2, duration: 1 }}
        className="absolute bottom-0 left-0 right-0 z-10 border-t border-[#1A1A1A]/8 bg-[#F5F0E8]"
      >
        <div className="mx-auto max-w-[1400px] px-6 sm:px-10 py-4 flex items-center justify-between">
          <span className="text-[11px] text-[#8B8177] tracking-[0.2em] uppercase font-mono">
            Alias
          </span>
          <span className="text-[11px] text-[#8B8177] tracking-[0.2em] uppercase font-mono">
            Buenos Aires, Argentina
          </span>
        </div>
      </motion.div>
    </section>
  )
}

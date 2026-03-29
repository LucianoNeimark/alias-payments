"use client"

import { motion, useInView } from "framer-motion"
import { useRef, useState, useEffect } from "react"
import { TrendingUp, Sparkles } from "lucide-react"

function LiveYield() {
  const [yield_, setYield_] = useState(75.42)
  const [accumulatedPesos, setAccumulatedPesos] = useState(0)
  const baseBalance = 100000

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")
    if (mediaQuery.matches) return

    const timer = setInterval(() => {
      setYield_((prev) => {
        const change = (Math.random() - 0.5) * 0.02
        return Math.max(74, Math.min(77, prev + change))
      })
      
      setAccumulatedPesos((prev) => {
        const dailyYield = (0.75 / 365) * baseBalance
        const perSecond = dailyYield / 86400
        return prev + perSecond
      })
    }, 100)

    return () => clearInterval(timer)
  }, [])

  return (
    <div className="text-center">
      <div className="flex items-center justify-center gap-4 mb-6">
        <motion.div
          animate={{ rotate: [0, 10, -10, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
        >
          <TrendingUp className="w-8 h-8 text-emerald-400" />
        </motion.div>
        <span className="text-6xl sm:text-7xl lg:text-8xl font-bold text-emerald-400 tabular-nums tracking-tighter">
          {yield_.toFixed(2)}%
        </span>
        <span className="text-xl text-muted-foreground font-medium">TNA</span>
      </div>
      <div className="inline-block relative">
        <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded-2xl blur-lg" />
        <div className="relative glass rounded-2xl px-8 py-5">
          <p className="text-sm text-muted-foreground mb-1.5">Rendimiento acumulado (demo con $100K ARS)</p>
          <p className="text-3xl font-bold text-foreground tabular-nums">
            +${accumulatedPesos.toFixed(6)} <span className="text-lg text-muted-foreground">ARS</span>
          </p>
        </div>
      </div>
    </div>
  )
}

export function YieldSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section ref={ref} className="py-32 px-6 relative">
      <div className="mx-auto max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="relative"
        >
          {/* Intense glow */}
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/15 via-primary/10 to-secondary/15 rounded-[2rem] blur-[80px]" />

          <div className="relative rounded-[2rem] overflow-hidden">
            {/* Animated border */}
            <div className="absolute inset-0 animated-border rounded-[2rem]" />
            <div className="relative glass rounded-[2rem] p-10 sm:p-16 text-center m-[2px]">
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={isInView ? { opacity: 1, scale: 1 } : {}}
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-emerald-400 text-lg font-medium mb-8"
              >
                <Sparkles className="w-4 h-4" />
                Rendimiento automático
              </motion.div>

              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
                Tu saldo{" "}
                <span className="shimmer-text">no para quieto.</span>
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-12">
                Cada peso en Alias se invierte automáticamente en fondos money market
                con rendimiento cercano al 75% TNA. Disponible 24/7. Sin comisiones.
              </p>

              <LiveYield />

              <p className="text-sm text-muted-foreground mt-10 max-w-md mx-auto">
                Igual que los bancos grandes. Solo que el titular es tu agente.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

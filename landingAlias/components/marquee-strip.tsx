"use client"

import { motion } from "framer-motion"
import { Zap, Shield, Banknote, Bot, TrendingUp, Lock, Globe, Cpu } from "lucide-react"

const items = [
  { icon: Bot, text: "Agentes autónomos" },
  { icon: Banknote, text: "CVU real en pesos" },
  { icon: Zap, text: "MCP nativo" },
  { icon: TrendingUp, text: "FCI yield automático" },
  { icon: Shield, text: "Límites configurables" },
  { icon: Lock, text: "Aprobación humana" },
  { icon: Globe, text: "Transferencias a cualquier CVU" },
  { icon: Cpu, text: "API-first" },
]

function MarqueeRow({ reverse = false }: { reverse?: boolean }) {
  const doubled = [...items, ...items]

  return (
    <div className="flex overflow-hidden relative group">
      <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-[#050505] to-transparent z-10" />
      <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-[#050505] to-transparent z-10" />

      <div className={reverse ? "marquee-reverse flex gap-4" : "marquee flex gap-4"}>
        {doubled.map((item, i) => (
          <div
            key={i}
            className="flex items-center gap-3 px-5 py-3 rounded-full border border-white/[0.06] bg-white/[0.02] whitespace-nowrap hover:border-primary/40 hover:bg-primary/5 transition-all duration-300 shrink-0"
          >
            <item.icon className="w-4 h-4 text-secondary" />
            <span className="text-sm font-medium text-foreground/80">{item.text}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function MarqueeStrip() {
  return (
    <motion.section
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.8 }}
      className="py-12 space-y-4 relative"
    >
      <MarqueeRow />
      <MarqueeRow reverse />
    </motion.section>
  )
}

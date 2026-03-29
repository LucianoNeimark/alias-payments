"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { UserPlus, Zap, CheckCircle2 } from "lucide-react"

const steps = [
  {
    number: "01",
    icon: UserPlus,
    title: "Creá la cuenta del agente",
    description:
      "Definí límites de gasto y el agente recibe su propio CVU. Así de simple.",
    accent: "from-violet-500 to-purple-600",
    glow: "violet",
  },
  {
    number: "02",
    icon: Zap,
    title: "El agente opera con autonomía",
    description:
      "Vía MCP, consulta saldo, solicita pagos y ejecuta transferencias a cualquier CVU en Argentina.",
    accent: "from-cyan-500 to-blue-600",
    glow: "cyan",
  },
  {
    number: "03",
    icon: CheckCircle2,
    title: "Vos aprobás, no ejecutás",
    description:
      "Para pagos que superen el límite, recibís notificación y aprobás con un click.",
    accent: "from-emerald-500 to-green-600",
    glow: "emerald",
  },
]

export function HowItWorksSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section ref={ref} className="py-32 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/[0.03] to-transparent pointer-events-none" />

      <div className="mx-auto max-w-7xl relative">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <motion.span
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            className="inline-block px-4 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-primary text-lg font-medium mb-6"
          >
            Cómo funciona
          </motion.span>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
            Tres pasos.{" "}
            <span className="shimmer-text">Cero fricción.</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Darle autonomía financiera a tu agente es más fácil de lo que pensás.
          </p>
        </motion.div>

        <div className="relative">
          {/* Animated connecting line */}
          <motion.div
            initial={{ scaleX: 0 }}
            animate={isInView ? { scaleX: 1 } : {}}
            transition={{ duration: 1.5, delay: 0.5, ease: "easeOut" }}
            className="hidden md:block absolute top-28 left-[16%] right-[16%] h-px bg-gradient-to-r from-violet-500/50 via-cyan-500/50 to-emerald-500/50 origin-left"
          />

          <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
            {steps.map((step, i) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 60 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.3 + i * 0.2 }}
                className="relative group"
              >
                <div className="absolute -inset-px bg-gradient-to-b from-primary/20 to-secondary/10 rounded-3xl opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500" />

                <div className="relative glass rounded-3xl p-8 h-full transition-all duration-500 hover:border-primary/30 hover:translate-y-[-4px] hover:shadow-[0_20px_60px_-20px_rgba(124,58,237,0.3)]">
                  {/* Number */}
                  <div className="relative mb-8">
                    <div className={`absolute inset-0 bg-gradient-to-r ${step.accent} rounded-2xl blur-lg opacity-40 group-hover:opacity-70 transition-opacity duration-500`} />
                    <div className={`relative w-16 h-16 rounded-2xl bg-gradient-to-br ${step.accent} flex items-center justify-center`}>
                      <span className="text-2xl font-bold text-white">{step.number}</span>
                    </div>
                  </div>

                  {/* Icon */}
                  <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 group-hover:border-primary/30 transition-all duration-300">
                    <step.icon className="w-6 h-6 text-secondary" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold mb-3 text-foreground group-hover:text-primary transition-colors duration-300">
                    {step.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

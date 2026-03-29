"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { X, Check, Bot, ArrowRight, RefreshCw, Sparkles } from "lucide-react"

export function ProblemSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section ref={ref} className="py-32 px-6 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-red-500/[0.02] to-transparent pointer-events-none" />

      <div className="mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <motion.span
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.4 }}
            className="inline-block px-4 py-1.5 rounded-full border border-red-500/20 bg-red-500/5 text-red-400 text-lg font-medium mb-6"
          >
            El problema
          </motion.span>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 text-balance">
            Tu agente frena cuando tiene que{" "}
            <span className="relative inline-block">
              <span className="gradient-text">pagar</span>
              <motion.span
                initial={{ scaleX: 0 }}
                animate={isInView ? { scaleX: 1 } : {}}
                transition={{ duration: 0.8, delay: 0.5 }}
                className="absolute -bottom-2 left-0 right-0 h-[3px] bg-gradient-to-r from-primary to-secondary origin-left"
              />
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Los agentes de IA pueden investigar, analizar y ejecutar tareas complejas.
            Pero cuando necesitan mover dinero, vos volvés al loop.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 lg:gap-12 relative">
          {/* VS divider */}
          <div className="hidden md:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={isInView ? { scale: 1, rotate: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.8, type: "spring" }}
              className="w-16 h-16 rounded-full bg-[#050505] border-2 border-white/10 flex items-center justify-center"
            >
              <span className="text-sm font-bold text-muted-foreground">VS</span>
            </motion.div>
          </div>

          {/* BEFORE card */}
          <motion.div
            initial={{ opacity: 0, x: -60, rotateY: 10 }}
            animate={isInView ? { opacity: 1, x: 0, rotateY: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="relative group"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-orange-500/5 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative glass rounded-3xl p-8 border-red-500/20 hover:border-red-500/30 transition-all duration-500 h-full">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                  <X className="w-6 h-6 text-red-400" />
                </div>
                <div>
                  <span className="text-sm font-bold text-red-400 uppercase tracking-wider">Antes</span>
                  <p className="text-xs text-muted-foreground">Workflow manual</p>
                </div>
              </div>

              <h3 className="text-lg font-semibold mb-6 text-foreground/80 italic border-l-2 border-red-500/30 pl-4">
                &ldquo;Agente, organizá los pagos a freelancers de este mes.&rdquo;
              </h3>

              <div className="space-y-4">
                <StepItem
                  icon={<Bot className="w-4 h-4 text-muted-foreground" />}
                  text="El agente revisa entregas y calcula montos"
                  variant="muted"
                />
                <StepItem
                  icon={<Bot className="w-4 h-4 text-muted-foreground" />}
                  text="Te recomienda a quién pagar y cuánto"
                  variant="muted"
                />

                <div className="my-6 py-4 border-y border-red-500/20 relative">
                  <div className="absolute -left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-red-500/50 to-red-500/0" />
                  <div className="flex items-center gap-2 text-red-400 text-sm font-semibold mb-3">
                    <RefreshCw className="w-4 h-4 animate-spin" style={{ animationDuration: "3s" }} />
                    <span>Vos ejecutás cada transferencia</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="flex items-center gap-1.5 p-2.5 rounded-lg bg-red-500/5 border border-red-500/10">
                        <div className="w-5 h-5 rounded-full bg-red-500/20 flex items-center justify-center text-[10px] text-red-400 font-bold">{i}</div>
                        <ArrowRight className="w-3 h-3 text-red-400/40" />
                        <span className="text-[10px] text-red-400/60 font-mono">CVU</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground mt-3 italic">
                    ...y así con cada freelancer, uno por uno.
                  </p>
                </div>

                <p className="text-sm text-red-400/80 font-medium">
                  El humano sigue siendo el ejecutor de cada pago.
                </p>
              </div>
            </div>
          </motion.div>

          {/* AFTER card */}
          <motion.div
            initial={{ opacity: 0, x: 60, rotateY: -10 }}
            animate={isInView ? { opacity: 1, x: 0, rotateY: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="relative group"
          >
            <div className="absolute -inset-[1px] bg-gradient-to-br from-primary/30 to-secondary/30 rounded-3xl opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500" />
            <div className="relative glass rounded-3xl p-8 border-primary/20 hover:border-primary/40 transition-all duration-500 h-full">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 border border-primary/20 flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-secondary" />
                </div>
                <div>
                  <span className="text-sm font-bold text-primary uppercase tracking-wider">Con Alias</span>
                  <p className="text-xs text-muted-foreground">Workflow autónomo</p>
                </div>
              </div>

              <h3 className="text-lg font-semibold mb-6 text-foreground border-l-2 border-primary/30 pl-4">
                &ldquo;Agente, organizá los pagos a freelancers de este mes.&rdquo;
              </h3>

              <div className="space-y-4">
                <StepItem
                  icon={<Bot className="w-4 h-4 text-primary" />}
                  text="El agente detecta entregas y calcula montos"
                  variant="primary"
                />
                <StepItem
                  icon={<Bot className="w-4 h-4 text-primary" />}
                  text="Te pide UNA aprobación para el total"
                  variant="primary"
                />

                <div className="my-6 py-4 border-y border-primary/20 relative">
                  <div className="absolute -left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-primary/50 to-secondary/50" />
                  <div className="flex items-center gap-2 text-secondary text-sm font-semibold mb-3">
                    <Check className="w-4 h-4" />
                    <span>El agente ejecuta todo automáticamente</span>
                  </div>
                  <div className="flex items-center justify-center gap-3 p-4 rounded-xl bg-gradient-to-r from-primary/5 to-secondary/5 border border-primary/10">
                    <Bot className="w-5 h-5 text-primary" />
                    <div className="flex items-center gap-1">
                      <ArrowRight className="w-4 h-4 text-secondary" />
                      <ArrowRight className="w-4 h-4 text-secondary/60" />
                      <ArrowRight className="w-4 h-4 text-secondary/30" />
                    </div>
                    <div className="flex gap-1.5">
                      {[1, 2, 3].map((i) => (
                        <motion.div
                          key={i}
                          initial={{ scale: 0 }}
                          animate={isInView ? { scale: 1 } : {}}
                          transition={{ delay: 1 + i * 0.1, type: "spring" }}
                          className="w-7 h-7 rounded-full bg-secondary/20 flex items-center justify-center"
                        >
                          <Check className="w-3.5 h-3.5 text-secondary" />
                        </motion.div>
                      ))}
                    </div>
                    <span className="text-xs text-secondary font-bold ml-1">+7 más</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-3">
                    10 transferencias ejecutadas en segundos.
                  </p>
                </div>

                <p className="text-sm text-primary font-medium">
                  El humano pasa de ejecutor a aprobador.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

function StepItem({ icon, text, variant }: { icon: React.ReactNode; text: string; variant: "muted" | "primary" }) {
  return (
    <div className="flex items-center gap-4">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
        variant === "primary" ? "bg-primary/10" : "bg-muted"
      }`}>
        {icon}
      </div>
      <p className={`text-sm ${variant === "primary" ? "text-foreground/80" : "text-muted-foreground"}`}>
        {text}
      </p>
    </div>
  )
}

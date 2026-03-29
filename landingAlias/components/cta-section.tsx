"use client"

import { motion, useInView } from "framer-motion"
import { useRef, useState } from "react"
import { ArrowRight, Loader2, Check, Zap } from "lucide-react"

export function CTASection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })
  const [email, setEmail] = useState("")
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setStatus("loading")
    setTimeout(() => {
      setStatus("success")
      setEmail("")
    }, 1500)
  }

  return (
    <section ref={ref} className="py-32 px-6 relative overflow-hidden">
      {/* Background orbs */}
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[700px] bg-gradient-to-r from-primary/25 via-accent/15 to-secondary/25 rounded-full blur-[150px] pulse-glow" />
      </div>

      <div className="mx-auto max-w-4xl relative">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full animated-border text-lg font-medium mb-8"
          >
            <Zap className="w-4 h-4 text-secondary" />
            <span className="text-muted-foreground">Acceso anticipado</span>
          </motion.div>

          <h2 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold mb-6 text-balance leading-[1.1]">
            La economía agéntica{" "}
            <br className="hidden sm:block" />
            <span className="shimmer-text">ya está acá.</span>
          </h2>
          <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
            Sumate a la lista de espera. Primero en conectar, primero en operar.
          </p>

          <form onSubmit={handleSubmit} className="max-w-lg mx-auto">
            <div className="relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-primary/30 via-accent/20 to-secondary/30 rounded-2xl blur-lg opacity-60" />
              <div className="relative flex flex-col sm:flex-row gap-3 p-2 rounded-2xl glass">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="tu@email.com"
                  className="flex-1 px-5 py-4 rounded-xl bg-white/5 border border-white/10 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
                  disabled={status === "loading" || status === "success"}
                />
                <motion.button
                  type="submit"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  disabled={status === "loading" || status === "success"}
                  className="relative px-8 py-4 rounded-xl text-base font-semibold text-white overflow-hidden group disabled:opacity-80 shrink-0"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-secondary rounded-xl" />
                  <span className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-secondary rounded-xl opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500" />
                  <span className="relative flex items-center justify-center gap-2">
                    {status === "loading" ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Enviando...
                      </>
                    ) : status === "success" ? (
                      <>
                        <Check className="w-4 h-4" />
                        ¡Anotado!
                      </>
                    ) : (
                      <>
                        Quiero acceso
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </span>
                </motion.button>
              </div>
            </div>
          </form>

          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ delay: 0.5 }}
            className="text-sm text-muted-foreground mt-8"
          >
            Sin spam. Solo cuando esté listo para vos.
          </motion.p>
        </motion.div>
      </div>
    </section>
  )
}

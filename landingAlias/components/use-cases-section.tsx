"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { Factory, UtensilsCrossed, ArrowUpRight } from "lucide-react"

const useCases = [
  {
    icon: Factory,
    title: "Pagos a proveedores",
    description:
      "Tu agente de operaciones gestiona la cadena de pagos sin que toques nada.",
    span: "md:col-span-1",
    featured: false,
    gradient: "from-emerald-500/20 to-green-600/10",
  },
  {
    icon: UtensilsCrossed,
    title: "Pedido de comida autónomo",
    description:
      "Le pedís al agente que ordene el almuerzo. Él busca opciones, te tira la propuesta, y cuando confirmás paga solo, hace el pedido y después pregunta la demora en caso de necesitarlo.",
    span: "md:col-span-2",
    featured: true,
    gradient: "from-orange-500/20 to-red-600/10",
  },
]

export function UseCasesSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section ref={ref} className="pt-32 pb-0 px-6">
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
            className="inline-block px-4 py-1.5 rounded-full border border-secondary/20 bg-secondary/5 text-secondary text-lg font-medium mb-6"
          >
            Casos de uso
          </motion.span>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 text-balance">
            ¿Qué puede hacer{" "}
            <span className="shimmer-text">tu agente</span>?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Desde pagos recurrentes hasta operaciones complejas,
            tu agente opera con autonomía real.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-4 lg:gap-6 items-start">
          {useCases.map((useCase, i) => (
            <motion.div
              key={useCase.title}
              initial={{ opacity: 0, y: 50, scale: 0.95 }}
              animate={isInView ? { opacity: 1, y: 0, scale: 1 } : {}}
              transition={{ duration: 0.5, delay: 0.2 + i * 0.1 }}
              className={`group relative ${useCase.span}`}
            >
              <div className={`absolute -inset-[1px] bg-gradient-to-r ${useCase.gradient} rounded-2xl opacity-0 group-hover:opacity-100 blur-xl transition-all duration-500`} />

              <div className={`relative glass rounded-2xl ${useCase.featured ? "p-8 lg:p-10" : "p-8"} h-full cursor-pointer transition-all duration-500 hover:border-primary/40 hover:translate-y-[-2px] hover:shadow-[0_16px_48px_-12px_rgba(124,58,237,0.25)] overflow-hidden`}>
                {/* Gradient corner accent */}
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${useCase.gradient} rounded-bl-full opacity-30 group-hover:opacity-60 transition-opacity duration-500`} />

                <div className={`relative flex ${useCase.featured ? "items-start gap-6" : "flex-col gap-5"}`}>
                  <div className="w-14 h-14 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center shrink-0 group-hover:scale-110 group-hover:border-primary/30 transition-all duration-300">
                    <useCase.icon className="w-7 h-7 text-secondary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-xl font-semibold text-foreground group-hover:text-primary transition-colors duration-300">
                        {useCase.title}
                      </h3>
                      <ArrowUpRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all duration-300" />
                    </div>
                    <p className={`text-muted-foreground leading-relaxed ${useCase.featured ? "text-base" : ""}`}>
                      {useCase.description}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

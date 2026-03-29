"use client"

import { motion, useInView } from "framer-motion"
import { useRef, useState, useEffect } from "react"
import { Check, Copy, Terminal, Bot } from "lucide-react"

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"

const skillCommand = `curl -sL ${SITE_URL}/agentpay-skill.md \\
  -o agentpay-skill.md`

const usageCode = `// Your agent now has access to:
await mcp.call("request_payment", {
  destination_cvu: "0000003100099999999999",
  amount: 15000,
  purpose: "Pago freelancer - Proyecto X"
});

// → Payment requested. Awaiting human approval.
// → Approved. Executing transfer...
// → ✓ Transfer completed. Receipt: TRX-8821`

const steps = [
  {
    number: "1",
    title: "Agregá a tu config MCP",
    description: "Configurá Alias como servidor MCP en tu agente.",
  },
  {
    number: "2",
    title: "Fondea tu cuenta",
    description: "Transferí pesos a tu CVU de Alias.",
  },
  {
    number: "3",
    title: "Tu agente ya puede pagar",
    description: "Consultá saldo, solicitá pagos, ejecutá transferencias.",
  },
]

function CodeBlock({ code, filename }: { code: string; filename: string }) {
  const [copied, setCopied] = useState(false)
  const [displayedLines, setDisplayedLines] = useState<string[]>([])
  const lines = code.split('\n')
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  useEffect(() => {
    if (!isInView) return
    
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")
    if (mediaQuery.matches) {
      setDisplayedLines(lines)
      return
    }

    let currentLine = 0
    const timer = setInterval(() => {
      if (currentLine >= lines.length) {
        clearInterval(timer)
        return
      }
      setDisplayedLines((prev) => [...prev, lines[currentLine]])
      currentLine++
    }, 80)

    return () => clearInterval(timer)
  }, [isInView])

  const copyCode = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div ref={ref} className="relative group/code">
      <div className="absolute -inset-1 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-2xl blur-lg opacity-0 group-hover/code:opacity-100 transition-opacity duration-500" />
      <div className="relative glass rounded-2xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 bg-black/40 border-b border-white/[0.06]">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#FF5F56]" />
              <div className="w-3 h-3 rounded-full bg-[#FFBD2E]" />
              <div className="w-3 h-3 rounded-full bg-[#27CA40]" />
            </div>
            <span className="text-xs text-muted-foreground ml-2 font-mono">{filename}</span>
          </div>
          <button
            onClick={copyCode}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        <div className="p-5 overflow-x-auto">
          <pre className="font-mono text-sm leading-relaxed">
            {displayedLines.map((line, i) => {
              const l = line ?? ""
              return (
                <div key={i} className="flex">
                  <span className="text-muted-foreground/50 w-6 select-none text-right mr-4 text-xs">{i + 1}</span>
                  <code className="flex-1">
                    {l.startsWith('//') ? (
                      <span className="text-muted-foreground">{l}</span>
                    ) : l.includes('destination_cvu') || l.includes('amount') || l.includes('purpose') ? (
                      <span>
                        <span className="text-foreground">{l.split(':')[0]}:</span>
                        <span className="text-emerald-400">{l.split(':').slice(1).join(':')}</span>
                      </span>
                    ) : l.includes('await') || l.includes('mcp.call') ? (
                      <span>
                        <span className="text-primary">{l.includes('await') ? 'await ' : ''}</span>
                        <span className="text-secondary">{l.replace('await ', '')}</span>
                      </span>
                    ) : l.startsWith('// →') ? (
                      <span className="text-secondary">{l}</span>
                    ) : (
                      <span className="text-foreground">{l}</span>
                    )}
                  </code>
                </div>
              )
            })}
            {displayedLines.length < lines.length && (
              <div className="flex">
                <span className="text-muted-foreground/50 w-6 select-none text-right mr-4 text-xs">{displayedLines.length + 1}</span>
                <span className="text-secondary animate-pulse">▋</span>
              </div>
            )}
          </pre>
        </div>
      </div>
    </div>
  )
}

function AgentSkillBlock() {
  const [copied, setCopied] = useState(false)

  const copyCommand = () => {
    navigator.clipboard.writeText(skillCommand)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative group/skill">
      <div className="absolute -inset-1 bg-gradient-to-r from-secondary/20 to-primary/20 rounded-2xl blur-lg opacity-0 group-hover/skill:opacity-100 transition-opacity duration-500" />
      <div className="relative glass rounded-2xl overflow-hidden border border-secondary/20">
        <div className="flex items-center justify-between px-4 py-3 bg-secondary/[0.06] border-b border-white/[0.06]">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-secondary" />
            <span className="text-sm font-medium text-secondary">Para agentes</span>
          </div>
          <button
            onClick={copyCommand}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
        <div className="px-5 py-4">
          <p className="text-xs text-muted-foreground mb-3">
            Importá la skill de AgentPay directamente en tu agente:
          </p>
          <div className="flex items-start gap-2 bg-black/30 rounded-lg px-4 py-3">
            <span className="text-secondary font-mono text-sm select-none shrink-0">$</span>
            <pre className="font-mono text-sm text-foreground whitespace-pre-wrap break-all">
              {skillCommand}
            </pre>
          </div>
          <p className="text-xs text-muted-foreground/70 mt-3">
            La skill le enseña a tu agente a usar las tools de pago, verificar saldo,
            respetar límites y manejar todos los estados del flujo.
          </p>
        </div>
      </div>
    </div>
  )
}

export function DeveloperSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section ref={ref} className="py-32 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-secondary/[0.03] to-transparent pointer-events-none" />

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
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-secondary/20 bg-secondary/5 text-secondary text-lg font-medium mb-6"
          >
            <Terminal className="w-4 h-4" />
            Para developers
          </motion.span>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
            Conectá tu agente en{" "}
            <span className="shimmer-text">2 minutos</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            MCP nativo. Tres herramientas. Sin SDKs complejos.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-start">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="space-y-8"
          >
            {steps.map((step) => (
              <div key={step.number} className="flex items-start gap-5 group">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shrink-0 shadow-lg shadow-primary/20 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-lg font-bold text-white">{step.number}</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-1 text-foreground group-hover:text-primary transition-colors">{step.title}</h3>
                  <p className="text-muted-foreground">{step.description}</p>
                </div>
              </div>
            ))}

            <div className="pt-4">
              <p className="text-sm text-muted-foreground mb-4">
                Herramientas disponibles via MCP:
              </p>
              <div className="flex flex-wrap gap-2">
                {['get_balance', 'request_payment', 'get_payment_request', 'list_payment_requests', 'get_agent_config'].map((tool) => (
                  <span
                    key={tool}
                    className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-mono text-muted-foreground hover:border-primary/30 hover:text-primary transition-all duration-300"
                  >
                    {tool}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="space-y-6"
          >
            <AgentSkillBlock />
            <CodeBlock code={usageCode} filename="agent.ts" />
          </motion.div>
        </div>
      </div>
    </section>
  )
}

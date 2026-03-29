"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Check, Copy, Bot } from "lucide-react"

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"

const terminalLines = [
  { text: '$ ', color: 'text-secondary', rest: `curl -sL ${SITE_URL}/agentpay-skill.md \\`, restColor: 'text-foreground' },
  { text: '    -o ', color: 'text-foreground', rest: 'agentpay-skill.md', restColor: 'text-green-400' },
  { text: '', color: 'text-foreground' },
  { text: '# ✓ Skill downloaded', color: 'text-muted-foreground' },
  { text: '', color: 'text-foreground' },
  { text: '$ ', color: 'text-secondary', rest: 'cat agentpay-skill.md | head -5', restColor: 'text-foreground' },
  { text: '', color: 'text-foreground' },
  { text: '# AgentPay Skill — Pagos en pesos con CVU', color: 'text-green-400' },
  { text: '# Tu agente aprende a pagar, verificar saldo,', color: 'text-muted-foreground' },
  { text: '# respetar límites y manejar el flujo completo.', color: 'text-muted-foreground' },
]

const skillCommandText = `curl -sL ${SITE_URL}/agentpay-skill.md \\\n  -o agentpay-skill.md`

export function TerminalWindow() {
  const [visibleLines, setVisibleLines] = useState(0)
  const [showCursor, setShowCursor] = useState(true)
  const [copied, setCopied] = useState(false)

  const copyCommand = () => {
    navigator.clipboard.writeText(skillCommandText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")

    if (mediaQuery.matches) {
      setVisibleLines(terminalLines.length)
      return
    }

    const timer = setInterval(() => {
      setVisibleLines((prev) => {
        if (prev >= terminalLines.length) {
          clearInterval(timer)
          return prev
        }
        return prev + 1
      })
    }, 200)

    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const cursorTimer = setInterval(() => {
      setShowCursor((prev) => !prev)
    }, 530)
    return () => clearInterval(cursorTimer)
  }, [])

  return (
    <div className="relative">
      <div className="glass rounded-2xl overflow-hidden shadow-2xl transform-gpu" style={{ transform: 'perspective(1000px) rotateY(-5deg) rotateX(5deg)' }}>
        <div className="flex items-center justify-between px-4 py-3 bg-black/40 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#FF5F56]" />
              <div className="w-3 h-3 rounded-full bg-[#FFBD2E]" />
              <div className="w-3 h-3 rounded-full bg-[#27CA40]" />
            </div>
            <Bot className="w-3.5 h-3.5 text-secondary ml-2" />
            <span className="text-xs text-muted-foreground font-mono">agent — skill install</span>
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

        <div className="p-6 font-mono text-sm leading-relaxed overflow-x-auto">
          <pre>
            {terminalLines.slice(0, visibleLines).map((line, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2 }}
              >
                <span className={line.color}>{line.text}</span>
                {line.rest && <span className={line.restColor}>{line.rest}</span>}
              </motion.div>
            ))}
            {visibleLines < terminalLines.length && (
              <div>
                <span className={`${showCursor ? 'opacity-100' : 'opacity-0'} text-secondary transition-opacity`}>▋</span>
              </div>
            )}
          </pre>
        </div>
      </div>
    </div>
  )
}

"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Check, Copy } from "lucide-react"

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"

const terminalLines = [
  { text: '$ ', color: 'text-[#A89880]', rest: `curl -sL ${SITE_URL}/agentpay-skill.md \\`, restColor: 'text-[#D4CBC0]' },
  { text: '    -o ', color: 'text-[#D4CBC0]', rest: 'agentpay-skill.md', restColor: 'text-[#B8C9A3]' },
  { text: '', color: '' },
  { text: '# ✓ Skill downloaded', color: 'text-[#5C5650]' },
  { text: '', color: '' },
  { text: '$ ', color: 'text-[#A89880]', rest: 'cat agentpay-skill.md | head -5', restColor: 'text-[#D4CBC0]' },
  { text: '', color: '' },
  { text: '# AgentPay Skill — Pagos en pesos con CVU', color: 'text-[#B8C9A3]' },
  { text: '# Tu agente aprende a pagar, verificar saldo,', color: 'text-[#5C5650]' },
  { text: '# respetar límites y manejar el flujo completo.', color: 'text-[#5C5650]' },
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
    const cursorTimer = setInterval(() => setShowCursor((p) => !p), 530)
    return () => clearInterval(cursorTimer)
  }, [])

  return (
    <div className="relative">
      <div className="absolute -inset-px rounded-2xl bg-[#1A1A1A]/[0.03]" />
      <div
        className="relative rounded-2xl overflow-hidden bg-[#181715] border border-[#2A2725]"
        style={{ boxShadow: "0 20px 60px -12px rgba(26, 26, 26, 0.25), 0 0 0 1px rgba(26,26,26,0.05)" }}
      >
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#2A2725]">
          <div className="flex items-center gap-2.5">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-[#3A3530]" />
              <div className="w-3 h-3 rounded-full bg-[#3A3530]" />
              <div className="w-3 h-3 rounded-full bg-[#3A3530]" />
            </div>
            <span className="text-[11px] text-[#5C5650] font-mono ml-2">~/agent</span>
          </div>
          <button
            onClick={copyCommand}
            className="flex items-center gap-1.5 text-[11px] text-[#5C5650] hover:text-[#A89880] transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-[#B8C9A3]" />
                <span className="text-[#B8C9A3]">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        <div className="px-5 py-5 font-mono text-[13px] leading-[1.8]">
          <pre className="m-0">
            {terminalLines.slice(0, visibleLines).map((line, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.15 }}
                className="min-h-[1.8em]"
              >
                <span className={line.color}>{line.text}</span>
                {line.rest && <span className={line.restColor}>{line.rest}</span>}
              </motion.div>
            ))}
            {visibleLines < terminalLines.length && (
              <div className="min-h-[1.8em]">
                <span className={`${showCursor ? 'opacity-100' : 'opacity-0'} text-[#A89880] transition-opacity`}>▋</span>
              </div>
            )}
          </pre>
        </div>
      </div>
    </div>
  )
}

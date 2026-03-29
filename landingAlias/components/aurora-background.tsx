"use client"

import { useEffect, useRef } from "react"

const WORDS_A = [
  "hamaca", "perro", "mate", "vaso", "luna", "tango", "rio", "cielo",
  "fuego", "plata", "dulce", "campo", "asado", "barco", "nube", "sol",
  "arbol", "carta", "gato", "libro", "mesa", "piedra", "reloj", "viento",
  "agua", "flor", "puerta", "trigo", "bici", "farol", "globo", "hoja",
  "jaula", "kiosko", "leche", "mango", "nariz", "oveja", "pasto", "queso",
]

const WORDS_B = [
  "compu", "hambre", "zapato", "silla", "pared", "techo", "llave", "torta",
  "trueno", "humo", "hierro", "cobre", "nieve", "rayo", "sombra", "chispa",
  "crema", "polvo", "tinta", "menta", "coral", "bruma", "seda", "lana",
  "fibra", "calma", "brisa", "pulso", "ritmo", "trazo", "ancla", "faro",
  "nudo", "ola", "canto", "marca", "surco", "raiz", "borde", "grano",
]

const WORDS_C = [
  "auto", "helado", "heladera", "guitarra", "ventana", "estrella", "cuadro",
  "espejo", "alfombra", "timbre", "moneda", "antena", "ladrillo", "botella",
  "linterna", "campana", "escalera", "almohada", "bandera", "cadena",
  "diamante", "enchufe", "frazada", "galleta", "herradura", "imprenta",
  "jardin", "kayak", "lampara", "madera", "naranja", "oceano", "paloma",
]

function seededRandom(seed: number) {
  let s = seed
  return () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff
    return s / 0x7fffffff
  }
}

function generateAlias(rand: () => number) {
  const a = WORDS_A[Math.floor(rand() * WORDS_A.length)]
  const b = WORDS_B[Math.floor(rand() * WORDS_B.length)]
  const c = WORDS_C[Math.floor(rand() * WORDS_C.length)]
  return `${a}.${b}.${c}`
}

export function AuroraBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animId: number
    let startTime: number | null = null
    const speed = 12

    const setupCanvas = () => {
      const dpr = window.devicePixelRatio || 1
      const w = window.innerWidth
      const h = window.innerHeight
      canvas.width = w * dpr
      canvas.height = h * dpr
      canvas.style.width = `${w}px`
      canvas.style.height = `${h}px`
      return { dpr, w, h }
    }

    const draw = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const elapsed = (timestamp - startTime) / 1000

      const { dpr, w, h } = setupCanvas()
      ctx.scale(dpr, dpr)
      ctx.clearRect(0, 0, w, h)

      const rand = seededRandom(42)
      const fontSize = Math.max(12, Math.min(14, w * 0.009))
      ctx.textAlign = "left"

      const lineHeight = fontSize * 3.2
      const colWidth = fontSize * 20
      const cols = Math.ceil(w / colWidth) + 4
      const rows = Math.ceil(h / lineHeight) + 4

      const offsetX = (elapsed * speed) % colWidth
      const offsetY = (elapsed * speed * 0.3) % lineHeight

      for (let row = -2; row < rows; row++) {
        for (let col = -2; col < cols; col++) {
          const alias = generateAlias(rand)
          const baseX = col * colWidth + (row % 2 === 0 ? 0 : colWidth * 0.5) - offsetX
          const baseY = row * lineHeight + fontSize - offsetY
          const jitterX = (rand() - 0.5) * colWidth * 0.15
          const jitterY = (rand() - 0.5) * lineHeight * 0.15
          const finalX = baseX + jitterX
          const finalY = baseY + jitterY
          const sizeVariation = 0.9 + rand() * 0.2

          const baseOpacity = 0.13 + rand() * 0.09

          if (baseOpacity < 0.02) continue

          ctx.font = `400 ${fontSize * sizeVariation}px 'Geist Mono', monospace`
          ctx.fillStyle = `rgba(100, 85, 60, ${baseOpacity})`
          ctx.fillText(alias, finalX, finalY)
        }
      }

      animId = requestAnimationFrame(draw)
    }

    animId = requestAnimationFrame(draw)
    window.addEventListener("resize", () => { startTime = null })
    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener("resize", () => { startTime = null })
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10"
      style={{ background: "#F5F0E8" }}
    />
  )
}

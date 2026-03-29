"use client"

import { useEffect, useRef } from "react"

export function AuroraBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animationId: number
    let time = 0

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resize()
    window.addEventListener("resize", resize)

    const draw = () => {
      time += 0.002

      ctx.fillStyle = "#050505"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      const blobs = [
        {
          x: canvas.width * 0.25 + Math.sin(time * 0.5) * 150,
          y: canvas.height * 0.35 + Math.cos(time * 0.3) * 100,
          radius: 500,
          color1: "rgba(124, 58, 237, 0.18)",
          color2: "rgba(124, 58, 237, 0)",
        },
        {
          x: canvas.width * 0.75 + Math.cos(time * 0.4) * 180,
          y: canvas.height * 0.25 + Math.sin(time * 0.6) * 80,
          radius: 450,
          color1: "rgba(6, 182, 212, 0.15)",
          color2: "rgba(6, 182, 212, 0)",
        },
        {
          x: canvas.width * 0.5 + Math.sin(time * 0.7) * 120,
          y: canvas.height * 0.6 + Math.cos(time * 0.5) * 140,
          radius: 550,
          color1: "rgba(168, 85, 247, 0.12)",
          color2: "rgba(168, 85, 247, 0)",
        },
        {
          x: canvas.width * 0.15 + Math.cos(time * 0.3) * 80,
          y: canvas.height * 0.75 + Math.sin(time * 0.4) * 90,
          radius: 400,
          color1: "rgba(59, 130, 246, 0.1)",
          color2: "rgba(59, 130, 246, 0)",
        },
        {
          x: canvas.width * 0.85 + Math.sin(time * 0.6) * 100,
          y: canvas.height * 0.8 + Math.cos(time * 0.35) * 60,
          radius: 350,
          color1: "rgba(16, 185, 129, 0.08)",
          color2: "rgba(16, 185, 129, 0)",
        },
      ]

      blobs.forEach((blob) => {
        const gradient = ctx.createRadialGradient(
          blob.x, blob.y, 0,
          blob.x, blob.y, blob.radius
        )
        gradient.addColorStop(0, blob.color1)
        gradient.addColorStop(1, blob.color2)

        ctx.beginPath()
        ctx.fillStyle = gradient
        ctx.arc(blob.x, blob.y, blob.radius, 0, Math.PI * 2)
        ctx.fill()
      })

      animationId = requestAnimationFrame(draw)
    }

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")
    if (!mediaQuery.matches) {
      draw()
    } else {
      ctx.fillStyle = "#050505"
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      const gradient = ctx.createRadialGradient(
        canvas.width * 0.5, canvas.height * 0.4, 0,
        canvas.width * 0.5, canvas.height * 0.4, 600
      )
      gradient.addColorStop(0, "rgba(124, 58, 237, 0.18)")
      gradient.addColorStop(1, "rgba(124, 58, 237, 0)")
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, canvas.width, canvas.height)
    }

    return () => {
      window.removeEventListener("resize", resize)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10"
      style={{ background: "#050505" }}
    />
  )
}

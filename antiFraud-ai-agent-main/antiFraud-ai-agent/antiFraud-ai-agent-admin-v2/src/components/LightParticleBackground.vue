<template>
  <canvas ref="canvasRef" class="particle-canvas" aria-hidden="true"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)

let ctx = null
let animationId = null
let particles = []
let orbs = []
let mouseX = -9999
let mouseY = -9999
let canvasWidth = 0
let canvasHeight = 0
let dpr = 1
let time = 0

// ===== 配色（暖白 + 雾蓝紫点缀）=====
const CONFIG = {
  particleCount: 140,
  colors: ['#4A90D9', '#7B68EE', '#6BB5FF', '#9B8EFF', '#5BA3EC'],
  lineColor: 'rgba(74, 144, 217, 0.10)',
  lineHoverColor: 'rgba(74, 144, 217, 0.28)',
  lineDistance: 160,
  mouseRadius: 220,
  particleSize: 2.4,
  particleSizeHover: 4,
  baseSpeed: 0.35,
  // 背景：暖白 → 极淡蓝
  bgTop: '#FBFBFA',
  bgMid: '#F4F7FB',
  bgBottom: '#EAEEF6',
}

class Particle {
  constructor() {
    this.reset()
  }

  reset() {
    this.x = Math.random() * canvasWidth
    this.y = Math.random() * canvasHeight
    this.vx = (Math.random() - 0.5) * CONFIG.baseSpeed
    this.vy = (Math.random() - 0.5) * CONFIG.baseSpeed
    this.size = Math.random() * 1.6 + 0.6
    this.baseSize = this.size
    this.alpha = Math.random() * 0.35 + 0.35
    this.pulse = Math.random() * Math.PI * 2
    this.color = CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)]
    this.orbitX = Math.random() * 100
    this.orbitY = Math.random() * 100
    this.orbitAmp = 0.08 + Math.random() * 0.18
  }

  update() {
    time += 0.004
    this.pulse += 0.018
    // 漂浮感：正弦扰动
    this.x += this.vx + Math.sin(time + this.orbitX) * this.orbitAmp
    this.y += this.vy + Math.cos(time + this.orbitY) * this.orbitAmp

    if (this.x < 0 || this.x > canvasWidth) this.vx *= -1
    if (this.y < 0 || this.y > canvasHeight) this.vy *= -1

    // 鼠标交互
    const dx = this.x - mouseX
    const dy = this.y - mouseY
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist < CONFIG.mouseRadius) {
      const t = 1 - dist / CONFIG.mouseRadius
      this.size = this.baseSize + (CONFIG.particleSizeHover - this.baseSize) * t
    } else {
      this.size = this.baseSize
    }
  }

  draw() {
    if (!ctx) return
    const pulseAlpha = 0.7 + 0.3 * Math.sin(this.pulse)
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.globalAlpha = this.alpha * pulseAlpha
    ctx.fill()
    ctx.globalAlpha = 1
  }
}

// 大型漂浮光斑（环境光感）
class Orb {
  constructor() {
    this.reset()
  }
  reset() {
    this.x = Math.random() * canvasWidth
    this.y = Math.random() * canvasHeight
    this.radius = 180 + Math.random() * 220
    this.vx = (Math.random() - 0.5) * 0.15
    this.vy = (Math.random() - 0.5) * 0.15
    // 极淡的彩色径向光斑
    const palette = [
      'rgba(123, 104, 238, 0.10)', // 紫
      'rgba(74, 144, 217, 0.10)',  // 蓝
      'rgba(107, 181, 255, 0.08)', // 浅蓝
      'rgba(155, 142, 255, 0.08)', // 淡紫
    ]
    this.color = palette[Math.floor(Math.random() * palette.length)]
  }
  update() {
    this.x += this.vx
    this.y += this.vy
    if (this.x < -this.radius || this.x > canvasWidth + this.radius) this.vx *= -1
    if (this.y < -this.radius || this.y > canvasHeight + this.radius) this.vy *= -1
  }
  draw() {
    if (!ctx) return
    const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius)
    g.addColorStop(0, this.color)
    g.addColorStop(1, this.color.replace(/[\d.]+\)$/, '0)'))
    ctx.fillStyle = g
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fill()
  }
}

function initParticles() {
  particles = []
  for (let i = 0; i < CONFIG.particleCount; i++) {
    particles.push(new Particle())
  }
  orbs = []
  for (let i = 0; i < 5; i++) orbs.push(new Orb())
}

function drawBackground() {
  if (!ctx) return
  // 三段式垂直渐变：暖白 → 极淡蓝
  const gradient = ctx.createLinearGradient(0, 0, 0, canvasHeight)
  gradient.addColorStop(0, CONFIG.bgTop)
  gradient.addColorStop(0.5, CONFIG.bgMid)
  gradient.addColorStop(1, CONFIG.bgBottom)
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)
}

function drawLines() {
  if (!ctx) return
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < CONFIG.lineDistance) {
        const alpha = (1 - dist / CONFIG.lineDistance) * 0.4

        const miDx = (particles[i].x + particles[j].x) / 2 - mouseX
        const miDy = (particles[i].y + particles[j].y) / 2 - mouseY
        const miDist = Math.sqrt(miDx * miDx + miDy * miDy)
        const isNearMouse = miDist < CONFIG.mouseRadius

        ctx.beginPath()
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        if (isNearMouse) {
          ctx.strokeStyle = `rgba(74, 144, 217, ${Math.min(alpha + 0.22, 0.55)})`
          ctx.lineWidth = 1.2
        } else {
          ctx.strokeStyle = `rgba(74, 144, 217, ${alpha * 0.32})`
          ctx.lineWidth = 0.6
        }
        ctx.stroke()
      }
    }
  }
}

function drawGlow() {
  if (!ctx) return
  for (const p of particles) {
    const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 4)
    gradient.addColorStop(0, 'rgba(74, 144, 217, 0.07)')
    gradient.addColorStop(1, 'rgba(74, 144, 217, 0)')
    ctx.fillStyle = gradient
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size * 4, 0, Math.PI * 2)
    ctx.fill()
  }
}

function animate() {
  if (!ctx) return
  drawBackground()

  // 大光斑（最底层）
  for (const o of orbs) {
    o.update()
    o.draw()
  }

  drawGlow()

  for (const p of particles) {
    p.update()
    p.draw()
  }

  drawLines()

  animationId = requestAnimationFrame(animate)
}

function handleResize() {
  const canvas = canvasRef.value
  if (!canvas) return
  dpr = Math.min(window.devicePixelRatio || 1, 2)
  canvasWidth = window.innerWidth
  canvasHeight = window.innerHeight
  canvas.width = canvasWidth * dpr
  canvas.height = canvasHeight * dpr
  canvas.style.width = canvasWidth + 'px'
  canvas.style.height = canvasHeight + 'px'
  if (ctx) {
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    ctx.scale(dpr, dpr)
  }
  const targetCount = Math.floor((canvasWidth * canvasHeight) / 9000)
  CONFIG.particleCount = Math.max(80, Math.min(targetCount, 280))
  initParticles()
}

let resizeTimer = null
function throttledResize() {
  if (resizeTimer) return
  resizeTimer = setTimeout(() => {
    handleResize()
    resizeTimer = null
  }, 200)
}

function handleMouseMove(e) {
  mouseX = e.clientX
  mouseY = e.clientY
}

function handleMouseLeave() {
  mouseX = -9999
  mouseY = -9999
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  ctx = canvas.getContext('2d')
  handleResize()
  initParticles()
  animate()

  window.addEventListener('resize', throttledResize)
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseleave', handleMouseLeave)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', throttledResize)
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseleave', handleMouseLeave)
  ctx = null
  particles = []
  orbs = []
})
</script>

<style scoped>
.particle-canvas {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
}
</style>
<template>
  <canvas ref="canvasRef" class="particle-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)

let ctx = null
let animationId = null
let particles = []
let mouseX = -9999
let mouseY = -9999
let canvasWidth = 0
let canvasHeight = 0

// ===== 配置 =====
const CONFIG = {
  particleCount: 180,
  particleColor: '#165DFF',
  lineColor: 'rgba(22, 93, 255, 0.15)',
  lineHoverColor: 'rgba(22, 93, 255, 0.4)',
  lineDistance: 150,
  mouseRadius: 200,
  particleSize: 2,
  particleSizeHover: 3.5,
  speed: 0.4,
  bgColor: '#0a0e1a',
}

class Particle {
  constructor() {
    this.reset()
  }

  reset() {
    this.x = Math.random() * canvasWidth
    this.y = Math.random() * canvasHeight
    this.vx = (Math.random() - 0.5) * CONFIG.speed
    this.vy = (Math.random() - 0.5) * CONFIG.speed
    this.size = Math.random() * 1.5 + 0.5
    this.baseSize = this.size
    this.alpha = Math.random() * 0.5 + 0.3
    this.pulse = Math.random() * Math.PI * 2
  }

  update() {
    this.pulse += 0.02
    this.x += this.vx
    this.y += this.vy

    // 边缘回弹
    if (this.x < 0 || this.x > canvasWidth) this.vx *= -1
    if (this.y < 0 || this.y > canvasHeight) this.vy *= -1

    // 鼠标交互 — 靠近时变大
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
    const pulseAlpha = 0.6 + 0.4 * Math.sin(this.pulse)
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(22, 93, 255, ${this.alpha * pulseAlpha})`
    ctx.fill()
  }
}

function initParticles() {
  particles = []
  for (let i = 0; i < CONFIG.particleCount; i++) {
    particles.push(new Particle())
  }
}

function drawLines() {
  if (!ctx) return
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < CONFIG.lineDistance) {
        const alpha = (1 - dist / CONFIG.lineDistance) * 0.5

        // 判断是否靠近鼠标
        const miDx = (particles[i].x + particles[j].x) / 2 - mouseX
        const miDy = (particles[i].y + particles[j].y) / 2 - mouseY
        const miDist = Math.sqrt(miDx * miDx + miDy * miDy)
        const isNearMouse = miDist < CONFIG.mouseRadius

        const color = isNearMouse
          ? CONFIG.lineHoverColor
          : CONFIG.lineColor
        ctx.beginPath()
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        ctx.strokeStyle = isNearMouse
          ? `rgba(22, 93, 255, ${Math.min(alpha + 0.3, 0.6)})`
          : `rgba(22, 93, 255, ${alpha * 0.4})`
        ctx.lineWidth = isNearMouse ? 1.2 : 0.6
        ctx.stroke()
      }
    }
  }
}

function animate() {
  if (!ctx) return
  ctx.clearRect(0, 0, canvasWidth, canvasHeight)

  // 绘制背景
  ctx.fillStyle = CONFIG.bgColor
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  // 绘制一个微弱的网格底纹（像素点阵感）
  drawGrid()

  // 更新 & 绘制粒子
  for (const p of particles) {
    p.update()
    p.draw()
  }

  // 绘制连线
  drawLines()

  animationId = requestAnimationFrame(animate)
}

function drawGrid() {
  if (!ctx) return
  const gridSize = 60
  ctx.fillStyle = 'rgba(22, 93, 255, 0.03)'
  for (let x = 0; x < canvasWidth; x += gridSize) {
    for (let y = 0; y < canvasHeight; y += gridSize) {
      ctx.fillRect(x, y, 1, 1)
    }
  }
}

function handleResize() {
  const canvas = canvasRef.value
  if (!canvas) return
  canvasWidth = window.innerWidth
  canvasHeight = window.innerHeight
  canvas.width = canvasWidth * devicePixelRatio
  canvas.height = canvasHeight * devicePixelRatio
  canvas.style.width = canvasWidth + 'px'
  canvas.style.height = canvasHeight + 'px'
  if (ctx) {
    ctx.scale(devicePixelRatio, devicePixelRatio)
  }
  // 粒子数量随分辨率自适应
  const targetCount = Math.floor((canvasWidth * canvasHeight) / 8000)
  CONFIG.particleCount = Math.max(80, Math.min(targetCount, 300))
  initParticles()
}

// 节流 resize
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
})
</script>

<style scoped>
.particle-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
}
</style>
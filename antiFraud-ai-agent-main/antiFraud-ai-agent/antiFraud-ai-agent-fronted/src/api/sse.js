import { API_BASE } from '../config'

/**
 * 拼接带 query 的完整 URL（支持绝对 API_BASE 或以 / 开头的相对前缀，便于 Vite 代理）。
 * @param {string} path 如 `/ai/love_app/chat/sse`
 * @param {Record<string, string>} query
 */
export function buildApiUrl(path, query = {}) {
  const base = API_BASE.replace(/\/$/, '') || ''
  const p = path.startsWith('/') ? path : `/${path}`
  const joined = `${base}${p}`.replace(/([^:]\/)\/+/g, '$1')
  const url =
    joined.startsWith('http://') || joined.startsWith('https://')
      ? new URL(joined)
      : new URL(joined.startsWith('/') ? joined : `/${joined}`, window.location.origin)
  for (const [k, v] of Object.entries(query)) {
    if (v != null) url.searchParams.set(k, String(v))
  }
  return url.toString()
}

/**
 * Spring WebFlux `ServerSentEvent<String>` 常把 data 写成 JSON 字符串（带引号与转义），此处解包。
 * @param {string} raw
 */
export function normalizeSseDataPayload(raw) {
  const t = raw.replace(/\r/g, '').trimEnd()
  if (t === '' || t === '[DONE]') return ''
  try {
    const parsed = JSON.parse(t)
    if (typeof parsed === 'string') return parsed
  } catch {
    /* 非 JSON 则原样返回 */
  }
  return raw
}

/**
 * 消费 text/event-stream：按行解析 SSE，遇空行结束一条事件；流结束时冲刷未闭合的 data。
 * @param {string} url
 * @param {{ signal?: AbortSignal; onChunk: (text: string) => void }} options
 */
export async function consumeEventStream(url, { signal, onChunk }) {
  const res = await fetch(url, {
    method: 'GET',
    signal,
    headers: { Accept: 'text/event-stream' },
    cache: 'no-store',
  })

  if (!res.ok) {
    const errText = await res.text().catch(() => '')
    throw new Error(errText || `请求失败：HTTP ${res.status}`)
  }

  const reader = res.body?.getReader()
  if (!reader) {
    throw new Error('响应不支持流式读取')
  }

  const decoder = new TextDecoder()
  /** 未拼成完整行（无 \n）的尾部 */
  let lineCarry = ''
  /** 当前事件内多条 data: 行 */
  let eventDataLines = []

  const flushEvent = () => {
    if (!eventDataLines.length) return
    const merged = eventDataLines.join('\n')
    eventDataLines = []
    const text = normalizeSseDataPayload(merged)
    if (text !== '') onChunk(text)
  }

  const consumeLines = (text, eof) => {
    let buf = lineCarry + text
    lineCarry = ''

    while (true) {
      const nl = buf.indexOf('\n')
      if (nl === -1) {
        lineCarry = buf
        break
      }
      let line = buf.slice(0, nl)
      buf = buf.slice(nl + 1)
      if (line.endsWith('\r')) line = line.slice(0, -1)

      if (line === '') {
        flushEvent()
      } else if (line.startsWith(':')) {
        /* SSE 注释 / 心跳 */
      } else if (line.startsWith('data:')) {
        eventDataLines.push(line.slice(5).trimStart())
      }
    }

    if (eof) {
      if (lineCarry !== '') {
        let line = lineCarry
        if (line.endsWith('\r')) line = line.slice(0, -1)
        lineCarry = ''
        if (line.startsWith('data:')) {
          eventDataLines.push(line.slice(5).trimStart())
        } else if (line.trim() !== '') {
          eventDataLines.push(line)
        }
      }
      flushEvent()
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    consumeLines(decoder.decode(value, { stream: true }), false)
  }
  consumeLines(decoder.decode(), true)
}

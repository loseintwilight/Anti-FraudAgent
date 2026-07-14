/**
 * 按后端 AntiFraudManus 输出格式拆分：每条以 "Step 数字:" 开头（忽略大小写，允许 Step 与数字间多空格）。
 * 若首段在第一个 Step 之前还有文字（如错误提示），会作为单独一条气泡。
 * @param {string} text
 * @returns {string[]}
 */
export function splitManusStreamIntoSegments(text) {
  if (text == null || text === '') return []

  const re = /Step\s+(\d+)\s*:/gi
  /** @type {{ index: number }[]} */
  const matches = []
  let m
  while ((m = re.exec(text)) !== null) {
    matches.push({ index: m.index })
  }

  if (matches.length === 0) {
    return [text]
  }

  const out = []
  if (matches[0].index > 0) {
    const prefix = text.slice(0, matches[0].index).trimEnd()
    if (prefix) out.push(prefix)
  }

  for (let i = 0; i < matches.length; i++) {
    const start = matches[i].index
    const end = i + 1 < matches.length ? matches[i + 1].index : text.length
    const piece = text.slice(start, end).trimEnd()
    if (piece) out.push(piece)
  }

  return out
}

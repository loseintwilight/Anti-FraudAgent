/**
 * 反诈卫士 - API 工具模块
 * 封装所有后端 API 调用
 */

const API_BASE_URL = 'http://localhost:8123';

/**
 * 通用请求函数
 * @param {string} endpoint - API 端点路径
 * @param {string} method - 请求方法 (GET, POST)
 * @param {object|null} body - 请求体数据
 * @returns {Promise<object>} 响应数据
 */
async function apiRequest(endpoint, method = 'GET', body = null) {
  const url = `${API_BASE_URL}${endpoint}`;

  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };

  if (body !== null) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    throw new Error(`API 请求失败 (${response.status}): ${errorText || response.statusText}`);
  }

  const data = await response.json();

  if (data.code !== 0 && data.code !== undefined) {
    throw new Error(data.message || 'API 返回错误');
  }

  return data;
}

/**
 * 诈骗风险检测
 * 调用 POST /api/v1/risk/assess
 * @param {string} text - 待检测的文本内容
 * @returns {Promise<object>} 检测结果
 */
export async function assessRisk(text) {
  if (!text || typeof text !== 'string') {
    throw new Error('检测文本不能为空');
  }

  const trimmedText = text.trim();
  if (trimmedText.length === 0) {
    throw new Error('检测文本不能为空');
  }

  return apiRequest('/api/v1/risk/assess', 'POST', { text: trimmedText });
}

/**
 * 批量检测文本
 * @param {string[]} texts - 文本数组
 * @returns {Promise<object[]>} 检测结果数组
 */
export async function batchAssessRisk(texts) {
  if (!Array.isArray(texts) || texts.length === 0) {
    throw new Error('检测文本列表不能为空');
  }

  const results = [];
  for (const text of texts) {
    const result = await assessRisk(text);
    results.push(result);
  }
  return results;
}

/**
 * 获取检测历史
 * @returns {Promise<Array>} 历史记录列表
 */
export async function getHistory() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['detectHistory'], (result) => {
      const history = result.detectHistory || [];
      resolve(history);
    });
  });
}

/**
 * 保存检测记录到历史
 * @param {object} record - 检测记录
 * @returns {Promise<void>}
 */
export async function saveHistory(record) {
  const history = await getHistory();
  history.unshift({
    ...record,
    id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
    timestamp: Date.now()
  });
  // 只保留最近 100 条记录
  if (history.length > 100) {
    history.length = 100;
  }
  return new Promise((resolve) => {
    chrome.storage.local.set({ detectHistory: history }, resolve);
  });
}

/**
 * 清除检测历史
 * @returns {Promise<void>}
 */
export async function clearHistory() {
  return new Promise((resolve) => {
    chrome.storage.local.remove('detectHistory', resolve);
  });
}

export async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.message || '登录失败')
  }
  return response.json()
}

export async function register(username, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.message || '注册失败')
  }
  return response.json()
}

export default {
  assessRisk,
  batchAssessRisk,
  getHistory,
  saveHistory,
  clearHistory,
  login,
  register
};
/**
 * 反诈卫士 - 弹出窗口脚本
 * 负责 popup 页面的交互逻辑、API 调用、结果展示
 */

// ===== 登录状态 =====
const LOGIN_STORAGE_KEY = 'antiFraud_auth'

function getAuth() {
  try {
    const data = localStorage.getItem(LOGIN_STORAGE_KEY)
    return data ? JSON.parse(data) : null
  } catch { return null }
}

function setAuth(token, username) {
  localStorage.setItem(LOGIN_STORAGE_KEY, JSON.stringify({ token, username, loginTime: Date.now() }))
}

function clearAuth() {
  localStorage.removeItem(LOGIN_STORAGE_KEY)
}

function isLoggedIn() {
  const auth = getAuth()
  return auth && auth.token
}

// 登录/注册 UI 控制
const loginOverlay = document.getElementById('loginOverlay')
const loginForm = document.querySelector('.login-form')
const registerForm = document.getElementById('registerForm')
const loginBtn = document.getElementById('loginBtn')
const registerBtn = document.getElementById('registerBtn')
const registerLink = document.getElementById('registerLink')
const backToLoginLink = document.getElementById('backToLoginLink')
const loginError = document.getElementById('loginError')
const regError = document.getElementById('regError')

// 切换登录/注册表单
registerLink.addEventListener('click', (e) => {
  e.preventDefault()
  loginForm.style.display = 'none'
  registerForm.style.display = 'block'
  hideError(loginError)
})

backToLoginLink.addEventListener('click', (e) => {
  e.preventDefault()
  loginForm.style.display = 'block'
  registerForm.style.display = 'none'
  hideError(regError)
})

function showError(el, msg) {
  el.textContent = msg
  el.style.display = 'block'
}

function hideError(el) {
  el.style.display = 'none'
  el.textContent = ''
}

// 登录
loginBtn.addEventListener('click', async () => {
  const username = document.getElementById('loginUsername').value.trim()
  const password = document.getElementById('loginPassword').value.trim()
  if (!username || !password) {
    showError(loginError, '请输入用户名和密码')
    return
  }
  hideError(loginError)
  loginBtn.disabled = true
  loginBtn.textContent = '登录中...'
  
  try {
    const res = await api.login(username, password)
    if (res.success) {
      setAuth(res.token, username)
      checkLoginState()
    } else {
      showError(loginError, res.message || '登录失败')
    }
  } catch (err) {
    showError(loginError, err.message || '登录失败，请重试')
  } finally {
    loginBtn.disabled = false
    loginBtn.textContent = '登 录'
  }
})

// 注册
registerBtn.addEventListener('click', async () => {
  const username = document.getElementById('regUsername').value.trim()
  const password = document.getElementById('regPassword').value.trim()
  const confirm = document.getElementById('regConfirm').value.trim()
  
  hideError(regError)
  if (!username || !password || !confirm) {
    showError(regError, '请填写所有字段')
    return
  }
  if (password.length < 6) {
    showError(regError, '密码长度不少于6位')
    return
  }
  if (password !== confirm) {
    showError(regError, '两次密码不一致')
    return
  }
  
  registerBtn.disabled = true
  registerBtn.textContent = '注册中...'
  
  try {
    const res = await api.register(username, password)
    if (res.success) {
      loginForm.style.display = 'block'
      registerForm.style.display = 'none'
      document.getElementById('loginUsername').value = username
      showError(loginError, '注册成功，请登录')
    } else {
      showError(regError, res.message || '注册失败')
    }
    registerBtn.textContent = '注 册'
    registerBtn.disabled = false
  } catch (err) {
    showError(regError, err.message || '注册失败')
    registerBtn.disabled = false
    registerBtn.textContent = '注 册'
  }
})

// 检查登录状态并显示/隐藏覆盖层
function checkLoginState() {
  if (isLoggedIn()) {
    loginOverlay.style.display = 'none'
  } else {
    loginOverlay.style.display = 'flex'
  }
}

// 在页面加载时检查登录状态
checkLoginState()

// ========== DOM 引用 ==========
const DOM = {
  pageTitle: document.getElementById('pageTitle'),
  pageUrl: document.getElementById('pageUrl'),
  detectText: document.getElementById('detectText'),
  charCount: document.getElementById('charCount'),
  detectBtn: document.getElementById('detectBtn'),
  loadingSection: document.getElementById('loadingSection'),
  resultSection: document.getElementById('resultSection'),
  errorSection: document.getElementById('errorSection'),
  resultTime: document.getElementById('resultTime'),
  riskBadge: document.getElementById('riskBadge'),
  riskDesc: document.getElementById('riskDesc'),
  fraudType: document.getElementById('fraudType'),
  confidence: document.getElementById('confidence'),
  suggestion: document.getElementById('suggestion'),
  errorText: document.getElementById('errorText'),
  retryBtn: document.getElementById('retryBtn'),
  historyBtn: document.getElementById('historyBtn'),
  settingsBtn: document.getElementById('settingsBtn')
};

// ========== 常量 ==========
const API_BASE_URL = 'http://localhost:8123';
const MAX_TEXT_LENGTH = 5000;
const RISK_COLORS = {
  'LOW': '#67C23A',
  'MEDIUM': '#E6A23C',
  'HIGH': '#F56C6C',
  'CRITICAL': '#F56C6C',
  'UNKNOWN': '#909399'
};
const RISK_TEXTS = {
  'LOW': '低风险',
  'MEDIUM': '中风险',
  'HIGH': '高风险',
  'CRITICAL': '极高风险',
  'UNKNOWN': '未知'
};
const RISK_DESCS = {
  'LOW': '此内容看起来安全，未发现明显诈骗特征',
  'MEDIUM': '此内容存在可疑特征，请保持警惕',
  'HIGH': '此内容具有明显的诈骗特征，请务必小心',
  'CRITICAL': '此内容为高度疑似诈骗信息，请立即停止操作',
  'UNKNOWN': '无法确定风险等级'
};

// ========== 工具函数 ==========

/**
 * HTML 转义
 * @param {string} text
 * @returns {string}
 */
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * 获取当前时间字符串
 * @returns {string}
 */
function getCurrentTime() {
  return new Date().toLocaleString('zh-CN', { hour12: false });
}

/**
 * 获取风险等级颜色
 * @param {string} level
 * @returns {string}
 */
function getRiskColor(level) {
  return RISK_COLORS[level] || RISK_COLORS.UNKNOWN;
}

/**
 * 获取风险等级文本
 * @param {string} level
 * @returns {string}
 */
function getRiskText(level) {
  return RISK_TEXTS[level] || RISK_TEXTS.UNKNOWN;
}

/**
 * 获取风险等级描述
 * @param {string} level
 * @returns {string}
 */
function getRiskDesc(level) {
  return RISK_DESCS[level] || RISK_DESCS.UNKNOWN;
}

// ========== 页面状态管理 ==========

/**
 * 显示指定区域，隐藏其他区域
 * @param {string} section - 要显示的区域 ('result', 'loading', 'error', 'none')
 */
function showSection(section) {
  DOM.resultSection.style.display = 'none';
  DOM.loadingSection.style.display = 'none';
  DOM.errorSection.style.display = 'none';

  if (section === 'result') {
    DOM.resultSection.style.display = 'block';
  } else if (section === 'loading') {
    DOM.loadingSection.style.display = 'flex';
  } else if (section === 'error') {
    DOM.errorSection.style.display = 'flex';
  }
}

/**
 * 更新按钮状态
 * @param {boolean} disabled
 */
function setButtonState(disabled) {
  DOM.detectBtn.disabled = disabled;
  if (disabled) {
    DOM.detectBtn.innerHTML = `
      <svg class="detect-btn-icon" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="animation:spin 0.8s linear infinite;">
        <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5" stroke-dasharray="30 10"/>
      </svg>
      检测中...
    `;
  } else {
    DOM.detectBtn.innerHTML = `
      <svg class="detect-btn-icon" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 3V13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M3 8H13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      开始检测
    `;
  }
}

// ========== 核心功能 ==========

/**
 * 获取当前标签页信息
 */
async function getCurrentTabInfo() {
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs && tabs.length > 0) {
      const tab = tabs[0];
      DOM.pageTitle.textContent = tab.title || '未知页面';
      DOM.pageUrl.textContent = tab.url || '未知地址';
    }
  } catch (error) {
    DOM.pageTitle.textContent = '无法获取页面信息';
    DOM.pageUrl.textContent = '无法获取页面信息';
  }
}

/**
 * 调用 API 检测风险
 * @param {string} text - 待检测文本
 * @returns {Promise<object>} 检测结果
 */
async function assessRisk(text) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/risk/assess`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ text: text.trim() }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      throw new Error(`API 请求失败 (${response.status}): ${errorText || response.statusText}`);
    }

    const data = await response.json();

    if (data.code !== 0 && data.code !== undefined) {
      throw new Error(data.message || 'API 返回错误');
    }

    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('请求超时，请检查网络连接后重试');
    }
    throw error;
  }
}

/**
 * 展示检测结果
 * @param {object} result - API 返回的检测结果
 */
function showResult(result) {
  const data = result.data || result;

  const riskLevel = data.risk_level || data.riskLevel || 'UNKNOWN';
  const riskColor = getRiskColor(riskLevel);
  const riskText = getRiskText(riskLevel);
  const riskDesc = getRiskDesc(riskLevel);

  DOM.resultTime.textContent = getCurrentTime();

  DOM.riskBadge.textContent = riskText;
  DOM.riskBadge.style.background = riskColor;

  DOM.riskDesc.textContent = riskDesc;

  DOM.fraudType.textContent = escapeHtml(data.fraud_type || data.fraudType || '未识别');

  if (data.confidence !== undefined && data.confidence !== null) {
    const confidenceValue = typeof data.confidence === 'number'
      ? (data.confidence * 100).toFixed(1) + '%'
      : data.confidence;
    DOM.confidence.textContent = confidenceValue;
  } else {
    DOM.confidence.textContent = '-';
  }

  DOM.suggestion.textContent = data.suggestion || data.suggest || '请保持警惕，不要轻易向陌生人转账或提供个人信息。';

  showSection('result');
}

/**
 * 显示错误信息
 * @param {string} message
 */
function showError(message) {
  DOM.errorText.textContent = message || '检测失败，请稍后重试';
  showSection('error');
}

/**
 * 执行检测
 */
async function performDetection() {
  const text = DOM.detectText.value.trim();

  if (!text) {
    DOM.detectText.focus();
    DOM.detectText.style.borderColor = '#F56C6C';
    DOM.detectText.style.boxShadow = '0 0 0 3px rgba(245, 108, 108, 0.15)';
    setTimeout(() => {
      DOM.detectText.style.borderColor = '';
      DOM.detectText.style.boxShadow = '';
    }, 2000);
    return;
  }

  if (text.length > MAX_TEXT_LENGTH) {
    showError(`文本内容超过 ${MAX_TEXT_LENGTH} 字符限制，请减少后重试`);
    return;
  }

  setButtonState(true);
  showSection('loading');

  try {
    const result = await assessRisk(text);
    showResult(result);

    // 保存检测历史
    try {
      const storageResult = await chrome.storage.local.get(['detectHistory']);
      const history = storageResult.detectHistory || [];
      history.unshift({
        id: Date.now().toString(36) + Math.random().toString(36).substring(2, 7),
        text: text.substring(0, 200) + (text.length > 200 ? '...' : ''),
        result: result,
        source: 'popup',
        timestamp: Date.now(),
        timestampStr: getCurrentTime()
      });
      if (history.length > 100) {
        history.length = 100;
      }
      await chrome.storage.local.set({ detectHistory: history });
    } catch (storageError) {
      console.error('保存历史记录失败:', storageError);
    }
  } catch (error) {
    showError(error.message || '检测失败，请稍后重试');
  } finally {
    setButtonState(false);
  }
}

// ========== 事件绑定 ==========

/**
 * 初始化事件监听
 */
function initEvents() {
  // 开始检测按钮
  DOM.detectBtn.addEventListener('click', performDetection);

  // 重试按钮
  DOM.retryBtn.addEventListener('click', performDetection);

  // 回车键检测（Ctrl+Enter 或 Shift+Enter）
  DOM.detectText.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      performDetection();
    }
  });

  // 字符计数
  DOM.detectText.addEventListener('input', () => {
    const length = DOM.detectText.value.length;
    DOM.charCount.textContent = `${length} / ${MAX_TEXT_LENGTH}`;

    if (length > MAX_TEXT_LENGTH * 0.9) {
      DOM.charCount.style.color = '#F56C6C';
    } else if (length > MAX_TEXT_LENGTH * 0.7) {
      DOM.charCount.style.color = '#E6A23C';
    } else {
      DOM.charCount.style.color = '';
    }
  });

  // 历史记录按钮
  DOM.historyBtn.addEventListener('click', () => {
    chrome.storage.local.get(['detectHistory'], (result) => {
      const history = result.detectHistory || [];
      if (history.length === 0) {
        alert('暂无检测历史记录');
        return;
      }

      const historyText = history.slice(0, 10).map((record, index) => {
        const level = (record.result?.data?.risk_level || record.result?.data?.riskLevel || 'UNKNOWN');
        const levelText = RISK_TEXTS[level] || '未知';
        return `${index + 1}. [${levelText}] ${record.timestampStr || '未知时间'}\n   ${record.text || '无内容'}`;
      }).join('\n\n');

      alert(`最近检测记录 (共 ${history.length} 条):\n\n${historyText}`);
    });
  });

  // 退出登录按钮
  document.getElementById('logoutBtn').addEventListener('click', () => {
    clearAuth()
    checkLoginState()
    // 清空输入框
    document.getElementById('loginUsername').value = ''
    document.getElementById('loginPassword').value = ''
  })

  // 设置按钮
  DOM.settingsBtn.addEventListener('click', () => {
    alert(
      '反诈卫士 v1.0.0\n\n' +
      'API 地址: http://localhost:8123\n\n' +
      '功能说明:\n' +
      '1. 在 popup 中输入文本检测\n' +
      '2. 选中文本后右键菜单检测\n' +
      '3. 自动扫描页面可疑关键词\n\n' +
      '提示: 使用 Ctrl+Enter 快速检测'
    );
  });
}

// ========== 初始化 ==========

/**
 * 启动 popup
 */
async function init() {
  await getCurrentTabInfo();
  initEvents();

  // 自动聚焦到输入框
  DOM.detectText.focus();

  console.log('反诈卫士 popup 已加载');
}

// 页面加载完成后启动
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
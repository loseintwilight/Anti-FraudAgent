/**
 * 反诈卫士 - Service Worker 后台脚本
 * 负责右键菜单管理、API 调用、消息转发
 */

const API_BASE_URL = 'http://localhost:8123';
const CONTEXT_MENU_ID = 'detectFraudRisk';
const DEFAULT_TIMEOUT = 30000;

// ========== 工具函数 ==========

/**
 * 延迟函数
 * @param {number} ms - 毫秒
 * @returns {Promise<void>}
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 获取当前时间戳字符串
 * @returns {string}
 */
function getTimestamp() {
  return new Date().toLocaleString('zh-CN', { hour12: false });
}

/**
 * 调用 API 检测风险
 * @param {string} text - 待检测文本
 * @returns {Promise<object>} 检测结果
 */
async function assessRisk(text) {
  if (!text || text.trim().length === 0) {
    throw new Error('检测文本不能为空');
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

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
      throw new Error('请求超时，请稍后重试');
    }
    throw error;
  }
}

/**
 * 保存检测记录到存储
 * @param {object} record - 检测记录
 * @returns {Promise<void>}
 */
async function saveToHistory(record) {
  const result = await chrome.storage.local.get(['detectHistory']);
  const history = result.detectHistory || [];
  history.unshift({
    ...record,
    id: Date.now().toString(36) + Math.random().toString(36).substring(2, 7),
    timestamp: Date.now(),
    timestampStr: getTimestamp()
  });
  if (history.length > 100) {
    history.length = 100;
  }
  await chrome.storage.local.set({ detectHistory: history });
}

// ========== 右键菜单管理 ==========

/**
 * 创建或更新右键菜单
 */
function createContextMenu() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: CONTEXT_MENU_ID,
      title: '检测诈骗风险',
      contexts: ['selection']
    }, () => {
      if (chrome.runtime.lastError) {
        console.error('创建右键菜单失败:', chrome.runtime.lastError.message);
      }
    });
  });
}

// ========== 消息处理 ==========

/**
 * 处理来自 popup 或 content script 的消息
 */
function handleMessage(message, sender, sendResponse) {
  switch (message.type) {
    case 'ASSESS_RISK':
      assessRisk(message.text)
        .then(result => {
          const record = {
            text: message.text,
            result: result,
            source: message.source || 'popup'
          };
          saveToHistory(record).catch(err => {
            console.error('保存历史记录失败:', err);
          });
          sendResponse({ success: true, data: result });
        })
        .catch(error => {
          sendResponse({ success: false, error: error.message });
        });
      return true;

    case 'GET_HISTORY':
      chrome.storage.local.get(['detectHistory'], (result) => {
        sendResponse({ success: true, data: result.detectHistory || [] });
      });
      return true;

    case 'CLEAR_HISTORY':
      chrome.storage.local.remove('detectHistory', () => {
        sendResponse({ success: true });
      });
      return true;

    case 'GET_TAB_INFO':
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs && tabs.length > 0) {
          sendResponse({
            success: true,
            data: {
              url: tabs[0].url || '',
              title: tabs[0].title || ''
            }
          });
        } else {
          sendResponse({ success: false, error: '无法获取当前标签页信息' });
        }
      });
      return true;

    default:
      sendResponse({ success: false, error: `未知消息类型: ${message.type}` });
      return false;
  }
}

// ========== 事件监听 ==========

// 插件安装或更新时触发
chrome.runtime.onInstalled.addListener((details) => {
  createContextMenu();
  console.log(`反诈卫士 v1.0.0 已${details.reason === 'install' ? '安装' : '更新'}`);
});

// 浏览器启动时确保菜单存在
chrome.runtime.onStartup.addListener(() => {
  createContextMenu();
});

// 右键菜单点击事件
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === CONTEXT_MENU_ID && info.selectionText) {
    const selectedText = info.selectionText.trim();

    // 限制选中文本长度
    if (selectedText.length > 5000) {
      chrome.tabs.sendMessage(tab.id, {
        type: 'SHOW_NOTIFICATION',
        data: {
          level: 'error',
          message: '选中文本过长（超过5000字符），请减少选中内容后重试'
        }
      }).catch(() => {});
      return;
    }

    // 显示加载状态
    chrome.tabs.sendMessage(tab.id, {
      type: 'SHOW_NOTIFICATION',
      data: {
        level: 'loading',
        message: '正在检测诈骗风险...'
      }
    }).catch(() => {});

    // 调用 API 检测
    assessRisk(selectedText)
      .then(result => {
        const record = {
          text: selectedText,
          result: result,
          source: 'contextMenu'
        };
        saveToHistory(record).catch(err => {
          console.error('保存历史记录失败:', err);
        });

        // 通知 content script 显示结果
        chrome.tabs.sendMessage(tab.id, {
          type: 'SHOW_DETECT_RESULT',
          data: result,
          selectedText: selectedText
        }).catch(() => {});
      })
      .catch(error => {
        chrome.tabs.sendMessage(tab.id, {
          type: 'SHOW_NOTIFICATION',
          data: {
            level: 'error',
            message: '检测失败: ' + error.message
          }
        }).catch(() => {});
      });
  }
});

// 消息监听
chrome.runtime.onMessage.addListener(handleMessage);

// ========== 扩展信息 ==========
console.log('反诈卫士 Service Worker 已启动');
console.log(`版本: 1.0.0`);
console.log(`API 地址: ${API_BASE_URL}`);
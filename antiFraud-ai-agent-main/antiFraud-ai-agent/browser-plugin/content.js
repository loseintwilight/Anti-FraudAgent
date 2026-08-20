/**
 * 反诈卫士 - 内容脚本
 * 负责页面内风险文本高亮、浮动通知显示、可疑关键词扫描
 */

// ========== 配置 ==========

const FRAUD_KEYWORDS = [
  '转账', '安全账户', '刷单', '解冻', '保证金', '手续费',
  '验证码', '银行卡号', '密码', '身份证号', '裸聊', '投资理财',
  '稳赚不赔', '高收益', '日结', '月入过万', '提现', '充值',
  '客服', '退款', '理赔', '双倍返还', '兼职', '刷信誉',
  '虚拟货币', '比特币', 'USDT', '泰达币', '挖矿', '区块链',
  '贷款', '无抵押', '秒到账', '征信', '洗白', '代办信用卡',
  '校园贷', '套路贷', '杀猪盘', '冒充公检法', '通缉令',
  '冻结令', '资金清查', '安全审查', '屏幕共享', '远程控制',
  '刷流水', '包装流水', '跑分', '水房', '车手', '卡农',
  '注销账户', '影响征信', '关闭服务', '自动扣费', '会员续费',
  '保证金认证', '解冻金', '提现通道', '风控拦截', '异常登录',
  '海外代购', '走私', '违禁品', '博彩', '赌博', '六合彩',
  '时时彩', '一分快三', '幸运飞艇', '澳洲幸运5', '大发彩票',
  '导师带单', '内幕消息', '涨停板', '建仓', '拉升',
  '出货', '庄家', '主力资金', '配资', '杠杆', '股指期货',
  '原始股', '股权众筹', '数字货币', 'NFT', '元宇宙投资',
  '跨境电商', '无货源', '代运营', '一件代发', '店群',
  '僵尸粉', '刷粉', '刷赞', '刷播放', '数据优化',
  '恶意软件', '病毒', '木马', '勒索', '蠕虫', '钓鱼链接',
  '中奖', '大奖', '免费领取', '幸运用户', '系统随机抽取',
  '点击链接', '扫描二维码', '下载APP', '安装包', 'apk',
  '共享屏幕', '远程协助', 'TeamViewer', 'AnyDesk', '向日葵',
  '会议号', '加入会议', '屏幕录制', '录屏', '偷拍',
  '裸贷', '肉偿', '卖淫', '招嫖', '约炮', '一夜情',
  '代孕', '捐卵', '捐精', '卖血', '器官',
  '作弊', '代考', '替考', '答案', '包过', '改分',
  '黑客', '破解', '入侵', '盗号', '找回密码',
  '灰色项目', '偏门', '捞偏门', '空手套白狼', '暴利项目'
];

const STYLE_ID = 'antiFraudGuardStyle';
const NOTIFICATION_CLASS = 'antiFraudGuardNotification';
const HIGHLIGHT_CLASS = 'antiFraudGuardHighlight';
const RISK_BADGE_CLASS = 'antiFraudGuardBadge';

// ========== 样式注入 ==========

/**
 * 注入自定义样式
 */
function injectStyles() {
  if (document.getElementById(STYLE_ID)) {
    return;
  }

  const style = document.createElement('style');
  style.id = STYLE_ID;
  style.textContent = `
    .${HIGHLIGHT_CLASS} {
      outline: 3px solid #F56C6C !important;
      outline-offset: 2px !important;
      background-color: rgba(245, 108, 108, 0.15) !important;
      border-radius: 2px !important;
      cursor: pointer !important;
      position: relative !important;
      transition: background-color 0.3s ease !important;
    }

    .${HIGHLIGHT_CLASS}:hover {
      background-color: rgba(245, 108, 108, 0.3) !important;
    }

    .${RISK_BADGE_CLASS} {
      display: inline-block !important;
      font-size: 11px !important;
      line-height: 1 !important;
      padding: 2px 6px !important;
      margin-left: 4px !important;
      border-radius: 3px !important;
      font-weight: bold !important;
      color: #fff !important;
      background-color: #F56C6C !important;
      vertical-align: middle !important;
      cursor: pointer !important;
      user-select: none !important;
    }

    .${RISK_BADGE_CLASS}:hover {
      opacity: 0.85 !important;
    }

    .${NOTIFICATION_CLASS} {
      position: fixed !important;
      bottom: 24px !important;
      right: 24px !important;
      z-index: 2147483647 !important;
      min-width: 320px !important;
      max-width: 420px !important;
      background: #ffffff !important;
      border-radius: 12px !important;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
      font-size: 14px !important;
      color: #333 !important;
      line-height: 1.5 !important;
      overflow: hidden !important;
      animation: ${NOTIFICATION_CLASS}SlideIn 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
      border: 1px solid rgba(0, 0, 0, 0.08) !important;
    }

    @keyframes ${NOTIFICATION_CLASS}SlideIn {
      from {
        transform: translateX(120%) scale(0.9);
        opacity: 0;
      }
      to {
        transform: translateX(0) scale(1);
        opacity: 1;
      }
    }

    .${NOTIFICATION_CLASS}-header {
      display: flex !important;
      align-items: center !important;
      padding: 14px 16px !important;
      border-bottom: 1px solid #f0f0f0 !important;
      gap: 8px !important;
    }

    .${NOTIFICATION_CLASS}-header-icon {
      width: 24px !important;
      height: 24px !important;
      flex-shrink: 0 !important;
    }

    .${NOTIFICATION_CLASS}-header-title {
      font-size: 15px !important;
      font-weight: 600 !important;
      color: #1a1a1a !important;
      flex: 1 !important;
    }

    .${NOTIFICATION_CLASS}-header-close {
      width: 24px !important;
      height: 24px !important;
      border: none !important;
      background: none !important;
      cursor: pointer !important;
      font-size: 18px !important;
      color: #999 !important;
      padding: 0 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      border-radius: 4px !important;
    }

    .${NOTIFICATION_CLASS}-header-close:hover {
      background: #f5f5f5 !important;
      color: #333 !important;
    }

    .${NOTIFICATION_CLASS}-body {
      padding: 14px 16px !important;
    }

    .${NOTIFICATION_CLASS}-risk-level {
      display: flex !important;
      align-items: center !important;
      margin-bottom: 10px !important;
      gap: 8px !important;
    }

    .${NOTIFICATION_CLASS}-risk-badge {
      display: inline-block !important;
      padding: 3px 12px !important;
      border-radius: 12px !important;
      font-size: 12px !important;
      font-weight: 600 !important;
      color: #fff !important;
    }

    .${NOTIFICATION_CLASS}-risk-label {
      font-size: 13px !important;
      color: #666 !important;
    }

    .${NOTIFICATION_CLASS}-detail-row {
      display: flex !important;
      margin-bottom: 6px !important;
      font-size: 13px !important;
    }

    .${NOTIFICATION_CLASS}-detail-label {
      color: #999 !important;
      width: 70px !important;
      flex-shrink: 0 !important;
    }

    .${NOTIFICATION_CLASS}-detail-value {
      color: #333 !important;
      flex: 1 !important;
      word-break: break-word !important;
    }

    .${NOTIFICATION_CLASS}-suggestion {
      margin-top: 10px !important;
      padding: 10px 12px !important;
      background: #f0f9ff !important;
      border-radius: 8px !important;
      font-size: 13px !important;
      color: #409EFF !important;
      border-left: 3px solid #409EFF !important;
    }

    .${NOTIFICATION_CLASS}-loading {
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      padding: 20px !important;
      gap: 10px !important;
    }

    .${NOTIFICATION_CLASS}-spinner {
      width: 20px !important;
      height: 20px !important;
      border: 2px solid #e0e0e0 !important;
      border-top: 2px solid #409EFF !important;
      border-radius: 50% !important;
      animation: ${NOTIFICATION_CLASS}Spin 0.8s linear infinite !important;
    }

    @keyframes ${NOTIFICATION_CLASS}Spin {
      to { transform: rotate(360deg); }
    }

    .${NOTIFICATION_CLASS}-error {
      padding: 16px !important;
      text-align: center !important;
      color: #F56C6C !important;
    }

    .${NOTIFICATION_CLASS}-error-icon {
      font-size: 32px !important;
      margin-bottom: 8px !important;
    }

    @media (prefers-reduced-motion: reduce) {
      .${NOTIFICATION_CLASS} {
        animation: none !important;
      }
    }
  `;
  document.head.appendChild(style);
}

// ========== 浮动通知 ==========

/**
 * 创建浮动通知元素
 * @returns {HTMLElement}
 */
function createNotificationContainer() {
  let container = document.querySelector(`.${NOTIFICATION_CLASS}`);
  if (container) {
    container.remove();
  }

  container = document.createElement('div');
  container.className = NOTIFICATION_CLASS;
  document.body.appendChild(container);
  return container;
}

/**
 * 移除浮动通知
 */
function removeNotification() {
  const container = document.querySelector(`.${NOTIFICATION_CLASS}`);
  if (container) {
    container.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
    container.style.transform = 'translateX(120%)';
    container.style.opacity = '0';
    setTimeout(() => {
      if (container.parentNode) {
        container.parentNode.removeChild(container);
      }
    }, 300);
  }
}

/**
 * 显示加载中通知
 * @param {string} message
 */
function showLoadingNotification(message) {
  const container = createNotificationContainer();
  container.innerHTML = `
    <div class="${NOTIFICATION_CLASS}-loading">
      <div class="${NOTIFICATION_CLASS}-spinner"></div>
      <span style="color:#666;font-size:14px;">${escapeHtml(message)}</span>
    </div>
  `;
}

/**
 * 显示错误通知
 * @param {string} message
 */
function showErrorNotification(message) {
  const container = createNotificationContainer();
  container.innerHTML = `
    <div class="${NOTIFICATION_CLASS}-error">
      <div class="${NOTIFICATION_CLASS}-error-icon">⚠️</div>
      <div>${escapeHtml(message)}</div>
    </div>
  `;
  autoHideNotification(5000);
}

/**
 * 显示检测结果通知
 * @param {object} result - API 返回的检测结果
 */
function showDetectResultNotification(result) {
  const container = createNotificationContainer();

  const riskInfo = extractRiskInfo(result);
  const riskColor = getRiskColor(riskInfo.level);
  const riskText = getRiskLevelText(riskInfo.level);

  container.innerHTML = `
    <div class="${NOTIFICATION_CLASS}-header" style="background:${riskColor}08;">
      <svg class="${NOTIFICATION_CLASS}-header-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 3L20 7.5V12.5C20 17.3 16.5 21.7 12 23C7.5 21.7 4 17.3 4 12.5V7.5L12 3Z" fill="${riskColor}" stroke="${riskColor}" stroke-width="1.5"/>
        <path d="M12 8V13" stroke="white" stroke-width="2" stroke-linecap="round"/>
        <circle cx="12" cy="16" r="1" fill="white"/>
      </svg>
      <span class="${NOTIFICATION_CLASS}-header-title">检测结果</span>
      <button class="${NOTIFICATION_CLASS}-header-close" onclick="(function(){var e=document.querySelector('.${NOTIFICATION_CLASS}');if(e)e.remove();})()">✕</button>
    </div>
    <div class="${NOTIFICATION_CLASS}-body">
      <div class="${NOTIFICATION_CLASS}-risk-level">
        <span class="${NOTIFICATION_CLASS}-risk-badge" style="background:${riskColor};">${riskText}</span>
        <span class="${NOTIFICATION_CLASS}-risk-label">${riskInfo.level === 'LOW' ? '此内容看起来安全' : '请注意风险'}</span>
      </div>
      <div class="${NOTIFICATION_CLASS}-detail-row">
        <span class="${NOTIFICATION_CLASS}-detail-label">诈骗类型</span>
        <span class="${NOTIFICATION_CLASS}-detail-value">${escapeHtml(riskInfo.fraudType || '未识别')}</span>
      </div>
      <div class="${NOTIFICATION_CLASS}-detail-row">
        <span class="${NOTIFICATION_CLASS}-detail-label">置信度</span>
        <span class="${NOTIFICATION_CLASS}-detail-value">${riskInfo.confidence || '-'}</span>
      </div>
      <div class="${NOTIFICATION_CLASS}-suggestion">
        ${escapeHtml(riskInfo.suggestion || '请保持警惕，不要轻易向陌生人转账或提供个人信息。')}
      </div>
    </div>
  `;

  autoHideNotification(5000);
}

/**
 * 自动隐藏通知
 * @param {number} delay - 延迟毫秒数
 */
function autoHideNotification(delay) {
  setTimeout(() => {
    removeNotification();
  }, delay);
}

// ========== 风险等级工具 ==========

/**
 * 获取风险等级颜色
 * @param {string} level - 风险等级
 * @returns {string} 颜色值
 */
function getRiskColor(level) {
  const colorMap = {
    'LOW': '#67C23A',
    'MEDIUM': '#E6A23C',
    'HIGH': '#F56C6C',
    'CRITICAL': '#F56C6C',
    'UNKNOWN': '#909399'
  };
  return colorMap[level] || '#909399';
}

/**
 * 获取风险等级中文文本
 * @param {string} level - 风险等级
 * @returns {string} 中文文本
 */
function getRiskLevelText(level) {
  const textMap = {
    'LOW': '低风险',
    'MEDIUM': '中风险',
    'HIGH': '高风险',
    'CRITICAL': '极高风险',
    'UNKNOWN': '未知'
  };
  return textMap[level] || '未知';
}

/**
 * 从 API 响应中提取风险信息
 * @param {object} result - API 响应数据
 * @returns {object} 风险信息
 */
function extractRiskInfo(result) {
  const data = result.data || result;

  return {
    level: data.risk_level || data.riskLevel || 'UNKNOWN',
    fraudType: data.fraud_type || data.fraudType || '未识别',
    confidence: data.confidence ? `${(data.confidence * 100).toFixed(1)}%` : '-',
    suggestion: data.suggestion || data.suggest || '请保持警惕，不要轻易向陌生人转账或提供个人信息。'
  };
}

// ========== HTML 转义 ==========

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

// ========== 文本高亮 ==========

/**
 * 高亮页面中的文本
 * @param {string} text - 要高亮的文本
 */
function highlightText(text) {
  if (!text) return;

  const cleanedText = text.trim();
  if (cleanedText.length < 2) return;

  clearHighlights();

  const treeWalker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: function(node) {
        if (!node.textContent || node.textContent.trim().length === 0) {
          return NodeFilter.FILTER_REJECT;
        }
        const parent = node.parentElement;
        if (!parent || parent.closest(`.${NOTIFICATION_CLASS}`) ||
            parent.closest(`.${HIGHLIGHT_CLASS}`) ||
            parent.closest('script') ||
            parent.closest('style') ||
            parent.closest('noscript') ||
            parent.closest('iframe') ||
            parent.closest('svg') ||
            parent.closest('[contenteditable="false"]')) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    },
    false
  );

  const nodesToReplace = [];
  let node;
  while ((node = treeWalker.nextNode()) !== null) {
    if (node.textContent.includes(cleanedText)) {
      nodesToReplace.push(node);
    }
  }

  for (const textNode of nodesToReplace) {
    const parent = textNode.parentElement;
    if (!parent) continue;

    const text = textNode.textContent;
    const index = text.indexOf(cleanedText);
    if (index === -1) continue;

    const fragment = document.createDocumentFragment();

    if (index > 0) {
      fragment.appendChild(document.createTextNode(text.substring(0, index)));
    }

    const mark = document.createElement('mark');
    mark.className = HIGHLIGHT_CLASS;
    mark.textContent = cleanedText;
    mark.title = '反诈卫士: 疑似诈骗内容';
    mark.addEventListener('click', function() {
      this.style.outline = '3px solid #E6A23C';
      setTimeout(() => {
        this.style.outline = '3px solid #F56C6C';
      }, 1500);
    });

    const badge = document.createElement('span');
    badge.className = RISK_BADGE_CLASS;
    badge.textContent = '风险';
    badge.addEventListener('click', function(e) {
      e.stopPropagation();
      this.textContent = this.textContent === '风险' ? '已标记' : '风险';
    });

    fragment.appendChild(mark);
    fragment.appendChild(badge);

    if (index + cleanedText.length < text.length) {
      fragment.appendChild(document.createTextNode(text.substring(index + cleanedText.length)));
    }

    parent.replaceChild(fragment, textNode);
  }
}

/**
 * 清除所有高亮标记
 */
function clearHighlights() {
  const highlights = document.querySelectorAll(`.${HIGHLIGHT_CLASS}`);
  highlights.forEach(el => {
    const parent = el.parentNode;
    if (parent) {
      const textNode = document.createTextNode(el.textContent);
      parent.replaceChild(textNode, el);
      parent.normalize();
    }
  });

  const badges = document.querySelectorAll(`.${RISK_BADGE_CLASS}`);
  badges.forEach(el => el.remove());
}

// ========== 可疑关键词扫描 ==========

/**
 * 扫描页面中的可疑关键词并进行标记
 */
function scanFraudKeywords() {
  const foundKeywords = [];

  const treeWalker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: function(node) {
        if (!node.textContent || node.textContent.trim().length === 0) {
          return NodeFilter.FILTER_REJECT;
        }
        const parent = node.parentElement;
        if (!parent || parent.closest(`.${NOTIFICATION_CLASS}`) ||
            parent.closest(`.${HIGHLIGHT_CLASS}`) ||
            parent.closest('script') ||
            parent.closest('style') ||
            parent.closest('noscript') ||
            parent.closest('iframe') ||
            parent.closest('svg')) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    },
    false
  );

  const nodesToProcess = [];
  let node;
  while ((node = treeWalker.nextNode()) !== null) {
    nodesToProcess.push(node);
  }

  for (const textNode of nodesToProcess) {
    const text = textNode.textContent;
    let hasMatch = false;

    for (const keyword of FRAUD_KEYWORDS) {
      if (text.includes(keyword)) {
        hasMatch = true;
        if (!foundKeywords.includes(keyword)) {
          foundKeywords.push(keyword);
        }
      }
    }

    if (!hasMatch) continue;

    const parent = textNode.parentElement;
    if (!parent) continue;

    const fragment = document.createDocumentFragment();
    let remainingText = text;

    while (remainingText.length > 0) {
      let earliestIndex = -1;
      let earliestKeyword = '';

      for (const keyword of FRAUD_KEYWORDS) {
        const idx = remainingText.indexOf(keyword);
        if (idx !== -1 && (earliestIndex === -1 || idx < earliestIndex)) {
          earliestIndex = idx;
          earliestKeyword = keyword;
        }
      }

      if (earliestIndex === -1) {
        fragment.appendChild(document.createTextNode(remainingText));
        break;
      }

      if (earliestIndex > 0) {
        fragment.appendChild(document.createTextNode(remainingText.substring(0, earliestIndex)));
      }

      const mark = document.createElement('mark');
      mark.className = HIGHLIGHT_CLASS;
      mark.textContent = earliestKeyword;
      mark.title = '反诈卫士: 可疑关键词';

      const badge = document.createElement('span');
      badge.className = RISK_BADGE_CLASS;
      badge.textContent = '可疑';

      fragment.appendChild(mark);
      fragment.appendChild(badge);

      remainingText = remainingText.substring(earliestIndex + earliestKeyword.length);
    }

    parent.replaceChild(fragment, textNode);
  }

  return foundKeywords;
}

// ========== 消息处理 ==========

/**
 * 处理来自 background script 的消息
 */
function handleRuntimeMessage(message, sender, sendResponse) {
  switch (message.type) {
    case 'SHOW_NOTIFICATION':
      if (message.data.level === 'loading') {
        showLoadingNotification(message.data.message || '正在检测...');
      } else if (message.data.level === 'error') {
        showErrorNotification(message.data.message || '检测失败');
      }
      sendResponse({ success: true });
      break;

    case 'SHOW_DETECT_RESULT':
      showDetectResultNotification(message.data);
      if (message.selectedText) {
        highlightText(message.selectedText);
      }
      sendResponse({ success: true });
      break;

    case 'SCAN_KEYWORDS':
      const found = scanFraudKeywords();
      sendResponse({ success: true, data: found });
      break;

    case 'CLEAR_HIGHLIGHTS':
      clearHighlights();
      sendResponse({ success: true });
      break;

    default:
      sendResponse({ success: false, error: '未知消息类型' });
      break;
  }
}

// ========== 初始化 ==========

/**
 * 初始化内容脚本
 */
function init() {
  injectStyles();

  // 监听来自 background 的消息
  chrome.runtime.onMessage.addListener(handleRuntimeMessage);

  // 页面加载完成后自动扫描可疑关键词
  if (document.readyState === 'complete') {
    scanFraudKeywords();
  } else {
    window.addEventListener('load', function autoScan() {
      scanFraudKeywords();
      window.removeEventListener('load', autoScan);
    });
  }

  // 监听 DOM 变化，动态扫描新加载的内容
  let scanTimer = null;
  const observer = new MutationObserver(() => {
    if (scanTimer) {
      clearTimeout(scanTimer);
    }
    scanTimer = setTimeout(() => {
      scanFraudKeywords();
    }, 2000);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  console.log('反诈卫士内容脚本已加载');
}

// 启动
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
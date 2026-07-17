"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
if (!Math) {
  (RiskBadge + ChatInput)();
}
const ChatInput = () => "../../components/chat-input/chat-input.js";
const RiskBadge = () => "../../components/risk-badge/risk-badge.js";
const _sfc_main = {
  __name: "index",
  setup(__props) {
    const messages = common_vendor.ref([]);
    const isLoading = common_vendor.ref(false);
    const lastResult = common_vendor.ref(null);
    const scrollTop = common_vendor.ref(0);
    function setScrollViewRef(el) {
    }
    function scrollToBottom() {
      common_vendor.nextTick$1(() => {
        scrollTop.value = 999999;
      });
    }
    function getScoreColor(score) {
      if (score >= 80)
        return "#F56C6C";
      if (score >= 60)
        return "#E6A23C";
      if (score >= 30)
        return "#67C23A";
      return "#909399";
    }
    async function handleSubmit(text) {
      messages.value.push({
        role: "user",
        content: text
      });
      scrollToBottom();
      isLoading.value = true;
      try {
        const res = await api_index.assessRisk(text);
        const result = res.data || res;
        lastResult.value = result;
        messages.value.push({
          role: "ai",
          result
        });
        scrollToBottom();
      } catch (err) {
        messages.value.push({
          role: "ai",
          result: {
            riskLevel: "UNKNOWN",
            score: 0,
            fraudType: "检测失败",
            suggestion: "检测服务暂时不可用，请稍后重试。",
            keywords: []
          }
        });
        scrollToBottom();
      } finally {
        isLoading.value = false;
      }
    }
    function goToReport(reportId) {
      if (!reportId)
        return;
      common_vendor.index.navigateTo({
        url: `/pages/report/index?reportId=${reportId}`
      });
    }
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: lastResult.value
      }, lastResult.value ? {
        b: common_vendor.p({
          level: lastResult.value.riskLevel
        })
      } : {}, {
        c: messages.value.length === 0
      }, messages.value.length === 0 ? {} : {}, {
        d: common_vendor.f(messages.value, (msg, index, i0) => {
          return common_vendor.e({
            a: msg.role === "user"
          }, msg.role === "user" ? {
            b: common_vendor.t(msg.content)
          } : common_vendor.e({
            c: "1cf27b2a-1-" + i0,
            d: common_vendor.p({
              level: msg.result.riskLevel
            }),
            e: msg.result.fraudType
          }, msg.result.fraudType ? {
            f: common_vendor.t(msg.result.fraudType)
          } : {}, {
            g: common_vendor.t(msg.result.score),
            h: getScoreColor(msg.result.score),
            i: msg.result.confidence !== void 0
          }, msg.result.confidence !== void 0 ? {
            j: common_vendor.t((msg.result.confidence * 100).toFixed(0))
          } : {}, {
            k: msg.result.suggestion
          }, msg.result.suggestion ? {
            l: common_vendor.t(msg.result.suggestion)
          } : {}, {
            m: msg.result.keywords && msg.result.keywords.length > 0
          }, msg.result.keywords && msg.result.keywords.length > 0 ? {
            n: common_vendor.f(msg.result.keywords, (kw, ki, i1) => {
              return {
                a: common_vendor.t(kw),
                b: ki
              };
            })
          } : {}, {
            o: common_vendor.o(($event) => goToReport(msg.result.reportId), index)
          }), {
            p: index
          });
        }),
        e: isLoading.value
      }, isLoading.value ? {} : {}, {
        f: scrollTop.value,
        g: common_vendor.o(scrollToBottom),
        h: setScrollViewRef,
        i: common_vendor.o(handleSubmit),
        j: common_vendor.p({
          loading: isLoading.value
        })
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-1cf27b2a"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/index/index.js.map

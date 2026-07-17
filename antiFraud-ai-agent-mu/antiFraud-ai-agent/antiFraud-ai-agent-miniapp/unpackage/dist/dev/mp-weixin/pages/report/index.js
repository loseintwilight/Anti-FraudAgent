"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
if (!Math) {
  RiskBadge();
}
const RiskBadge = () => "../../components/risk-badge/risk-badge.js";
const _sfc_main = {
  __name: "index",
  setup(__props) {
    const report = common_vendor.ref(null);
    const loading = common_vendor.ref(true);
    onLoad(async (options) => {
      const reportId = options.reportId;
      if (!reportId) {
        loading.value = false;
        return;
      }
      try {
        const res = await api_index.getReport(reportId);
        report.value = res.data || res;
      } catch (err) {
        common_vendor.index.showToast({ title: "获取报告失败", icon: "none" });
      } finally {
        loading.value = false;
      }
    });
    function getScoreColor() {
      if (!report.value)
        return "#909399";
      const score = report.value.score;
      if (score >= 80)
        return "#F56C6C";
      if (score >= 60)
        return "#E6A23C";
      if (score >= 30)
        return "#67C23A";
      return "#909399";
    }
    function getOverviewBg() {
      if (!report.value)
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
      const level = report.value.riskLevel;
      switch (level) {
        case "LOW":
          return "linear-gradient(135deg, #67C23A 0%, #95de64 100%)";
        case "MEDIUM":
          return "linear-gradient(135deg, #E6A23C 0%, #f5c542 100%)";
        case "HIGH":
          return "linear-gradient(135deg, #F56C6C 0%, #fa8c8c 100%)";
        case "CRITICAL":
          return "linear-gradient(135deg, #F56C6C 0%, #d9363e 100%)";
        default:
          return "linear-gradient(135deg, #909399 0%, #b0b3b8 100%)";
      }
    }
    function handleReport() {
      common_vendor.index.showModal({
        title: "确认举报",
        content: "您确认要举报此内容为诈骗信息吗？",
        success: (res) => {
          if (res.confirm) {
            common_vendor.index.showToast({ title: "举报成功，感谢您的贡献", icon: "success" });
          }
        }
      });
    }
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: loading.value
      }, loading.value ? {} : report.value ? common_vendor.e({
        c: common_vendor.p({
          level: report.value.riskLevel
        }),
        d: common_vendor.t(report.value.score),
        e: getScoreColor(),
        f: common_vendor.t(report.value.detectTime || report.value.createTime || "--"),
        g: getOverviewBg(),
        h: common_vendor.p({
          level: report.value.riskLevel
        }),
        i: common_vendor.t(report.value.score),
        j: getScoreColor(),
        k: report.value.fraudType
      }, report.value.fraudType ? {
        l: common_vendor.t(report.value.fraudType)
      } : {}, {
        m: common_vendor.t(report.value.detectTime || report.value.createTime || "--"),
        n: report.value.keywords && report.value.keywords.length > 0
      }, report.value.keywords && report.value.keywords.length > 0 ? {
        o: common_vendor.f(report.value.keywords, (kw, index, i0) => {
          return {
            a: common_vendor.t(kw),
            b: index
          };
        })
      } : {}, {
        p: report.value.keywords && report.value.keywords.length > 0
      }, report.value.keywords && report.value.keywords.length > 0 ? {} : {}, {
        q: report.value.suggestion
      }, report.value.suggestion ? {
        r: common_vendor.t(report.value.suggestion)
      } : {}, {
        s: report.value.suggestion && report.value.persuasion
      }, report.value.suggestion && report.value.persuasion ? {} : {}, {
        t: report.value.persuasion
      }, report.value.persuasion ? {
        v: common_vendor.t(report.value.persuasion)
      } : {}, {
        w: common_vendor.o(handleReport)
      }) : {}, {
        b: report.value
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-14542b8b"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/report/index.js.map

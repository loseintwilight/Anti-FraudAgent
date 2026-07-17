"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
if (!Math) {
  RiskBadge();
}
const RiskBadge = () => "../../components/risk-badge/risk-badge.js";
const pageSize = 10;
const _sfc_main = {
  __name: "index",
  setup(__props) {
    const list = common_vendor.ref([]);
    const loading = common_vendor.ref(true);
    const refreshing = common_vendor.ref(false);
    const page = common_vendor.ref(1);
    const hasMore = common_vendor.ref(true);
    onLoad(() => {
      fetchHistory(true);
    });
    async function fetchHistory(reset = false) {
      var _a;
      if (reset) {
        page.value = 1;
        hasMore.value = true;
      }
      if (!hasMore.value && !reset)
        return;
      try {
        const res = await api_index.getHistory(page.value, pageSize);
        const records = ((_a = res.data) == null ? void 0 : _a.records) || res.data || [];
        if (reset) {
          list.value = records;
        } else {
          list.value = [...list.value, ...records];
        }
        hasMore.value = records.length >= pageSize;
        page.value++;
      } catch (err) {
        common_vendor.index.__f__("error", "at pages/history/index.vue:90", "获取历史记录失败:", err);
      } finally {
        loading.value = false;
        refreshing.value = false;
      }
    }
    async function loadMore() {
      if (hasMore.value && !loading.value) {
        await fetchHistory(false);
      }
    }
    async function onRefresh() {
      refreshing.value = true;
      await fetchHistory(true);
    }
    function goToReport(reportId) {
      if (!reportId)
        return;
      common_vendor.index.navigateTo({
        url: `/pages/report/index?reportId=${reportId}`
      });
    }
    function goToIndex() {
      common_vendor.index.switchTab({
        url: "/pages/index/index"
      });
    }
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: loading.value && list.value.length === 0
      }, loading.value && list.value.length === 0 ? {} : list.value.length === 0 ? {
        c: common_vendor.o(goToIndex)
      } : common_vendor.e({
        d: common_vendor.f(list.value, (item, index, i0) => {
          return {
            a: "b37acf1c-0-" + i0,
            b: common_vendor.p({
              level: item.riskLevel
            }),
            c: common_vendor.t(item.detectTime || item.createTime || "--"),
            d: common_vendor.t(item.content || item.summary || "无内容"),
            e: common_vendor.t(item.score || 0),
            f: item.id || index,
            g: common_vendor.o(($event) => goToReport(item.id || item.reportId), item.id || index)
          };
        }),
        e: hasMore.value
      }, hasMore.value ? {} : list.value.length > 0 ? {} : {}, {
        f: list.value.length > 0,
        g: common_vendor.o(loadMore),
        h: refreshing.value,
        i: common_vendor.o(onRefresh)
      }), {
        b: list.value.length === 0
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b37acf1c"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/history/index.js.map

"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "risk-badge",
  props: {
    level: {
      type: String,
      default: "UNKNOWN"
    }
  },
  setup(__props) {
    const props = __props;
    const riskConfig = {
      LOW: { label: "低", color: "#67C23A" },
      MEDIUM: { label: "中", color: "#E6A23C" },
      HIGH: { label: "高", color: "#F56C6C" },
      CRITICAL: { label: "极高", color: "#F56C6C" },
      UNKNOWN: { label: "未知", color: "#909399" }
    };
    const bgColor = common_vendor.computed(() => {
      const config = riskConfig[props.level] || riskConfig.UNKNOWN;
      return config.color;
    });
    const label = common_vendor.computed(() => {
      const config = riskConfig[props.level] || riskConfig.UNKNOWN;
      return config.label;
    });
    return (_ctx, _cache) => {
      return {
        a: common_vendor.t(label.value),
        b: bgColor.value
      };
    };
  }
};
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-c4e1c8db"]]);
wx.createComponent(Component);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/components/risk-badge/risk-badge.js.map

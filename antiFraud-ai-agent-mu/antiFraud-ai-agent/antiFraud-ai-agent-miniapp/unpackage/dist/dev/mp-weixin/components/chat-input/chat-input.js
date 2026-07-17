"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "chat-input",
  props: {
    placeholder: {
      type: String,
      default: "请输入您要检测的内容..."
    },
    maxlength: {
      type: Number,
      default: 2e3
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ["submit"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const content = common_vendor.ref("");
    function handleSubmit() {
      const text = content.value.trim();
      if (!text)
        return;
      if (props.loading)
        return;
      emit("submit", text);
      content.value = "";
    }
    return (_ctx, _cache) => {
      return {
        a: __props.placeholder,
        b: __props.maxlength,
        c: common_vendor.o(handleSubmit),
        d: content.value,
        e: common_vendor.o(($event) => content.value = $event.detail.value),
        f: content.value.trim() ? 1 : "",
        g: common_vendor.o(handleSubmit)
      };
    };
  }
};
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-7713cc3c"]]);
wx.createComponent(Component);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/components/chat-input/chat-input.js.map

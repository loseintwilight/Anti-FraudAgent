"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const _sfc_main = {
  __name: "index",
  setup(__props) {
    const store = common_vendor.useStore();
    const userInfo = common_vendor.ref(null);
    const stats = common_vendor.ref({
      detectionCount: 0,
      highRiskCount: 0,
      safeCount: 0
    });
    const userName = common_vendor.ref("U");
    onShow(async () => {
      await loadUserInfo();
    });
    async function loadUserInfo() {
      const cached = common_vendor.index.getStorageSync("userInfo");
      if (cached) {
        userInfo.value = typeof cached === "string" ? JSON.parse(cached) : cached;
        userName.value = getFirstChar(userInfo.value);
      }
      try {
        const res = await api_index.getUserProfile();
        const data = res.data || res;
        userInfo.value = data;
        store.commit("SET_USER", data);
        common_vendor.index.setStorageSync("userInfo", data);
        userName.value = getFirstChar(data);
        if (data.stats) {
          stats.value = data.stats;
        }
      } catch (err) {
        common_vendor.index.__f__("error", "at pages/profile/index.vue:97", "获取用户信息失败:", err);
      }
    }
    function getFirstChar(user) {
      if (!user)
        return "U";
      const name = user.nickname || user.nickName || "用户";
      return name.charAt(0).toUpperCase();
    }
    function handleEditProfile() {
      common_vendor.index.showToast({ title: "功能开发中", icon: "none" });
    }
    function handleMenuClick(type) {
      const titles = {
        profile: "个人信息",
        about: "关于我们",
        feedback: "意见反馈"
      };
      common_vendor.index.showToast({
        title: `${titles[type] || "功能"}开发中`,
        icon: "none"
      });
    }
    function handleLogout() {
      common_vendor.index.showModal({
        title: "确认退出",
        content: "确定要退出登录吗？",
        success: (res) => {
          if (res.confirm) {
            store.commit("CLEAR_USER");
            common_vendor.index.showToast({ title: "已退出登录", icon: "success" });
          }
        }
      });
    }
    return (_ctx, _cache) => {
      var _a, _b, _c, _d;
      return common_vendor.e({
        a: common_vendor.t(userName.value),
        b: common_vendor.t(((_a = userInfo.value) == null ? void 0 : _a.nickname) || ((_b = userInfo.value) == null ? void 0 : _b.nickName) || "未登录用户"),
        c: (_c = userInfo.value) == null ? void 0 : _c.phone
      }, ((_d = userInfo.value) == null ? void 0 : _d.phone) ? {} : {}, {
        d: common_vendor.o(handleEditProfile),
        e: common_vendor.t(stats.value.detectionCount || 0),
        f: common_vendor.t(stats.value.highRiskCount || 0),
        g: common_vendor.t(stats.value.safeCount || 0),
        h: common_vendor.o(($event) => handleMenuClick("profile")),
        i: common_vendor.o(($event) => handleMenuClick("about")),
        j: common_vendor.o(($event) => handleMenuClick("feedback")),
        k: common_vendor.o(handleLogout)
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-201c0da5"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/profile/index.js.map

"use strict";
const common_vendor = require("../common/vendor.js");
const api_index = require("../api/index.js");
const store = common_vendor.createStore({
  state: {
    userInfo: null,
    token: common_vendor.index.getStorageSync("token") || "",
    historyList: [],
    currentReport: null
  },
  mutations: {
    SET_USER(state, userInfo) {
      state.userInfo = userInfo;
    },
    SET_TOKEN(state, token) {
      state.token = token;
      common_vendor.index.setStorageSync("token", token);
    },
    SET_HISTORY(state, list) {
      state.historyList = list;
    },
    APPEND_HISTORY(state, list) {
      state.historyList = [...state.historyList, ...list];
    },
    SET_REPORT(state, report) {
      state.currentReport = report;
    },
    CLEAR_USER(state) {
      state.userInfo = null;
      state.token = "";
      state.historyList = [];
      state.currentReport = null;
      common_vendor.index.removeStorageSync("token");
      common_vendor.index.removeStorageSync("userInfo");
    }
  },
  actions: {
    // 获取用户信息
    async fetchUserProfile({ commit }) {
      try {
        const res = await api_index.getUserProfile();
        commit("SET_USER", res.data || res);
        common_vendor.index.setStorageSync("userInfo", res.data || res);
        return res;
      } catch (err) {
        common_vendor.index.__f__("error", "at store/index.js:46", "获取用户信息失败:", err);
        throw err;
      }
    },
    // 获取历史记录
    async fetchHistory({ commit }, { page = 1, size = 10 } = {}) {
      var _a;
      try {
        const res = await api_index.getHistory(page, size);
        const list = ((_a = res.data) == null ? void 0 : _a.records) || res.data || [];
        if (page === 1) {
          commit("SET_HISTORY", list);
        } else {
          commit("APPEND_HISTORY", list);
        }
        return res;
      } catch (err) {
        common_vendor.index.__f__("error", "at store/index.js:62", "获取历史记录失败:", err);
        throw err;
      }
    }
  }
});
exports.store = store;
//# sourceMappingURL=../../.sourcemap/mp-weixin/store/index.js.map

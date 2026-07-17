"use strict";
const common_vendor = require("../common/vendor.js");
const BASE_URL = "http://localhost:8123";
function requestInterceptor(config) {
  const token = common_vendor.index.getStorageSync("token");
  if (token) {
    config.header = {
      ...config.header,
      "Authorization": `Bearer ${token}`
    };
  }
  return config;
}
function responseInterceptor(response) {
  const { statusCode, data } = response;
  if (statusCode === 200) {
    return data;
  } else if (statusCode === 401) {
    common_vendor.index.removeStorageSync("token");
    common_vendor.index.removeStorageSync("userInfo");
    common_vendor.index.showToast({ title: "登录已过期，请重新登录", icon: "none" });
    return Promise.reject(new Error("登录已过期"));
  } else {
    common_vendor.index.showToast({
      title: (data == null ? void 0 : data.message) || "请求失败",
      icon: "none"
    });
    return Promise.reject(new Error((data == null ? void 0 : data.message) || "请求失败"));
  }
}
function request(options) {
  const config = requestInterceptor({
    url: `${BASE_URL}${options.url}`,
    method: options.method || "GET",
    data: options.data || {},
    header: {
      "Content-Type": "application/json",
      ...options.header
    }
  });
  return new Promise((resolve, reject) => {
    common_vendor.index.request({
      ...config,
      success: (res) => {
        try {
          const result = responseInterceptor(res);
          resolve(result);
        } catch (err) {
          reject(err);
        }
      },
      fail: (err) => {
        common_vendor.index.showToast({
          title: "网络连接失败，请检查网络",
          icon: "none"
        });
        reject(err);
      }
    });
  });
}
exports.request = request;
//# sourceMappingURL=../../.sourcemap/mp-weixin/utils/request.js.map

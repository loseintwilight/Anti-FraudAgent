"use strict";
const utils_request = require("../utils/request.js");
function assessRisk(text) {
  return utils_request.request({
    url: "/api/v1/risk/assess",
    method: "POST",
    data: { text }
  });
}
function getReport(reportId) {
  return utils_request.request({
    url: `/api/v1/report/${reportId}`,
    method: "GET"
  });
}
function getHistory(page = 1, size = 10) {
  return utils_request.request({
    url: "/api/v1/history",
    method: "GET",
    data: { page, size }
  });
}
function getUserProfile() {
  return utils_request.request({
    url: "/api/v1/user/profile",
    method: "GET"
  });
}
exports.assessRisk = assessRisk;
exports.getHistory = getHistory;
exports.getReport = getReport;
exports.getUserProfile = getUserProfile;
//# sourceMappingURL=../../.sourcemap/mp-weixin/api/index.js.map

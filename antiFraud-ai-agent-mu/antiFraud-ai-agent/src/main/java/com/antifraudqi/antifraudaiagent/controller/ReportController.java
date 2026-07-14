package com.antifraudqi.antifraudaiagent.controller;

import com.antifraudqi.antifraudaiagent.model.entity.ReportRecord;
import com.antifraudqi.antifraudaiagent.service.ReportSubmissionService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 举报上报接口
 * 提供用户举报的提交和历史查询功能
 */
@Slf4j
@RestController
@RequestMapping("/report")
public class ReportController {

    @Resource
    private ReportSubmissionService reportSubmissionService;

    /**
     * 提交举报
     * 请求体包含：userId, reportType, reportContent, screenshotBase64, description
     *
     * @param request 举报请求参数
     * @return 操作结果
     */
    @PostMapping("/submit")
    public Map<String, Object> submitReport(@RequestBody Map<String, Object> request) {
        Map<String, Object> result = new HashMap<>();
        try {
            String userId = (String) request.get("userId");
            if (userId == null || userId.isEmpty()) {
                result.put("success", false);
                result.put("error", "用户ID不能为空");
                return result;
            }

            ReportRecord record = reportSubmissionService.submitReport(userId, request);
            result.put("success", true);
            result.put("data", record);
            result.put("message", "举报提交成功");
        } catch (Exception e) {
            log.error("提交举报失败", e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }

    /**
     * 查询举报历史
     *
     * @param userId 用户ID
     * @return 举报历史列表
     */
    @GetMapping("/history")
    public Map<String, Object> getReportHistory(@RequestParam String userId) {
        Map<String, Object> result = new HashMap<>();
        try {
            List<ReportRecord> records = reportSubmissionService.getReportHistory(userId);
            result.put("success", true);
            result.put("data", records);
            result.put("count", records.size());
        } catch (Exception e) {
            log.error("查询举报历史失败: userId={}", userId, e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }
}

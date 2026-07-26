package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.DetectionHistory;
import com.antifraud.admin.domain.FraudReport;
import com.antifraud.admin.service.IDetectionHistoryService;
import com.antifraud.admin.service.IFraudReportService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * 仪表盘控制器
 */
@RestController
@RequestMapping("/api/v1/dashboard")
@Tag(name = "仪表盘", description = "数据统计概览")
public class DashboardController {

    @Resource
    private IDetectionHistoryService detectionHistoryService;

    @Resource
    private IFraudReportService fraudReportService;

    @GetMapping("/stats")
    @Operation(summary = "数据统计")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult stats() {
        Map<String, Object> stats = new HashMap<>();

        // 检测历史统计
        DetectionHistory queryAll = new DetectionHistory();
        long totalDetections = detectionHistoryService.selectDetectionHistoryList(queryAll).size();
        DetectionHistory highRiskQuery = new DetectionHistory();
        highRiskQuery.setRiskLevel("HIGH");
        long highRiskCount = detectionHistoryService.selectDetectionHistoryList(highRiskQuery).size();

        // 报告统计
        FraudReport reportQuery = new FraudReport();
        long totalReports = fraudReportService.selectFraudReportList(reportQuery).size();

        stats.put("totalDetections", totalDetections);
        stats.put("highRiskCount", highRiskCount);
        stats.put("totalReports", totalReports);

        return AjaxResult.success(stats);
    }

    @GetMapping("/risk-distribution")
    @Operation(summary = "风险等级分布")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult riskDistribution() {
        Map<String, Long> distribution = new HashMap<>();

        String[] levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"};
        for (String level : levels) {
            DetectionHistory query = new DetectionHistory();
            query.setRiskLevel(level);
            distribution.put(level, (long) detectionHistoryService.selectDetectionHistoryList(query).size());
        }

        return AjaxResult.success(distribution);
    }
}
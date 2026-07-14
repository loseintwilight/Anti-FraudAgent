package com.antifraudqi.antifraudaiagent.service;

import com.antifraudqi.antifraudaiagent.model.entity.ReportRecord;
import com.antifraudqi.antifraudaiagent.repository.ReportRecordRepository;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 举报提交服务
 * 处理用户的举报提交和历史查询
 */
@Slf4j
@Service
public class ReportSubmissionService {

    @Resource
    private ReportRecordRepository reportRecordRepository;

    /**
     * 提交举报记录
     *
     * @param userId  用户ID
     * @param request 举报请求参数
     * @return 保存后的举报记录
     */
    public ReportRecord submitReport(String userId, Map<String, Object> request) {
        String reportType = (String) request.getOrDefault("reportType", "");
        String reportContent = (String) request.getOrDefault("reportContent", "");
        String screenshotBase64 = (String) request.getOrDefault("screenshotBase64", "");
        String description = (String) request.getOrDefault("description", "");

        ReportRecord record = ReportRecord.builder()
                .userId(userId)
                .reportType(reportType)
                .reportContent(reportContent)
                .screenshotBase64(screenshotBase64)
                .description(description)
                .status("submitted")
                .build();

        ReportRecord saved = reportRecordRepository.save(record);
        log.info("举报提交成功: userId={}, reportType={}, reportContent={}",
                userId, reportType, reportContent);
        return saved;
    }

    /**
     * 查询用户的举报历史
     *
     * @param userId 用户ID
     * @return 举报记录列表
     */
    public List<ReportRecord> getReportHistory(String userId) {
        List<ReportRecord> records = reportRecordRepository.findByUserId(userId);
        log.info("查询举报历史: userId={}, count={}", userId, records.size());
        return records;
    }
}

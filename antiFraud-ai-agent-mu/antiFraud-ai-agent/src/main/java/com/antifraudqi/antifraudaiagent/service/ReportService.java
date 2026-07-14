package com.antifraudqi.antifraudaiagent.service;

import cn.hutool.core.io.FileUtil;
import com.antifraudqi.antifraudaiagent.constant.FileConstant;
import com.antifraudqi.antifraudaiagent.model.entity.DetectionHistory;
import com.antifraudqi.antifraudaiagent.model.entity.FraudReport;
import com.antifraudqi.antifraudaiagent.repository.DetectionHistoryRepository;
import com.antifraudqi.antifraudaiagent.repository.FraudReportRepository;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.element.Paragraph;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.io.ByteArrayOutputStream;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 报告生成服务
 * 负责生成反诈检测报告，支持 PDF 导出和图片导出
 */
@Slf4j
@Service
public class ReportService {

    @Resource
    private FraudReportRepository fraudReportRepository;

    @Resource
    private DetectionHistoryRepository detectionHistoryRepository;

    @Resource
    private RestTemplate restTemplate;

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    /**
     * 根据检测历史生成反诈报告
     *
     * @param userId      用户ID
     * @param detectionId 检测历史ID
     * @return 生成的报告实体
     */
    public FraudReport generateReport(String userId, Long detectionId) {
        // 查询检测历史
        DetectionHistory history = detectionHistoryRepository.findById(detectionId)
                .orElseThrow(() -> new RuntimeException("检测记录不存在: " + detectionId));

        // 构建报告实体
        String reportId = UUID.randomUUID().toString();
        FraudReport report = FraudReport.builder()
                .reportId(reportId)
                .userId(userId)
                .fraudType(history.getFraudType())
                .riskLevel(history.getRiskLevel())
                .riskScore(history.getRiskScore())
                .riskSources("[]")
                .preventionTips("[]")
                .transferWarning("请勿向陌生账户转账，如有疑问请拨打 96110 咨询。")
                .legalGuidance("如确认遭受诈骗，请立即拨打 110 报警，并保留所有聊天记录、转账凭证等证据。")
                .reportType("自查")
                .rawEvidence("[]")
                .analysisSteps("[]")
                .build();

        FraudReport savedReport = fraudReportRepository.save(report);
        log.info("反诈报告生成成功: reportId={}, userId={}", reportId, userId);
        return savedReport;
    }

    /**
     * 将报告导出为 PDF 文件
     *
     * @param reportId 报告唯一标识
     * @return PDF 文件路径
     */
    public String exportPdf(String reportId) {
        FraudReport report = fraudReportRepository.findByReportId(reportId)
                .orElseThrow(() -> new RuntimeException("报告不存在: " + reportId));

        String fileDir = FileConstant.FILE_SAVE_DIR + "/pdf/report";
        FileUtil.mkdir(fileDir);
        String fileName = "fraud_report_" + reportId + ".pdf";
        String filePath = fileDir + "/" + fileName;

        try (PdfWriter writer = new PdfWriter(filePath);
             PdfDocument pdf = new PdfDocument(writer);
             Document document = new Document(pdf)) {

            document.add(new Paragraph("反诈检测报告").setFontSize(20));
            document.add(new Paragraph("报告编号: " + report.getReportId()));
            document.add(new Paragraph("用户ID: " + report.getUserId()));
            document.add(new Paragraph("诈骗类型: " + report.getFraudType()));
            document.add(new Paragraph("风险等级: " + report.getRiskLevel()));
            document.add(new Paragraph("风险评分: " + report.getRiskScore()));
            document.add(new Paragraph("生成时间: " + report.getCreatedAt()));
            document.add(new Paragraph(""));
            document.add(new Paragraph("转账预警: ").setFontSize(14));
            document.add(new Paragraph(report.getTransferWarning()));
            document.add(new Paragraph(""));
            document.add(new Paragraph("法律指引: ").setFontSize(14));
            document.add(new Paragraph(report.getLegalGuidance()));

            log.info("PDF 报告导出成功: {}", filePath);
            return filePath;
        } catch (Exception e) {
            log.error("PDF 报告导出失败: reportId={}", reportId, e);
            throw new RuntimeException("PDF 导出失败: " + e.getMessage());
        }
    }

    /**
     * 将报告导出为图片（调用 Python 微服务生成）
     *
     * @param reportId 报告唯一标识
     * @return 图片字节数组
     */
    public byte[] exportImage(String reportId) {
        FraudReport report = fraudReportRepository.findByReportId(reportId)
                .orElseThrow(() -> new RuntimeException("报告不存在: " + reportId));

        String url = pythonServiceUrl + "/api/report/generate-image";
        Map<String, Object> request = new HashMap<>();
        request.put("report_id", report.getReportId());
        request.put("fraud_type", report.getFraudType());
        request.put("risk_level", report.getRiskLevel());
        request.put("risk_score", report.getRiskScore());
        request.put("transfer_warning", report.getTransferWarning());
        request.put("legal_guidance", report.getLegalGuidance());
        request.put("created_at", report.getCreatedAt().toString());

        try {
            log.info("调用 Python 微服务生成报告图片: reportId={}", reportId);
            byte[] imageBytes = restTemplate.postForObject(url, request, byte[].class);
            log.info("报告图片生成成功: reportId={}", reportId);
            return imageBytes;
        } catch (Exception e) {
            log.error("调用 Python 微服务生成报告图片失败: reportId={}", reportId, e);
            throw new RuntimeException("图片报告生成失败: " + e.getMessage());
        }
    }
}

package com.antifraudqi.antifraudaiagent.controller;

import com.antifraudqi.antifraudaiagent.service.ReportService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * 报告导出接口
 * 提供反诈报告的 PDF 和图片导出功能
 */
@Slf4j
@RestController
@RequestMapping("/report")
public class ReportExportController {

    @Resource
    private ReportService reportService;

    /**
     * 导出 PDF 格式的反诈报告
     *
     * @param reportId 报告唯一标识
     * @return PDF 文件响应
     */
    @GetMapping("/pdf/{reportId}")
    public ResponseEntity<byte[]> exportPdf(@PathVariable String reportId) {
        try {
            String filePath = reportService.exportPdf(reportId);
            byte[] pdfBytes = Files.readAllBytes(Paths.get(filePath));

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDispositionFormData("filename", "fraud_report_" + reportId + ".pdf");

            return ResponseEntity.ok()
                    .headers(headers)
                    .body(pdfBytes);
        } catch (Exception e) {
            log.error("导出 PDF 报告失败: reportId={}", reportId, e);
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * 导出图片格式的反诈报告
     *
     * @param reportId 报告唯一标识
     * @return 图片文件响应
     */
    @GetMapping("/image/{reportId}")
    public ResponseEntity<byte[]> exportImage(@PathVariable String reportId) {
        try {
            byte[] imageBytes = reportService.exportImage(reportId);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.IMAGE_PNG);
            headers.setContentDispositionFormData("filename", "fraud_report_" + reportId + ".png");

            return ResponseEntity.ok()
                    .headers(headers)
                    .body(imageBytes);
        } catch (Exception e) {
            log.error("导出图片报告失败: reportId={}", reportId, e);
            return ResponseEntity.badRequest().build();
        }
    }
}

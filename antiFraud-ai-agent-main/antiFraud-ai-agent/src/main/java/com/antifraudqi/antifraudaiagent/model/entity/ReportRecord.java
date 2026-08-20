package com.antifraudqi.antifraudaiagent.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 举报记录实体
 * 存储用户提交的举报信息，包括举报类型、内容、截图和审核状态
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "report_record")
public class ReportRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 用户ID */
    @Column(nullable = false)
    private String userId;

    /** 举报类型：phone/url/account */
    private String reportType;

    /** 举报内容（电话号码/URL/账号等） */
    @Column(nullable = false)
    private String reportContent;

    /** 截图（Base64 编码），大字段存储 */
    @Lob
    @Column(columnDefinition = "LONGTEXT")
    private String screenshotBase64;

    /** 举报描述 */
    @Column(columnDefinition = "TEXT")
    private String description;

    /** 处理状态：submitted（已提交）/processing（处理中）/resolved（已处理） */
    @Column(nullable = false)
    private String status;

    /** 创建时间 */
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (status == null) {
            status = "submitted";
        }
    }
}

package com.antifraudqi.antifraudaiagent.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 反诈报告实体
 * 存储每次反诈检测生成的完整报告，包含风险评估、防范建议、法律指引等信息
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "fraud_report")
public class FraudReport {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 报告唯一标识（UUID） */
    @Column(nullable = false, unique = true)
    private String reportId;

    /** 用户ID */
    @Column(nullable = false)
    private String userId;

    /** 诈骗类型，如 刷单诈骗/冒充公检法/投资理财诈骗 等 */
    private String fraudType;

    /** 风险等级 */
    private String riskLevel;

    /** 风险评分 */
    private double riskScore;

    /** 风险来源分析（JSON格式） */
    @Column(columnDefinition = "TEXT")
    private String riskSources;

    /** 防范建议（JSON格式） */
    @Column(columnDefinition = "TEXT")
    private String preventionTips;

    /** 转账预警提示 */
    @Column(columnDefinition = "TEXT")
    private String transferWarning;

    /** 法律指引 */
    @Column(columnDefinition = "TEXT")
    private String legalGuidance;

    /** 报告类型：自查/网格员协助/公安备案 */
    private String reportType;

    /** 原始证据（JSON格式），如聊天记录截图、通话录音等 */
    @Column(columnDefinition = "TEXT")
    private String rawEvidence;

    /** 分析步骤（JSON格式），记录 AI 分析的完整推理过程 */
    @Column(columnDefinition = "TEXT")
    private String analysisSteps;

    /** 创建时间 */
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}

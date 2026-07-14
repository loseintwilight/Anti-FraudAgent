package com.antifraudqi.antifraudaiagent.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 检测历史实体
 * 记录用户每次反诈检测的输入内容、检测结果及收藏状态
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "detection_history")
public class DetectionHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 用户ID */
    @Column(nullable = false)
    private String userId;

    /** 输入类型：text/image/video */
    private String inputType;

    /** 输入内容（文本原文或图片/视频的描述信息） */
    @Column(columnDefinition = "TEXT")
    private String inputContent;

    /** 识别出的诈骗类型 */
    private String fraudType;

    /** 风险等级 */
    private String riskLevel;

    /** 风险评分 */
    private double riskScore;

    /** 是否已收藏 */
    @Column(nullable = false)
    private boolean isFavorited;

    /** 创建时间 */
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}

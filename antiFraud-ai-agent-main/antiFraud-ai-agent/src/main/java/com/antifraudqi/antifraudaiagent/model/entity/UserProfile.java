package com.antifraudqi.antifraudaiagent.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 用户画像实体
 * 存储用户的基本画像信息、行为模式和风险评估结果
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "user_profile")
public class UserProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 用户ID，唯一标识 */
    @Column(nullable = false, unique = true)
    private String userId;

    /** 年龄段，如 18-25, 26-35, 36-45, 46+ */
    private String ageGroup;

    /** 职业标签 */
    private String occupationTag;

    /** 联系方式（JSON格式），如 ["phone","email","wechat"] */
    @Column(columnDefinition = "TEXT")
    private String contactMethods;

    /** 查询历史（JSON格式），记录用户的查询轨迹 */
    @Column(columnDefinition = "TEXT")
    private String queryHistory;

    /** 行为模式（JSON格式），描述用户的典型行为特征 */
    @Column(columnDefinition = "TEXT")
    private String behaviorPatterns;

    /** 风险评分（0-100），越高越危险 */
    private double riskScore;

    /** 风险等级，如 LOW/MEDIUM/HIGH/CRITICAL */
    private String riskLevel;

    /** 创建时间 */
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /** 更新时间 */
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

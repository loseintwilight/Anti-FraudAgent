package com.antifraud.admin.domain;

import java.time.LocalDateTime;

/**
 * 反诈报告对象 fraud_report
 * 
 * @author antiFraud
 */
public class FraudReport
{
    private static final long serialVersionUID = 1L;

    /** 报告ID */
    private Long id;

    /** 用户ID */
    private String userId;

    /** 报告标题 */
    private String title;

    /** 风险等级 */
    private String riskLevel;

    /** 风险评分 */
    private Double riskScore;

    /** 诈骗类型 */
    private String fraudType;

    /** 建议列表（JSON数组） */
    private String suggestions;

    /** 报告详细内容 */
    private String reportContent;

    /** 报告图片Base64 */
    private String imageBase64;

    /** 状态：pending/completed/archived */
    private String status;

    /** 创建时间 */
    private LocalDateTime createdAt;

    /** 更新时间 */
    private LocalDateTime updatedAt;

    public FraudReport()
    {
    }

    public Long getId()
    {
        return id;
    }

    public void setId(Long id)
    {
        this.id = id;
    }

    public String getUserId()
    {
        return userId;
    }

    public void setUserId(String userId)
    {
        this.userId = userId;
    }

    public String getTitle()
    {
        return title;
    }

    public void setTitle(String title)
    {
        this.title = title;
    }

    public String getRiskLevel()
    {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel)
    {
        this.riskLevel = riskLevel;
    }

    public Double getRiskScore()
    {
        return riskScore;
    }

    public void setRiskScore(Double riskScore)
    {
        this.riskScore = riskScore;
    }

    public String getFraudType()
    {
        return fraudType;
    }

    public void setFraudType(String fraudType)
    {
        this.fraudType = fraudType;
    }

    public String getSuggestions()
    {
        return suggestions;
    }

    public void setSuggestions(String suggestions)
    {
        this.suggestions = suggestions;
    }

    public String getReportContent()
    {
        return reportContent;
    }

    public void setReportContent(String reportContent)
    {
        this.reportContent = reportContent;
    }

    public String getImageBase64()
    {
        return imageBase64;
    }

    public void setImageBase64(String imageBase64)
    {
        this.imageBase64 = imageBase64;
    }

    public String getStatus()
    {
        return status;
    }

    public void setStatus(String status)
    {
        this.status = status;
    }

    public LocalDateTime getCreatedAt()
    {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt)
    {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt()
    {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt)
    {
        this.updatedAt = updatedAt;
    }
}
package com.antifraud.admin.domain;

import java.time.LocalDateTime;

/**
 * 检测记录对象 detection_history
 * 
 * @author antiFraud
 */
public class DetectionHistory
{
    private static final long serialVersionUID = 1L;

    /** 记录ID */
    private Long id;

    /** 用户ID */
    private String userId;

    /** 输入类型：text/image/video */
    private String inputType;

    /** 输入内容/文本 */
    private String inputContent;

    /** 诈骗类型 */
    private String fraudType;

    /** 风险评分 */
    private Double riskScore;

    /** 风险等级 */
    private String riskLevel;

    /** 置信度 */
    private Double confidence;

    /** 建议 */
    private String suggestion;

    /** AI回复内容 */
    private String aiResponse;

    /** 创建时间 */
    private LocalDateTime createdAt;

    public DetectionHistory()
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

    public String getInputType()
    {
        return inputType;
    }

    public void setInputType(String inputType)
    {
        this.inputType = inputType;
    }

    public String getInputContent()
    {
        return inputContent;
    }

    public void setInputContent(String inputContent)
    {
        this.inputContent = inputContent;
    }

    public String getFraudType()
    {
        return fraudType;
    }

    public void setFraudType(String fraudType)
    {
        this.fraudType = fraudType;
    }

    public Double getRiskScore()
    {
        return riskScore;
    }

    public void setRiskScore(Double riskScore)
    {
        this.riskScore = riskScore;
    }

    public String getRiskLevel()
    {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel)
    {
        this.riskLevel = riskLevel;
    }

    public Double getConfidence()
    {
        return confidence;
    }

    public void setConfidence(Double confidence)
    {
        this.confidence = confidence;
    }

    public String getSuggestion()
    {
        return suggestion;
    }

    public void setSuggestion(String suggestion)
    {
        this.suggestion = suggestion;
    }

    public String getAiResponse()
    {
        return aiResponse;
    }

    public void setAiResponse(String aiResponse)
    {
        this.aiResponse = aiResponse;
    }

    public LocalDateTime getCreatedAt()
    {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt)
    {
        this.createdAt = createdAt;
    }
}
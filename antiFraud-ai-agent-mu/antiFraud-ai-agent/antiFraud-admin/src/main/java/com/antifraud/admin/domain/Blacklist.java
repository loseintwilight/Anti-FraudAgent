package com.antifraud.admin.domain;

import java.time.LocalDateTime;

/**
 * 黑名单对象 blacklist
 * 
 * @author antiFraud
 */
public class Blacklist
{
    private static final long serialVersionUID = 1L;

    /** 记录ID */
    private Long id;

    /** 类型：phone/account/wechat/url */
    private String targetType;

    /** 具体值：手机号/账号/微信号/URL */
    private String targetValue;

    /** 来源：manual/crawler/report */
    private String source;

    /** 拉黑原因 */
    private String reason;

    /** 状态：0-已解除 1-生效中 */
    private Integer status;

    /** 操作人 */
    private String operator;

    /** 创建时间 */
    private LocalDateTime createdAt;

    /** 更新时间 */
    private LocalDateTime updatedAt;

    public Blacklist()
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

    public String getTargetType()
    {
        return targetType;
    }

    public void setTargetType(String targetType)
    {
        this.targetType = targetType;
    }

    public String getTargetValue()
    {
        return targetValue;
    }

    public void setTargetValue(String targetValue)
    {
        this.targetValue = targetValue;
    }

    public String getSource()
    {
        return source;
    }

    public void setSource(String source)
    {
        this.source = source;
    }

    public String getReason()
    {
        return reason;
    }

    public void setReason(String reason)
    {
        this.reason = reason;
    }

    public Integer getStatus()
    {
        return status;
    }

    public void setStatus(Integer status)
    {
        this.status = status;
    }

    public String getOperator()
    {
        return operator;
    }

    public void setOperator(String operator)
    {
        this.operator = operator;
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
package com.antifraud.admin.domain;

import java.time.LocalDateTime;

/**
 * 用户画像对象 user_profile
 * 
 * @author antiFraud
 */
public class UserProfile
{
    private static final long serialVersionUID = 1L;

    /** 记录ID */
    private Long id;

    /** 用户ID */
    private String userId;

    /** 年龄 */
    private Integer age;

    /** 性别 */
    private String gender;

    /** 职业 */
    private String occupation;

    /** 教育程度 */
    private String education;

    /** 省份 */
    private String province;

    /** 城市 */
    private String city;

    /** 综合风险评分 */
    private Double riskScore;

    /** 风险等级 */
    private String riskLevel;

    /** 画像JSON详情 */
    private String profileJson;

    /** 创建时间 */
    private LocalDateTime createdAt;

    /** 更新时间 */
    private LocalDateTime updatedAt;

    public UserProfile()
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

    public Integer getAge()
    {
        return age;
    }

    public void setAge(Integer age)
    {
        this.age = age;
    }

    public String getGender()
    {
        return gender;
    }

    public void setGender(String gender)
    {
        this.gender = gender;
    }

    public String getOccupation()
    {
        return occupation;
    }

    public void setOccupation(String occupation)
    {
        this.occupation = occupation;
    }

    public String getEducation()
    {
        return education;
    }

    public void setEducation(String education)
    {
        this.education = education;
    }

    public String getProvince()
    {
        return province;
    }

    public void setProvince(String province)
    {
        this.province = province;
    }

    public String getCity()
    {
        return city;
    }

    public void setCity(String city)
    {
        this.city = city;
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

    public String getProfileJson()
    {
        return profileJson;
    }

    public void setProfileJson(String profileJson)
    {
        this.profileJson = profileJson;
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
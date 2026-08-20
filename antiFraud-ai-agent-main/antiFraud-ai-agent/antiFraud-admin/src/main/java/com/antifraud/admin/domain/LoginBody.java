package com.antifraud.admin.domain;

import com.fasterxml.jackson.annotation.JsonAlias;
import jakarta.validation.constraints.NotBlank;

/**
 * 登录请求体
 */
public class LoginBody {

    @NotBlank(message = "用户名不能为空")
    private String username;

    @NotBlank(message = "密码不能为空")
    private String password;

    /** 验证码：兼容前端用 code 或 captcha 提交 */
    @JsonAlias({"code", "captcha"})
    private String code;

    private String uuid;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    /** 同时兼容 code/captcha 两种命名 */
    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    /** 兼容旧字段 captcha */
    public String getCaptcha() {
        return code;
    }

    public void setCaptcha(String captcha) {
        this.code = captcha;
    }

    public String getUuid() {
        return uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }
}
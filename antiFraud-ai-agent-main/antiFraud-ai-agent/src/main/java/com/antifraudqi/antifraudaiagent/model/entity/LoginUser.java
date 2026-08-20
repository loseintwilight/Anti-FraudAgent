package com.antifraudqi.antifraudaiagent.model.entity;

import java.time.LocalDateTime;

/**
 * 登录用户信息（存储于 Redis）
 */
public class LoginUser {

    private Long userId;
    private String username;
    private String role;
    private String token;
    private LocalDateTime loginTime;

    public LoginUser() {
    }

    public LoginUser(Long userId, String username, String role) {
        this.userId = userId;
        this.username = username;
        this.role = role;
        this.loginTime = LocalDateTime.now();
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public LocalDateTime getLoginTime() {
        return loginTime;
    }

    public void setLoginTime(LocalDateTime loginTime) {
        this.loginTime = loginTime;
    }
}
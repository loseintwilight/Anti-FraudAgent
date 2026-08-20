package com.antifraud.admin.domain;

import java.time.LocalDateTime;
import java.util.Set;

/**
 * 登录用户信息（存储于SecurityContext）
 */
public class LoginUser {

    private Long userId;
    private String username;
    private String role;
    private Set<String> permissions;
    private LocalDateTime loginTime;
    private String token;

    public LoginUser() {
    }

    public LoginUser(Long userId, String username, String role, Set<String> permissions) {
        this.userId = userId;
        this.username = username;
        this.role = role;
        this.permissions = permissions;
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

    public Set<String> getPermissions() {
        return permissions;
    }

    public void setPermissions(Set<String> permissions) {
        this.permissions = permissions;
    }

    public LocalDateTime getLoginTime() {
        return loginTime;
    }

    public void setLoginTime(LocalDateTime loginTime) {
        this.loginTime = loginTime;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }
}
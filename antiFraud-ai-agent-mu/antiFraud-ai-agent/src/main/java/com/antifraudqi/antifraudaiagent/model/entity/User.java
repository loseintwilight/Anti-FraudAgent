package com.antifraudqi.antifraudaiagent.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 系统用户实体
 * 存储登录认证信息，使用 MySQL 存储
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "sys_user")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long id;

    /** 用户名，唯一 */
    @Column(name = "user_name", nullable = false, unique = true, length = 50)
    private String username;

    /** BCrypt 加密后的密码 */
    @Column(nullable = false, length = 200)
    private String password;

    /** 手机号 */
    @Column(length = 20)
    private String phone;

    /** 角色：admin / grid_member / user */
    @Column(nullable = false, length = 20)
    @Builder.Default
    private String role = "user";

    /** 用户状态：0-正常 1-禁用（兼容 RuoYi 的 char(1) '0'=正常 '1'=停用） */
    @Column(nullable = false)
    @Builder.Default
    private Integer status = 0;

    /** 最后登录时间 */
    private LocalDateTime lastLoginTime;

    /** 创建时间 */
    @Column(name = "create_time", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /** 更新时间 */
    @Column(name = "update_time", nullable = false)
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
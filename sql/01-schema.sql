-- ============================================================
-- 反诈大师 - 业务核心表结构
-- MySQL 8.0+（兼容 MySQL 5.7+）
--
-- 前置条件：
--   1. 已创建 anti_fraud 数据库
--   2. 管理端（antiFraud-admin）基于 RuoYi，需先导入 RuoYi 官方基础表脚本
--      （sys_user / sys_role / sys_menu / sys_user_role / sys_role_menu 等）
--      获取地址：https://gitee.com/y_project/RuoYi-Vue  或  https://github.com/yangzongzhuan/RuoYi-Vue
--
-- 执行顺序：
--   RuoYi 官方脚本  ->  01-schema.sql  ->  02-admin-init.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS `anti_fraud`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `anti_fraud`;

-- ============================================================
-- 1. 用户画像表
-- ============================================================
CREATE TABLE IF NOT EXISTS `user_profile` (
    `id`              BIGINT       NOT NULL AUTO_INCREMENT  COMMENT '记录ID',
    `user_id`         VARCHAR(50)  NOT NULL                  COMMENT '用户ID',
    `age`             INT          DEFAULT 0                 COMMENT '年龄',
    `gender`          VARCHAR(10)  DEFAULT 'unknown'         COMMENT '性别',
    `occupation`      VARCHAR(50)  DEFAULT 'unknown'         COMMENT '职业',
    `education`       VARCHAR(50)  DEFAULT 'unknown'         COMMENT '教育程度',
    `province`        VARCHAR(50)  DEFAULT 'unknown'         COMMENT '省份',
    `city`            VARCHAR(50)  DEFAULT 'unknown'         COMMENT '城市',
    `risk_score`      DOUBLE       DEFAULT 0.0               COMMENT '综合风险评分',
    `risk_level`      VARCHAR(20)  DEFAULT 'unknown'         COMMENT '风险等级',
    `profile_json`    TEXT         DEFAULT NULL              COMMENT '画像JSON详情',
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_risk_level` (`risk_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户画像表';

-- ============================================================
-- 2. 检测记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS `detection_history` (
    `id`              BIGINT       NOT NULL AUTO_INCREMENT  COMMENT '记录ID',
    `user_id`         VARCHAR(50)  NOT NULL                  COMMENT '用户ID',
    `input_type`      VARCHAR(20)  DEFAULT 'text'            COMMENT '输入类型：text/image/video',
    `input_content`   TEXT         NOT NULL                  COMMENT '输入内容/文本',
    `fraud_type`      VARCHAR(50)  DEFAULT NULL              COMMENT '诈骗类型',
    `risk_score`      DOUBLE       DEFAULT 0.0               COMMENT '风险评分',
    `risk_level`      VARCHAR(20)  DEFAULT 'unknown'         COMMENT '风险等级',
    `confidence`      DOUBLE       DEFAULT 0.0               COMMENT '置信度',
    `suggestion`      TEXT         DEFAULT NULL              COMMENT '建议',
    `ai_response`     TEXT         DEFAULT NULL              COMMENT 'AI回复内容',
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_fraud_type` (`fraud_type`),
    KEY `idx_risk_level` (`risk_level`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检测记录表';

-- ============================================================
-- 3. 反诈报告表
-- ============================================================
CREATE TABLE IF NOT EXISTS `fraud_report` (
    `id`              BIGINT       NOT NULL AUTO_INCREMENT  COMMENT '报告ID',
    `user_id`         VARCHAR(50)  NOT NULL                  COMMENT '用户ID',
    `title`           VARCHAR(200) DEFAULT NULL              COMMENT '报告标题',
    `risk_level`      VARCHAR(20)  DEFAULT NULL              COMMENT '风险等级',
    `risk_score`      DOUBLE       DEFAULT 0.0               COMMENT '风险评分',
    `fraud_type`      VARCHAR(50)  DEFAULT NULL              COMMENT '诈骗类型',
    `suggestions`     TEXT         DEFAULT NULL              COMMENT '建议列表（JSON数组）',
    `report_content`  TEXT         DEFAULT NULL              COMMENT '报告详细内容',
    `image_base64`    LONGTEXT     DEFAULT NULL              COMMENT '报告图片Base64',
    `status`          VARCHAR(20)  DEFAULT 'pending'         COMMENT '状态：pending/completed/archived',
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_risk_level` (`risk_level`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='反诈报告表';
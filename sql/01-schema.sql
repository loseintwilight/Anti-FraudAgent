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
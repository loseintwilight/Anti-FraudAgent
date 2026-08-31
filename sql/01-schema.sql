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

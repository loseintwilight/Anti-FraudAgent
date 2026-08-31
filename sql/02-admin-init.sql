-- ============================================================
-- 反诈大师 - 管理后台初始化脚本
-- MySQL 8.0+（兼容 MySQL 5.7+）
--
-- 前置条件：已导入 RuoYi 官方基础表脚本 + 01-schema.sql
-- 功能：创建反诈管理菜单、网格员角色、按钮权限及关联关系
--
-- 安全提示（重要）：
--   本脚本中的 BCrypt 密码哈希为 RuoYi 框架出厂默认值（明文为 admin123），
--   仅用于本地开发调试。部署到任何公网环境前，必须修改所有账号密码。
--   示例手机号 / 邮箱均为占位数据，请按实际情况替换。
-- ============================================================

USE `anti_fraud`;

-- ============================================================
-- 1. 反诈管理菜单（menu_id 从 2001 起，避开 RuoYi 默认占用的 1-1060）
-- ============================================================
INSERT IGNORE INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `query`, `route_name`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES
(2001, '反诈管理', 0, 5, 'fraud', NULL, '', 'fraud', 1, 0, 'M', '0', '0', '', 'shield', 'admin', NOW(), '', NULL, '反诈管理目录');

INSERT IGNORE INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `query`, `route_name`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES
(2002, '检测记录', 2001, 1, 'detection', 'fraud/detection/index', '', 'detection', 1, 0, 'C', '0', '0', 'fraud:detection:list', 'search', 'admin', NOW(), '', NULL, '检测记录菜单'),
(2003, '报告管理', 2001, 2, 'report', 'fraud/report/index', '', 'report', 1, 0, 'C', '0', '0', 'fraud:report:list', 'document', 'admin', NOW(), '', NULL, '报告管理菜单'),
(2004, '黑名单管理', 2001, 3, 'blacklist', 'fraud/blacklist/index', '', 'blacklist', 1, 0, 'C', '0', '0', 'fraud:blacklist:list', 'lock', 'admin', NOW(), '', NULL, '黑名单管理菜单'),
(2005, '用户画像', 2001, 4, 'profile', 'fraud/profile/index', '', 'profile', 1, 0, 'C', '0', '0', 'fraud:profile:list', 'user', 'admin', NOW(), '', NULL, '用户画像菜单');

INSERT IGNORE INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `query`, `route_name`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES
(2006, '仪表盘', 0, 0, 'dashboard', 'dashboard/index', '', 'dashboard', 1, 0, 'C', '0', '0', 'dashboard:view', 'dashboard', 'admin', NOW(), '', NULL, '仪表盘菜单');
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

-- ============================================================
-- 2. 按钮级权限（F 类型）
-- ============================================================
INSERT IGNORE INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `query`, `route_name`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES
(2101, '检测记录查询', 2002, 1, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:detection:query', '#', 'admin', NOW(), '', NULL, ''),
(2102, '检测记录新增', 2002, 2, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:detection:add', '#', 'admin', NOW(), '', NULL, ''),
(2103, '检测记录修改', 2002, 3, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:detection:edit', '#', 'admin', NOW(), '', NULL, ''),
(2104, '检测记录删除', 2002, 4, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:detection:remove', '#', 'admin', NOW(), '', NULL, ''),
(2105, '报告查询', 2003, 1, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:report:query', '#', 'admin', NOW(), '', NULL, ''),
(2106, '报告新增', 2003, 2, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:report:add', '#', 'admin', NOW(), '', NULL, ''),
(2107, '报告修改', 2003, 3, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:report:edit', '#', 'admin', NOW(), '', NULL, ''),
(2108, '报告删除', 2003, 4, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:report:remove', '#', 'admin', NOW(), '', NULL, ''),
(2109, '黑名单查询', 2004, 1, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:blacklist:query', '#', 'admin', NOW(), '', NULL, ''),
(2110, '黑名单新增', 2004, 2, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:blacklist:add', '#', 'admin', NOW(), '', NULL, ''),
(2111, '黑名单修改', 2004, 3, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:blacklist:edit', '#', 'admin', NOW(), '', NULL, ''),
(2112, '黑名单删除', 2004, 4, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:blacklist:remove', '#', 'admin', NOW(), '', NULL, ''),
(2113, '用户画像查询', 2005, 1, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:profile:query', '#', 'admin', NOW(), '', NULL, ''),
(2114, '用户画像新增', 2005, 2, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:profile:add', '#', 'admin', NOW(), '', NULL, ''),
(2115, '用户画像修改', 2005, 3, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:profile:edit', '#', 'admin', NOW(), '', NULL, ''),
(2116, '用户画像删除', 2005, 4, '', NULL, '', '', 1, 0, 'F', '0', '0', 'fraud:profile:remove', '#', 'admin', NOW(), '', NULL, '');

-- ============================================================
-- 3. 网格员角色（role_id=3，RuoYi 默认已占用 1=超级管理员 2=普通角色）
-- ============================================================
INSERT IGNORE INTO `sys_role` (`role_id`, `role_name`, `role_key`, `role_sort`, `data_scope`, `menu_check_strictly`, `dept_check_strictly`, `status`, `del_flag`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES
(3, '网格员', 'grid_member', 3, '1', 1, 1, '0', '0', 'admin', NOW(), '', NULL, '网格员角色');

-- ============================================================
-- 4. 可选：网格员演示账号
--    邮箱 / 手机号为占位数据，请按实际情况替换
--    密码哈希为 RuoYi 出厂默认值（明文 admin123），上线前务必修改
-- ============================================================
INSERT IGNORE INTO `sys_user` (`user_id`, `dept_id`, `user_name`, `nick_name`, `user_type`, `email`, `phonenumber`, `sex`, `avatar`, `password`, `status`, `del_flag`, `login_ip`, `login_date`, `pwd_update_date`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES
(3, 103, 'grid_user', '网格员', '00', 'grid@example.com', '13800000000', '0', '', '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', '0', '0', '', NOW(), NOW(), 'admin', NOW(), '', NULL, '网格员演示账号');

INSERT IGNORE INTO `sys_user_role` (`user_id`, `role_id`) VALUES (3, 3);

-- ============================================================
-- 5. 角色 - 菜单关联
--    超级管理员（role_id=1）：反诈管理全部权限
--    网格员（role_id=3）：仅查看类权限
-- ============================================================
INSERT IGNORE INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT 1, `menu_id` FROM `sys_menu` WHERE `menu_id` >= 2001;

INSERT IGNORE INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT 3, `menu_id` FROM `sys_menu` WHERE `menu_id` IN (2001, 2002, 2003, 2004, 2005, 2006, 2101, 2105, 2109, 2113);

-- ============================================================
-- 6. 初始化结果校验
-- ============================================================
SELECT `menu_id`, `menu_name`, `parent_id`, `perms`
FROM `sys_menu`
WHERE `menu_id` >= 2001
ORDER BY `menu_id`;

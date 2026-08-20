package com.antifraud.admin.service;

import com.antifraud.admin.domain.SysMenu;
import com.antifraud.admin.mapper.SysMenuMapper;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 权限服务
 */
@Service
public class SysPermissionService {

    @Resource
    private SysMenuMapper sysMenuMapper;

    /**
     * 获取用户权限标识集合
     */
    public Set<String> getMenuPermission(Long userId) {
        List<SysMenu> perms = sysMenuMapper.selectMenuPermsByUserId(userId);
        if (perms == null || perms.isEmpty()) {
            return new HashSet<>();
        }
        return perms.stream()
                .map(SysMenu::getPerms)
                .collect(Collectors.toSet());
    }
}
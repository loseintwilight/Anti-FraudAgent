package com.antifraud.admin.mapper;

import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface SysRoleMenuMapper {

    List<Long> selectMenuIdsByRoleId(Long roleId);

    int insertRoleMenu(Long roleId, Long menuId);

    int deleteRoleMenuByRoleId(Long roleId);

    int deleteRoleMenuByMenuId(Long menuId);
}
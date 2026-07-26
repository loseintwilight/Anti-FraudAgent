package com.antifraud.admin.mapper;

import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface SysUserRoleMapper {

    List<Long> selectRoleIdsByUserId(Long userId);

    int insertUserRole(Long userId, Long roleId);

    int deleteUserRoleByUserId(Long userId);
}
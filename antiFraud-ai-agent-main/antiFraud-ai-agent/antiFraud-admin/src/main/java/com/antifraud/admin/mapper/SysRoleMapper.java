package com.antifraud.admin.mapper;

import com.antifraud.admin.domain.SysRole;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface SysRoleMapper {

    SysRole selectRoleById(Long id);

    List<SysRole> selectRoleList(SysRole role);

    List<SysRole> selectRoleByUserId(Long userId);

    int insertRole(SysRole role);

    int updateRole(SysRole role);

    int deleteRoleById(Long id);
}
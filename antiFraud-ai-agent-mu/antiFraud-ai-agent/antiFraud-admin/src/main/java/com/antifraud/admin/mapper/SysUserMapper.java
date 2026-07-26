package com.antifraud.admin.mapper;

import com.antifraud.admin.domain.SysUser;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface SysUserMapper {

    SysUser selectUserById(Long id);

    SysUser selectUserByUsername(String username);

    List<SysUser> selectUserList(SysUser user);

    int insertUser(SysUser user);

    int updateUser(SysUser user);

    int deleteUserById(Long id);

    int updateLastLoginTime(@Param("id") Long id);
}
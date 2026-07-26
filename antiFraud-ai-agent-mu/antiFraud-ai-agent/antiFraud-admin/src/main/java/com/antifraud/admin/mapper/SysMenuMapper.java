package com.antifraud.admin.mapper;

import com.antifraud.admin.domain.SysMenu;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface SysMenuMapper {

    SysMenu selectMenuById(Long id);

    List<SysMenu> selectMenuList(SysMenu menu);

    List<SysMenu> selectMenuByUserId(Long userId);

    List<SysMenu> selectMenuPermsByUserId(Long userId);

    int insertMenu(SysMenu menu);

    int updateMenu(SysMenu menu);

    int deleteMenuById(Long id);
}
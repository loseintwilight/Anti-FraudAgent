package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.SysMenu;
import com.antifraud.admin.mapper.SysMenuMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 菜单管理控制器
 */
@RestController
@RequestMapping("/api/v1/menu")
@Tag(name = "菜单管理", description = "系统菜单增删改查")
public class SysMenuController {

    @Resource
    private SysMenuMapper sysMenuMapper;

    @GetMapping("/list")
    @Operation(summary = "菜单列表")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult list(SysMenu menu) {
        List<SysMenu> list = sysMenuMapper.selectMenuList(menu);
        return AjaxResult.success(list);
    }

    @GetMapping("/{id}")
    @Operation(summary = "菜单详情")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult getInfo(@PathVariable Long id) {
        SysMenu menu = sysMenuMapper.selectMenuById(id);
        return menu != null ? AjaxResult.success(menu) : AjaxResult.error("菜单不存在");
    }

    @PostMapping
    @Operation(summary = "新增菜单")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult add(@RequestBody SysMenu menu) {
        int result = sysMenuMapper.insertMenu(menu);
        return result > 0 ? AjaxResult.success("新增成功") : AjaxResult.error("新增失败");
    }

    @PutMapping
    @Operation(summary = "修改菜单")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult edit(@RequestBody SysMenu menu) {
        int result = sysMenuMapper.updateMenu(menu);
        return result > 0 ? AjaxResult.success("修改成功") : AjaxResult.error("修改失败");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除菜单")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult remove(@PathVariable Long id) {
        int result = sysMenuMapper.deleteMenuById(id);
        return result > 0 ? AjaxResult.success("删除成功") : AjaxResult.error("删除失败");
    }
}
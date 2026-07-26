package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.SysRole;
import com.antifraud.admin.mapper.SysRoleMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 角色管理控制器
 */
@RestController
@RequestMapping("/api/v1/role")
@Tag(name = "角色管理", description = "系统角色增删改查")
public class SysRoleController {

    @Resource
    private SysRoleMapper sysRoleMapper;

    @GetMapping("/list")
    @Operation(summary = "角色列表")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult list(SysRole role,
                           @RequestParam(defaultValue = "1") int pageNum,
                           @RequestParam(defaultValue = "10") int pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<SysRole> list = sysRoleMapper.selectRoleList(role);
        PageInfo<SysRole> pageInfo = new PageInfo<>(list);
        return AjaxResult.success(pageInfo);
    }

    @GetMapping("/{id}")
    @Operation(summary = "角色详情")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult getInfo(@PathVariable Long id) {
        SysRole role = sysRoleMapper.selectRoleById(id);
        return role != null ? AjaxResult.success(role) : AjaxResult.error("角色不存在");
    }

    @PostMapping
    @Operation(summary = "新增角色")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult add(@RequestBody SysRole role) {
        int result = sysRoleMapper.insertRole(role);
        return result > 0 ? AjaxResult.success("新增成功") : AjaxResult.error("新增失败");
    }

    @PutMapping
    @Operation(summary = "修改角色")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult edit(@RequestBody SysRole role) {
        int result = sysRoleMapper.updateRole(role);
        return result > 0 ? AjaxResult.success("修改成功") : AjaxResult.error("修改失败");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除角色")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult remove(@PathVariable Long id) {
        int result = sysRoleMapper.deleteRoleById(id);
        return result > 0 ? AjaxResult.success("删除成功") : AjaxResult.error("删除失败");
    }
}
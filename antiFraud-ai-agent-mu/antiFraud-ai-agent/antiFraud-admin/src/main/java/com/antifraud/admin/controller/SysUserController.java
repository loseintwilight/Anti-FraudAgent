package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.LoginUser;
import com.antifraud.admin.domain.SysUser;
import com.antifraud.admin.mapper.SysUserMapper;
import com.antifraud.admin.service.TokenService;
import com.antifraud.admin.util.ServletUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 用户管理控制器
 */
@RestController
@RequestMapping("/api/v1/user")
@Tag(name = "用户管理", description = "系统用户增删改查")
public class SysUserController {

    @Resource
    private SysUserMapper sysUserMapper;

    @Resource
    private PasswordEncoder passwordEncoder;

    @Resource
    private TokenService tokenService;

    @GetMapping("/list")
    @Operation(summary = "用户列表")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult list(SysUser user,
                           @RequestParam(defaultValue = "1") int pageNum,
                           @RequestParam(defaultValue = "10") int pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<SysUser> list = sysUserMapper.selectUserList(user);
        PageInfo<SysUser> pageInfo = new PageInfo<>(list);
        return AjaxResult.success(pageInfo);
    }

    @GetMapping("/{id}")
    @Operation(summary = "用户详情")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult getInfo(@PathVariable Long id) {
        SysUser user = sysUserMapper.selectUserById(id);
        if (user == null) {
            return AjaxResult.error("用户不存在");
        }
        user.setPassword(null);
        return AjaxResult.success(user);
    }

    @PostMapping
    @Operation(summary = "新增用户")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult add(@RequestBody SysUser user) {
        if (sysUserMapper.selectUserByUsername(user.getUsername()) != null) {
            return AjaxResult.error("用户名已存在");
        }
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        int result = sysUserMapper.insertUser(user);
        return result > 0 ? AjaxResult.success("新增成功") : AjaxResult.error("新增失败");
    }

    @PutMapping
    @Operation(summary = "修改用户")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult edit(@RequestBody SysUser user) {
        if (user.getPassword() != null && !user.getPassword().isEmpty()) {
            user.setPassword(passwordEncoder.encode(user.getPassword()));
        }
        int result = sysUserMapper.updateUser(user);
        return result > 0 ? AjaxResult.success("修改成功") : AjaxResult.error("修改失败");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除用户")
    @PreAuthorize("hasRole('admin')")
    public AjaxResult remove(@PathVariable Long id) {
        int result = sysUserMapper.deleteUserById(id);
        return result > 0 ? AjaxResult.success("删除成功") : AjaxResult.error("删除失败");
    }

    @GetMapping("/profile")
    @Operation(summary = "获取当前用户个人信息")
    public AjaxResult getProfile() {
        try {
            HttpServletRequest request = ServletUtils.getRequest();
            LoginUser loginUser = tokenService.getLoginUser(request);
            if (loginUser == null) {
                return AjaxResult.unauthorized("未授权");
            }

            SysUser user = sysUserMapper.selectUserById(loginUser.getUserId());
            if (user == null) {
                return AjaxResult.error("用户不存在");
            }

            Map<String, Object> profile = new HashMap<>();
            profile.put("id", user.getId());
            profile.put("username", user.getUsername());
            profile.put("nickname", user.getNickname() != null ? user.getNickname() : user.getUsername());
            profile.put("fraudRole", user.getFraudRole() != null ? user.getFraudRole() : "youth");
            profile.put("phone", user.getPhone());

            return AjaxResult.success(profile);
        } catch (Exception e) {
            return AjaxResult.unauthorized("令牌无效或已过期");
        }
    }

    @PutMapping("/profile")
    @Operation(summary = "更新当前用户个人信息")
    public AjaxResult updateProfile(@RequestBody SysUser updateUser) {
        try {
            HttpServletRequest request = ServletUtils.getRequest();
            LoginUser loginUser = tokenService.getLoginUser(request);
            if (loginUser == null) {
                return AjaxResult.unauthorized("未授权");
            }

            SysUser user = new SysUser();
            user.setId(loginUser.getUserId());
            user.setNickname(updateUser.getNickname());
            user.setFraudRole(updateUser.getFraudRole());

            int result = sysUserMapper.updateUserProfile(user);
            return result > 0 ? AjaxResult.success("更新成功") : AjaxResult.error("更新失败");
        } catch (Exception e) {
            return AjaxResult.unauthorized("令牌无效或已过期");
        }
    }
}
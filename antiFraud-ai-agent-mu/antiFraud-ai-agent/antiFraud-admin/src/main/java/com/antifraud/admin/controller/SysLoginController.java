package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.LoginBody;
import com.antifraud.admin.domain.LoginUser;
import com.antifraud.admin.domain.SysUser;
import com.antifraud.admin.mapper.SysUserMapper;
import com.antifraud.admin.service.SysLoginService;
import com.antifraud.admin.service.TokenService;
import com.antifraud.admin.util.ServletUtils;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 登录控制器
 */
@RestController
@RequestMapping("/api/v1/auth")
@Tag(name = "登录管理", description = "用户登录、登出、信息获取")
public class SysLoginController {

    private static final Logger log = LoggerFactory.getLogger(SysLoginController.class);

    @Resource
    private SysLoginService sysLoginService;

    @Resource
    private TokenService tokenService;

    @Resource
    private SysUserMapper sysUserMapper;

    @PostMapping("/login")
    @Operation(summary = "用户登录")
    public AjaxResult login(@Valid @RequestBody LoginBody loginBody) {
        try {
            LoginUser loginUser = sysLoginService.login(loginBody.getUsername(), loginBody.getPassword());

            Map<String, Object> data = new HashMap<>();
            data.put("token", loginUser.getToken());
            data.put("user", Map.of(
                    "id", loginUser.getUserId(),
                    "username", loginUser.getUsername(),
                    "role", loginUser.getRole()
            ));

            // 查询用户详细信息
            SysUser sysUser = sysUserMapper.selectUserById(loginUser.getUserId());
            if (sysUser != null) {
                data.put("nickname", sysUser.getNickname() != null ? sysUser.getNickname() : sysUser.getUsername());
                data.put("fraudRole", sysUser.getFraudRole() != null ? sysUser.getFraudRole() : "youth");
            } else {
                data.put("nickname", loginUser.getUsername());
                data.put("fraudRole", "youth");
            }

            return AjaxResult.success("登录成功", data);
        } catch (Exception e) {
            log.error("登录失败", e);
            String msg = e.getMessage();
            if (msg == null) {
                msg = "登录失败: " + e.getClass().getSimpleName();
            }
            return AjaxResult.error(msg);
        }
    }

    @GetMapping("/userinfo")
    @Operation(summary = "获取当前用户信息")
    public AjaxResult getUserInfo() {
        try {
            HttpServletRequest request = ServletUtils.getRequest();
            LoginUser loginUser = tokenService.getLoginUser(request);
            if (loginUser == null) {
                return AjaxResult.unauthorized("未授权");
            }

            SysUser sysUser = sysUserMapper.selectUserById(loginUser.getUserId());

            Map<String, Object> userInfo = new HashMap<>();
            userInfo.put("id", loginUser.getUserId());
            userInfo.put("username", loginUser.getUsername());
            userInfo.put("role", loginUser.getRole());
            userInfo.put("nickname", sysUser != null && sysUser.getNickname() != null ? sysUser.getNickname() : loginUser.getUsername());
            userInfo.put("fraudRole", sysUser != null && sysUser.getFraudRole() != null ? sysUser.getFraudRole() : "youth");

            return AjaxResult.success(userInfo);
        } catch (Exception e) {
            return AjaxResult.unauthorized("令牌无效或已过期");
        }
    }

    @PostMapping("/register")
    @Operation(summary = "用户注册")
    public AjaxResult register(@Valid @RequestBody LoginBody loginBody) {
        try {
            // 检查用户名是否已存在
            if (sysUserMapper.selectUserByUsername(loginBody.getUsername()) != null) {
                return AjaxResult.error("用户名已存在");
            }

            // 创建新用户
            SysUser user = new SysUser();
            user.setUsername(loginBody.getUsername());
            user.setPassword(passwordEncoder.encode(loginBody.getPassword()));
            user.setPhone(loginBody.getPhone());
            user.setStatus(1);
            user.setNickname(loginBody.getUsername());
            user.setFraudRole("youth");

            int result = sysUserMapper.insertUser(user);
            return result > 0 ? AjaxResult.success("注册成功") : AjaxResult.error("注册失败");
        } catch (Exception e) {
            log.error("注册失败", e);
            return AjaxResult.error("注册失败: " + e.getMessage());
        }
    }
}
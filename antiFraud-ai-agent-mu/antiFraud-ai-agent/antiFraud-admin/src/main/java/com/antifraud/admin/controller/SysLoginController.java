package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.LoginBody;
import com.antifraud.admin.domain.LoginUser;
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

            Map<String, Object> userInfo = new HashMap<>();
            userInfo.put("id", loginUser.getUserId());
            userInfo.put("username", loginUser.getUsername());
            userInfo.put("role", loginUser.getRole());

            return AjaxResult.success(userInfo);
        } catch (Exception e) {
            return AjaxResult.unauthorized("令牌无效或已过期");
        }
    }
}
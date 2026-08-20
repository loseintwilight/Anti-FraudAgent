package com.antifraudqi.antifraudaiagent.controller;

import com.antifraudqi.antifraudaiagent.common.CacheConstants;
import com.antifraudqi.antifraudaiagent.common.RedisCache;
import com.antifraudqi.antifraudaiagent.config.JwtUtil;
import com.antifraudqi.antifraudaiagent.model.entity.LoginUser;
import com.antifraudqi.antifraudaiagent.model.entity.User;
import com.antifraudqi.antifraudaiagent.repository.UserRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * 认证控制器
 * 提供登录、注册、用户信息接口
 * 遵循若依框架思路：验证码 + Redis 存储登录用户
 */
@Slf4j
@RestController
@RequestMapping("/v1/auth")
@Tag(name = "认证管理", description = "用户登录、注册、信息查询")
public class AuthController {

    @Resource
    private UserRepository userRepository;

    @Resource
    private PasswordEncoder passwordEncoder;

    @Resource
    private JwtUtil jwtUtil;

    @Resource
    private RedisCache redisCache;

    @PostMapping("/login")
    @Operation(summary = "用户登录")
    public ResponseEntity<Map<String, Object>> login(@RequestBody LoginRequest request) {
        Map<String, Object> result = new HashMap<>();

        if (request.getUsername() == null || request.getUsername().isBlank()
                || request.getPassword() == null || request.getPassword().isBlank()) {
            result.put("success", false);
            result.put("message", "用户名和密码不能为空");
            return ResponseEntity.badRequest().body(result);
        }

        // 验证码校验（若依风格）
        if (request.getCode() != null && request.getUuid() != null) {
            String verifyKey = CacheConstants.CAPTCHA_CODE_KEY + request.getUuid();
            String captcha = redisCache.getCacheObject(verifyKey);
            if (captcha == null) {
                result.put("success", false);
                result.put("message", "验证码已过期");
                return ResponseEntity.status(401).body(result);
            }
            redisCache.deleteObject(verifyKey);
            if (!captcha.equalsIgnoreCase(request.getCode())) {
                result.put("success", false);
                result.put("message", "验证码错误");
                return ResponseEntity.status(401).body(result);
            }
        }

        // 查询用户
        Optional<User> userOpt = userRepository.findByUsername(request.getUsername().trim());
        if (userOpt.isEmpty()) {
            result.put("success", false);
            result.put("message", "用户名或密码错误");
            return ResponseEntity.status(401).body(result);
        }

        User user = userOpt.get();

        // 校验状态：RuoYi 的 status='0' 表示正常，Integer 0 表示正常
        // 但为了兼容 JPA 映射，这里明确：status=0 表示正常，status=1 表示禁用
        if (user.getStatus() != null && user.getStatus() == 1) {
            result.put("success", false);
            result.put("message", "账号已被禁用");
            return ResponseEntity.status(403).body(result);
        }

        // 校验密码
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            result.put("success", false);
            result.put("message", "用户名或密码错误");
            return ResponseEntity.status(401).body(result);
        }

        // 更新最后登录时间
        user.setLastLoginTime(LocalDateTime.now());
        userRepository.save(user);

        // ---- 若依风格：生成 token 并存储到 Redis ----
        // 生成唯一 token 标识
        String tokenKey = UUID.randomUUID().toString().replaceAll("-", "");

        // 创建 LoginUser 存储到 Redis
        LoginUser loginUser = new LoginUser(user.getId(), user.getUsername(), user.getRole());
        loginUser.setToken(tokenKey);

        // 存储到 Redis，24 小时过期
        String redisKey = CacheConstants.LOGIN_TOKEN_KEY + tokenKey;
        redisCache.setCacheObject(redisKey, loginUser, 24, TimeUnit.HOURS);

        // JWT 令牌中只包含 tokenKey，用户信息从 Redis 获取
        Map<String, Object> claims = new HashMap<>();
        claims.put("login_token_key", tokenKey);
        claims.put("userId", user.getId());
        claims.put("username", user.getUsername());
        String token = jwtUtil.generateToken(user.getId(), user.getUsername(), user.getRole());

        result.put("success", true);
        result.put("token", token);
        result.put("user", Map.of(
                "id", user.getId(),
                "username", user.getUsername(),
                "role", user.getRole(),
                "phone", user.getPhone() != null ? user.getPhone() : ""
        ));

        log.info("用户登录成功: username={}, role={}", user.getUsername(), user.getRole());
        return ResponseEntity.ok(result);
    }

    @PostMapping("/register")
    @Operation(summary = "用户注册")
    public ResponseEntity<Map<String, Object>> register(@RequestBody RegisterRequest request) {
        Map<String, Object> result = new HashMap<>();

        if (request.getUsername() == null || request.getUsername().isBlank()) {
            result.put("success", false);
            result.put("message", "用户名不能为空");
            return ResponseEntity.badRequest().body(result);
        }

        if (request.getPassword() == null || request.getPassword().length() < 6) {
            result.put("success", false);
            result.put("message", "密码长度不能少于6位");
            return ResponseEntity.badRequest().body(result);
        }

        if (userRepository.existsByUsername(request.getUsername().trim())) {
            result.put("success", false);
            result.put("message", "用户名已存在");
            return ResponseEntity.badRequest().body(result);
        }

        // 创建用户
        User user = User.builder()
                .username(request.getUsername().trim())
                .password(passwordEncoder.encode(request.getPassword()))
                .phone(request.getPhone() != null ? request.getPhone().trim() : null)
                .role(request.getRole() != null ? request.getRole() : "user")
                .status(0) // 0 = 正常（兼容 RuoYi）
                .build();

        userRepository.save(user);

        result.put("success", true);
        result.put("message", "注册成功");

        log.info("用户注册成功: username={}, role={}", user.getUsername(), user.getRole());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/userinfo")
    @Operation(summary = "获取当前用户信息")
    public ResponseEntity<Map<String, Object>> getUserInfo(@RequestHeader("Authorization") String authHeader) {
        Map<String, Object> result = new HashMap<>();

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            result.put("success", false);
            result.put("message", "未授权");
            return ResponseEntity.status(401).body(result);
        }

        try {
            String token = authHeader.substring(7);
            Long userId = jwtUtil.getUserId(token);
            String username = jwtUtil.getUsername(token);
            String role = jwtUtil.getRole(token);

            // 从 Redis 获取登录用户信息
            // 先从 JWT 中提取 login_token_key，如果没有则直接返回 JWT 中的信息
            try {
                var claims = jwtUtil.parseToken(token);
                String loginTokenKey = claims.get("login_token_key", String.class);
                if (loginTokenKey != null) {
                    String redisKey = CacheConstants.LOGIN_TOKEN_KEY + loginTokenKey;
                    LoginUser loginUser = redisCache.getCacheObject(redisKey);
                    if (loginUser != null) {
                        result.put("success", true);
                        result.put("user", Map.of(
                                "id", loginUser.getUserId(),
                                "username", loginUser.getUsername(),
                                "role", loginUser.getRole()
                        ));
                        return ResponseEntity.ok(result);
                    }
                }
            } catch (Exception ignored) {
                // 忽略 Redis 查找失败，降级使用 JWT 信息
            }

            result.put("success", true);
            result.put("user", Map.of(
                    "id", userId,
                    "username", username,
                    "role", role
            ));
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "令牌无效或已过期");
            return ResponseEntity.status(401).body(result);
        }

        return ResponseEntity.ok(result);
    }

    @Data
    public static class LoginRequest {
        private String username;
        private String password;
        private String code;
        private String uuid;
    }

    @Data
    public static class RegisterRequest {
        private String username;
        private String password;
        private String phone;
        private String role;
    }
}
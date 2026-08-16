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
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.awt.*;
import java.awt.geom.AffineTransform;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import javax.imageio.ImageIO;

/**
 * 登录控制器
 */
@RestController
@RequestMapping("/api/v1/auth")
@Tag(name = "登录管理", description = "用户登录、登出、信息获取")
public class SysLoginController {

    private static final Logger log = LoggerFactory.getLogger(SysLoginController.class);

    private static final String CAPTCHA_KEY_PREFIX = "antifraud:captcha:";
    private static final long CAPTCHA_EXPIRE_SECONDS = 120; // 2分钟

    /** 内存验证码缓存（Redis 不可用时的后备方案） */
    private static final ConcurrentHashMap<String, String> CAPTCHA_CACHE = new ConcurrentHashMap<>();
    private static final ConcurrentHashMap<String, Long> CAPTCHA_CACHE_EXPIRY = new ConcurrentHashMap<>();
    private static final java.util.Timer CAPTCHA_CLEANER = new java.util.Timer("captcha-cleaner", true);

    @Resource
    private SysLoginService sysLoginService;

    @Resource
    private TokenService tokenService;

    @Resource
    private SysUserMapper sysUserMapper;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired(required = false)
    private StringRedisTemplate stringRedisTemplate;

    /** 静态初始化：定时清理过期验证码 */
    static {
        CAPTCHA_CLEANER.scheduleAtFixedRate(new java.util.TimerTask() {
            @Override
            public void run() {
                long now = System.currentTimeMillis();
                CAPTCHA_CACHE_EXPIRY.forEach((key, expiry) -> {
                    if (now > expiry) {
                        CAPTCHA_CACHE.remove(key);
                        CAPTCHA_CACHE_EXPIRY.remove(key);
                    }
                });
            }
        }, 30_000, 30_000); // 每30秒清理一次
    }

    /**
     * 生成验证码图片
     */
    @GetMapping("/captchaImage")
    @Operation(summary = "获取登录验证码")
    public AjaxResult captchaImage() {
        try {
            String code = generateCode(4);
            String uuid = UUID.randomUUID().toString().replace("-", "");
            String key = CAPTCHA_KEY_PREFIX + uuid;

            // 1. 存储到 Redis（如有）
            if (stringRedisTemplate != null) {
                stringRedisTemplate.opsForValue().set(key, code.toLowerCase(), CAPTCHA_EXPIRE_SECONDS, TimeUnit.SECONDS);
            }

            // 2. 始终存储到内存缓存（兜底）
            CAPTCHA_CACHE.put(key, code.toLowerCase());
            CAPTCHA_CACHE_EXPIRY.put(key, System.currentTimeMillis() + CAPTCHA_EXPIRE_SECONDS * 1000);

            // 生成验证码图片（Base64）
            String imgBase64 = generateCaptchaImage(code);

            Map<String, Object> data = new HashMap<>();
            data.put("uuid", uuid);
            data.put("img", imgBase64);
            data.put("captchaEnabled", true);
            data.put("expire", CAPTCHA_EXPIRE_SECONDS);

            return AjaxResult.success(data);
        } catch (Exception e) {
            log.error("生成验证码失败", e);
            return AjaxResult.error("验证码生成失败: " + e.getMessage());
        }
    }

    /**
     * 校验验证码（不区分大小写）
     * 优先检查 Redis，Redis 不可用时检查内存缓存
     */
    private boolean validateCaptcha(String uuid, String code) {
        if (uuid == null || code == null) return false;

        String key = CAPTCHA_KEY_PREFIX + uuid;
        String input = code.trim().toLowerCase();

        // 1. 检查 Redis（如果配置了 Redis）
        if (stringRedisTemplate != null) {
            String stored = stringRedisTemplate.opsForValue().get(key);
            if (stored != null) {
                // 一次性使用：校验后立即删除
                stringRedisTemplate.delete(key);
                // 也删除内存缓存中的对应项
                CAPTCHA_CACHE.remove(key);
                CAPTCHA_CACHE_EXPIRY.remove(key);
                return stored.equals(input);
            }
            // Redis 中不存在，但可能已过期或被其他服务清理，继续检查内存缓存
        }

        // 2. 检查内存缓存（兜底）
        String stored = CAPTCHA_CACHE.get(key);
        if (stored == null) return false;

        // 一次性使用：校验后立即删除
        CAPTCHA_CACHE.remove(key);
        CAPTCHA_CACHE_EXPIRY.remove(key);
        return stored.equals(input);
    }

    @PostMapping("/login")
    @Operation(summary = "用户登录")
    public AjaxResult login(@Valid @RequestBody LoginBody loginBody) {
        try {
            // 1. 校验验证码（不通过直接返回错误）
            if (!validateCaptcha(loginBody.getUuid(), loginBody.getCode())) {
                return AjaxResult.error("验证码错误或已过期");
            }

            // 2. 用户名密码登录
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

    @PostMapping("/logout")
    @Operation(summary = "用户登出")
    public AjaxResult logout() {
        try {
            HttpServletRequest request = ServletUtils.getRequest();
            LoginUser loginUser = tokenService.getLoginUser(request);
            if (loginUser != null) {
                // 删除 Redis 中的 token
                tokenService.delLoginUser(loginUser.getToken());
            }
            return AjaxResult.success("登出成功");
        } catch (Exception e) {
            log.error("登出失败", e);
            return AjaxResult.error("登出失败: " + e.getMessage());
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

    // ========================= 验证码图片生成工具方法 =========================

    private static final char[] CODE_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ".toCharArray();

    private String generateCode(int length) {
        Random random = new Random();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < length; i++) {
            sb.append(CODE_CHARS[random.nextInt(CODE_CHARS.length)]);
        }
        return sb.toString();
    }

    private String generateCaptchaImage(String code) throws Exception {
        int width = 120;
        int height = 44;
        int fontSize = 28;

        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2d = image.createGraphics();

        // 抗锯齿
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

        // 背景渐变
        GradientPaint bg = new GradientPaint(0, 0, new Color(245, 248, 255), width, height, new Color(225, 235, 250));
        g2d.setPaint(bg);
        g2d.fillRect(0, 0, width, height);

        // 干扰线
        Random random = new Random();
        g2d.setStroke(new BasicStroke(1.0f));
        for (int i = 0; i < 6; i++) {
            g2d.setColor(new Color(180 + random.nextInt(50), 180 + random.nextInt(50), 180 + random.nextInt(50)));
            int x1 = random.nextInt(width);
            int y1 = random.nextInt(height);
            int x2 = random.nextInt(width);
            int y2 = random.nextInt(height);
            g2d.drawLine(x1, y1, x2, y2);
        }

        // 噪点
        for (int i = 0; i < 40; i++) {
            int x = random.nextInt(width);
            int y = random.nextInt(height);
            g2d.setColor(new Color(150 + random.nextInt(100), 150 + random.nextInt(100), 150 + random.nextInt(100)));
            g2d.fillRect(x, y, 1, 1);
        }

        // 字符
        Font font = new Font("Arial", Font.BOLD, fontSize);
        g2d.setFont(font);

        int charWidth = (width - 16) / code.length();
        for (int i = 0; i < code.length(); i++) {
            // 随机颜色
            g2d.setColor(new Color(
                30 + random.nextInt(80),
                60 + random.nextInt(80),
                120 + random.nextInt(100)
            ));
            char c = code.charAt(i);
            int x = 8 + i * charWidth + random.nextInt(4);
            int y = fontSize + random.nextInt(6) - 4;

            // 旋转角度
            double angle = (random.nextInt(60) - 30) * Math.PI / 180;
            AffineTransform transform = new AffineTransform();
            transform.rotate(angle, x, y);
            g2d.setTransform(transform);
            g2d.drawString(String.valueOf(c), x, y);
            g2d.setTransform(new AffineTransform());
        }

        g2d.dispose();

        // 输出为 Base64 PNG
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ImageIO.write(image, "png", baos);
        return "data:image/png;base64," + Base64.getEncoder().encodeToString(baos.toByteArray());
    }
}

package com.antifraudqi.antifraudaiagent.controller;

import com.antifraudqi.antifraudaiagent.common.CacheConstants;
import com.antifraudqi.antifraudaiagent.common.RedisCache;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * 验证码操作处理
 * 生成图形验证码，存储到 Redis
 */
@RestController
@Tag(name = "验证码管理", description = "验证码生成与获取")
public class CaptchaController {

    @Resource
    private RedisCache redisCache;

    @GetMapping("/v1/auth/captchaImage")
    @Operation(summary = "获取验证码")
    public Map<String, Object> getCode() {
        Map<String, Object> result = new HashMap<>();

        // 生成验证码
        String uuid = UUID.randomUUID().toString().replaceAll("-", "");
        String verifyKey = CacheConstants.CAPTCHA_CODE_KEY + uuid;

        // 生成 4 位数字验证码
        String code = String.format("%04d", (int) (Math.random() * 10000));
        String capStr = code;

        // 生成验证码图片
        BufferedImage image = createCaptchaImage(capStr);

        // 存储到 Redis，5 分钟过期
        redisCache.setCacheObject(verifyKey, code, CacheConstants.CAPTCHA_EXPIRATION, TimeUnit.MINUTES);

        // 转换为 Base64
        try {
            ByteArrayOutputStream os = new ByteArrayOutputStream();
            ImageIO.write(image, "png", os);
            String imgBase64 = Base64.getEncoder().encodeToString(os.toByteArray());

            result.put("success", true);
            result.put("uuid", uuid);
            result.put("img", "data:image/png;base64," + imgBase64);
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "验证码生成失败");
        }

        return result;
    }

    /**
     * 生成验证码图片
     */
    private BufferedImage createCaptchaImage(String code) {
        int width = 130;
        int height = 48;
        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = image.createGraphics();

        // 背景
        g.setColor(new Color(240, 243, 250));
        g.fillRect(0, 0, width, height);

        // 干扰线
        g.setColor(new Color(200, 210, 230));
        for (int i = 0; i < 5; i++) {
            int x1 = (int) (Math.random() * width);
            int y1 = (int) (Math.random() * height);
            int x2 = (int) (Math.random() * width);
            int y2 = (int) (Math.random() * height);
            g.drawLine(x1, y1, x2, y2);
        }

        // 干扰点
        g.setColor(new Color(180, 190, 210));
        for (int i = 0; i < 30; i++) {
            int x = (int) (Math.random() * width);
            int y = (int) (Math.random() * height);
            g.fillRect(x, y, 2, 2);
        }

        // 验证码文字
        g.setFont(new Font("Arial", Font.BOLD | Font.ITALIC, 28));
        for (int i = 0; i < code.length(); i++) {
            int r = 30 + (int) (Math.random() * 80);
            int gv = 30 + (int) (Math.random() * 80);
            int b = 30 + (int) (Math.random() * 80);
            g.setColor(new Color(r, gv, b));
            double angle = (Math.random() - 0.5) * 0.6;
            g.rotate(angle, 25 + i * 28, 30);
            g.drawString(String.valueOf(code.charAt(i)), 25 + i * 28, 34);
            g.rotate(-angle, 25 + i * 28, 30);
        }

        // 边框
        g.setColor(new Color(180, 190, 210));
        g.drawRect(0, 0, width - 1, height - 1);

        g.dispose();
        return image;
    }
}
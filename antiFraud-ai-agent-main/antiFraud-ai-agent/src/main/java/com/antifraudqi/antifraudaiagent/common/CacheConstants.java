package com.antifraudqi.antifraudaiagent.common;

/**
 * 缓存 Key 常量
 */
public class CacheConstants {

    /**
     * 登录用户 redis key
     */
    public static final String LOGIN_TOKEN_KEY = "login_tokens:";

    /**
     * 验证码 redis key
     */
    public static final String CAPTCHA_CODE_KEY = "captcha_codes:";

    /**
     * 验证码过期时间（分钟）
     */
    public static final long CAPTCHA_EXPIRATION = 5;
}
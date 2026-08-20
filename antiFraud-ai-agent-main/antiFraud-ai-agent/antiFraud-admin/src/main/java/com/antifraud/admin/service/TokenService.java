package com.antifraud.admin.service;

import com.antifraud.admin.domain.LoginUser;
import com.antifraud.admin.util.JwtUtil;
import com.antifraud.admin.util.ServletUtils;
import io.jsonwebtoken.Claims;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * JWT 令牌服务
 * 负责令牌的创建、验证、刷新和从请求中提取
 */
@Service
public class TokenService {

    @Resource
    private JwtUtil jwtUtil;

    @Value("${jwt.header:Authorization}")
    private String header;

    @Value("${jwt.token-prefix:Bearer }")
    private String tokenPrefix;

    /**
     * 创建令牌
     */
    public String createToken(LoginUser loginUser) {
        String token = jwtUtil.generateToken(loginUser.getUserId(), loginUser.getUsername(), loginUser.getRole());
        loginUser.setToken(token);
        return token;
    }

    /**
     * 从请求中获取 LoginUser
     */
    public LoginUser getLoginUser(HttpServletRequest request) {
        String token = getToken(request);
        if (token == null) {
            return null;
        }
        try {
            Claims claims = jwtUtil.parseToken(token);
            Long userId = claims.get("userId", Long.class);
            String username = claims.getSubject();
            String role = claims.get("role", String.class);

            LoginUser loginUser = new LoginUser();
            loginUser.setUserId(userId);
            loginUser.setUsername(username);
            loginUser.setRole(role);
            loginUser.setToken(token);
            return loginUser;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 验证令牌有效性
     */
    public boolean validateToken(LoginUser loginUser) {
        if (loginUser == null || loginUser.getToken() == null) {
            return false;
        }
        return jwtUtil.validateToken(loginUser.getToken());
    }

    /**
     * 从请求中提取令牌
     */
    private String getToken(HttpServletRequest request) {
        String authHeader = request.getHeader(header);
        if (authHeader != null && authHeader.startsWith(tokenPrefix)) {
            return authHeader.substring(tokenPrefix.length());
        }
        return null;
    }
}
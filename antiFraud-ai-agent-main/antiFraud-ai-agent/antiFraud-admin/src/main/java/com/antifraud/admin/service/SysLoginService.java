package com.antifraud.admin.service;

import com.antifraud.admin.domain.LoginUser;
import com.antifraud.admin.domain.SysUser;
import com.antifraud.admin.mapper.SysUserMapper;
import jakarta.annotation.Resource;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * 登录服务
 */
@Service
public class SysLoginService {

    @Resource
    private SysUserMapper sysUserMapper;

    @Resource
    private PasswordEncoder passwordEncoder;

    @Resource
    private TokenService tokenService;

    /**
     * 用户登录认证
     *
     * @param username 用户名
     * @param password 密码
     * @return 登录用户信息
     */
    public LoginUser login(String username, String password) {
        // 查询用户
        SysUser user = sysUserMapper.selectUserByUsername(username);
        if (user == null) {
            throw new RuntimeException("用户名或密码错误");
        }

        // 校验状态
        if (user.getStatus() == null || user.getStatus() == 0) {
            throw new RuntimeException("账号已被禁用");
        }

        // 校验密码
        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new RuntimeException("用户名或密码错误");
        }

        // 更新最后登录时间
        sysUserMapper.updateLastLoginTime(user.getId());

        // 构建 LoginUser
        LoginUser loginUser = new LoginUser();
        loginUser.setUserId(user.getId());
        loginUser.setUsername(user.getUsername());
        loginUser.setRole(user.getRole());

        // 生成令牌
        tokenService.createToken(loginUser);

        return loginUser;
    }
}
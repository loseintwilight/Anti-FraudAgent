package com.antifraudqi.antifraudaiagent.service;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * 黑名单服务
 * 管理用户的黑名单条目，支持添加、移除和检查操作
 * 当前使用内存存储，后续可迁移到数据库表
 */
@Slf4j
@Service
public class BlacklistService {

    /** 黑名单存储结构：userId -> Set<黑名单内容> */
    private final Map<String, Set<String>> blacklistMap = new ConcurrentHashMap<>();

    /** 全局黑名单（所有用户共享） */
    private final Set<String> globalBlacklist = ConcurrentHashMap.newKeySet();

    @PostConstruct
    public void init() {
        log.info("黑名单服务初始化完成（内存模式）");
    }

    /**
     * 添加条目到黑名单
     *
     * @param userId  用户ID
     * @param content 黑名单内容（电话号码、URL、账号等）
     * @param type    类型（预留参数，可用于后续分类）
     */
    public void addToBlacklist(String userId, String content, String type) {
        blacklistMap.computeIfAbsent(userId, k -> ConcurrentHashMap.newKeySet()).add(content);
        globalBlacklist.add(content);
        log.info("黑名单添加成功: userId={}, content={}, type={}", userId, content, type);
    }

    /**
     * 检查内容是否在黑名单中
     *
     * @param content 待检查的内容
     * @return true 表示在黑名单中
     */
    public boolean isBlacklisted(String content) {
        return globalBlacklist.contains(content);
    }

    /**
     * 从黑名单中移除条目
     *
     * @param userId  用户ID
     * @param content 要移除的内容
     */
    public void removeFromBlacklist(String userId, String content) {
        Set<String> userBlacklist = blacklistMap.get(userId);
        if (userBlacklist != null) {
            userBlacklist.remove(content);
            if (userBlacklist.isEmpty()) {
                blacklistMap.remove(userId);
            }
        }
        globalBlacklist.remove(content);
        log.info("黑名单移除成功: userId={}, content={}", userId, content);
    }

    /**
     * 查询用户的所有黑名单条目
     *
     * @param userId 用户ID
     * @return 黑名单条目列表
     */
    public List<String> getUserBlacklist(String userId) {
        Set<String> userBlacklist = blacklistMap.get(userId);
        if (userBlacklist == null) {
            return Collections.emptyList();
        }
        return new ArrayList<>(userBlacklist);
    }
}

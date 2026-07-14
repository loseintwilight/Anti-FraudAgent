package com.antifraudqi.antifraudaiagent.controller;

import com.antifraudqi.antifraudaiagent.service.BlacklistService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 黑名单接口
 * 提供黑名单的添加、移除和查询功能
 */
@Slf4j
@RestController
@RequestMapping("/blacklist")
public class BlacklistController {

    @Resource
    private BlacklistService blacklistService;

    /**
     * 添加条目到黑名单
     * 请求体包含：userId, content, type
     *
     * @param request 包含 userId, content, type 的请求参数
     * @return 操作结果
     */
    @PostMapping("/add")
    public Map<String, Object> addToBlacklist(@RequestBody Map<String, Object> request) {
        Map<String, Object> result = new HashMap<>();
        try {
            String userId = (String) request.get("userId");
            String content = (String) request.get("content");
            String type = (String) request.getOrDefault("type", "");

            if (userId == null || content == null) {
                result.put("success", false);
                result.put("error", "userId 和 content 不能为空");
                return result;
            }

            blacklistService.addToBlacklist(userId, content, type);
            result.put("success", true);
            result.put("message", "黑名单添加成功");
        } catch (Exception e) {
            log.error("添加黑名单失败", e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }

    /**
     * 从黑名单中移除条目
     * 请求体包含：userId, content
     *
     * @param request 包含 userId, content 的请求参数
     * @return 操作结果
     */
    @DeleteMapping("/remove")
    public Map<String, Object> removeFromBlacklist(@RequestBody Map<String, Object> request) {
        Map<String, Object> result = new HashMap<>();
        try {
            String userId = (String) request.get("userId");
            String content = (String) request.get("content");

            if (userId == null || content == null) {
                result.put("success", false);
                result.put("error", "userId 和 content 不能为空");
                return result;
            }

            blacklistService.removeFromBlacklist(userId, content);
            result.put("success", true);
            result.put("message", "黑名单移除成功");
        } catch (Exception e) {
            log.error("移除黑名单失败", e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }

    /**
     * 查询用户的黑名单列表
     *
     * @param userId 用户ID
     * @return 黑名单条目列表
     */
    @GetMapping("/list")
    public Map<String, Object> getBlacklist(@RequestParam String userId) {
        Map<String, Object> result = new HashMap<>();
        try {
            List<String> blacklist = blacklistService.getUserBlacklist(userId);
            result.put("success", true);
            result.put("data", blacklist);
            result.put("count", blacklist.size());
        } catch (Exception e) {
            log.error("查询黑名单失败: userId={}", userId, e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }
}

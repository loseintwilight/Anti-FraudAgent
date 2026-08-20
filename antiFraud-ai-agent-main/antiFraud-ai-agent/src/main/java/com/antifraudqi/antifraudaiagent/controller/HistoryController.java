package com.antifraudqi.antifraudaiagent.controller;

import com.antifraudqi.antifraudaiagent.model.entity.DetectionHistory;
import com.antifraudqi.antifraudaiagent.service.HistoryService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 历史记录接口
 * 提供检测历史的分页查询、收藏切换和删除功能
 */
@Slf4j
@RestController
@RequestMapping("/history")
public class HistoryController {

    @Resource
    private HistoryService historyService;

    /**
     * 分页查询用户的检测历史
     *
     * @param userId 用户ID
     * @param page   页码（从0开始）
     * @param size   每页条数
     * @return 包含分页数据的响应
     */
    @GetMapping("/list")
    public Map<String, Object> getHistory(
            @RequestParam String userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Map<String, Object> result = new HashMap<>();
        try {
            Page<DetectionHistory> historyPage = historyService.getHistory(userId, PageRequest.of(page, size));
            result.put("success", true);
            result.put("data", historyPage.getContent());
            result.put("total", historyPage.getTotalElements());
            result.put("page", historyPage.getNumber());
            result.put("size", historyPage.getSize());
            result.put("totalPages", historyPage.getTotalPages());
        } catch (Exception e) {
            log.error("查询检测历史失败: userId={}", userId, e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }

    /**
     * 切换检测历史的收藏状态
     *
     * @param historyId 检测历史ID
     * @return 操作结果
     */
    @PostMapping("/favorite")
    public Map<String, Object> toggleFavorite(@RequestParam Long historyId) {
        Map<String, Object> result = new HashMap<>();
        try {
            DetectionHistory history = historyService.toggleFavorite(historyId);
            result.put("success", true);
            result.put("data", history);
            result.put("isFavorited", history.isFavorited());
        } catch (Exception e) {
            log.error("切换收藏状态失败: historyId={}", historyId, e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }

    /**
     * 删除检测历史记录
     *
     * @param historyId 检测历史ID
     * @return 操作结果
     */
    @DeleteMapping("/{historyId}")
    public Map<String, Object> deleteHistory(@PathVariable Long historyId) {
        Map<String, Object> result = new HashMap<>();
        try {
            historyService.deleteHistory(historyId);
            result.put("success", true);
            result.put("message", "删除成功");
        } catch (Exception e) {
            log.error("删除检测历史失败: historyId={}", historyId, e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }
}

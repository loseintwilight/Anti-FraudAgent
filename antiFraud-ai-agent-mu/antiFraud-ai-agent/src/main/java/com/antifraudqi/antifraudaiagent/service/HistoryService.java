package com.antifraudqi.antifraudaiagent.service;

import com.antifraudqi.antifraudaiagent.model.entity.DetectionHistory;
import com.antifraudqi.antifraudaiagent.repository.DetectionHistoryRepository;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 历史记录服务
 * 管理用户的检测历史，支持分页查询、收藏切换和删除操作
 */
@Slf4j
@Service
public class HistoryService {

    @Resource
    private DetectionHistoryRepository detectionHistoryRepository;

    /**
     * 分页查询用户的检测历史
     *
     * @param userId   用户ID
     * @param pageable 分页参数
     * @return 分页后的检测历史列表
     */
    public Page<DetectionHistory> getHistory(String userId, Pageable pageable) {
        List<DetectionHistory> allHistory = detectionHistoryRepository.findByUserIdOrderByCreatedAtDesc(userId);

        // 手动分页
        int start = (int) pageable.getOffset();
        int end = Math.min((start + pageable.getPageSize()), allHistory.size());

        if (start > allHistory.size()) {
            return Page.empty(pageable);
        }

        List<DetectionHistory> pageContent = allHistory.subList(start, end);
        return new PageImpl<>(pageContent, pageable, allHistory.size());
    }

    /**
     * 切换检测历史的收藏状态
     *
     * @param historyId 检测历史ID
     * @return 更新后的检测历史实体
     */
    public DetectionHistory toggleFavorite(Long historyId) {
        DetectionHistory history = detectionHistoryRepository.findById(historyId)
                .orElseThrow(() -> new RuntimeException("检测历史记录不存在: " + historyId));

        history.setFavorited(!history.isFavorited());
        DetectionHistory updated = detectionHistoryRepository.save(history);
        log.info("收藏状态切换成功: historyId={}, isFavorited={}", historyId, updated.isFavorited());
        return updated;
    }

    /**
     * 删除检测历史记录
     *
     * @param historyId 检测历史ID
     */
    public void deleteHistory(Long historyId) {
        if (!detectionHistoryRepository.existsById(historyId)) {
            throw new RuntimeException("检测历史记录不存在: " + historyId);
        }
        detectionHistoryRepository.deleteById(historyId);
        log.info("检测历史记录删除成功: historyId={}", historyId);
    }
}

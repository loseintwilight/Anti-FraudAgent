package com.antifraudqi.antifraudaiagent.repository;

import com.antifraudqi.antifraudaiagent.model.entity.DetectionHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 检测历史数据访问接口
 */
@Repository
public interface DetectionHistoryRepository extends JpaRepository<DetectionHistory, Long> {

    /**
     * 根据用户ID查询检测历史，按创建时间降序排列
     */
    List<DetectionHistory> findByUserIdOrderByCreatedAtDesc(String userId);

    /**
     * 查询用户收藏的检测历史
     */
    List<DetectionHistory> findByUserIdAndIsFavoritedTrue(String userId);
}

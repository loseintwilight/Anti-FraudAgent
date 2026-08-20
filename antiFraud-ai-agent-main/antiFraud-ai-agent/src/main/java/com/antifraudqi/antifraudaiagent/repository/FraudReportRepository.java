package com.antifraudqi.antifraudaiagent.repository;

import com.antifraudqi.antifraudaiagent.model.entity.FraudReport;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 反诈报告数据访问接口
 */
@Repository
public interface FraudReportRepository extends JpaRepository<FraudReport, Long> {

    /**
     * 根据用户ID查询所有反诈报告
     */
    List<FraudReport> findByUserId(String userId);

    /**
     * 根据报告唯一标识查询报告
     */
    Optional<FraudReport> findByReportId(String reportId);
}

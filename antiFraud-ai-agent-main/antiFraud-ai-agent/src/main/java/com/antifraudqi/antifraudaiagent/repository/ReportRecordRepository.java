package com.antifraudqi.antifraudaiagent.repository;

import com.antifraudqi.antifraudaiagent.model.entity.ReportRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 举报记录数据访问接口
 */
@Repository
public interface ReportRecordRepository extends JpaRepository<ReportRecord, Long> {

    /**
     * 根据用户ID查询所有举报记录
     */
    List<ReportRecord> findByUserId(String userId);
}

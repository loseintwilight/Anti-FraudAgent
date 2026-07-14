package com.antifraudqi.antifraudaiagent.repository;

import com.antifraudqi.antifraudaiagent.model.entity.UserProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * 用户画像数据访问接口
 */
@Repository
public interface UserProfileRepository extends JpaRepository<UserProfile, Long> {

    /**
     * 根据用户ID查询用户画像
     */
    Optional<UserProfile> findByUserId(String userId);
}

package com.antifraudqi.antifraudaiagent.repository;

import com.antifraudqi.antifraudaiagent.model.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /** 根据用户名查找用户 */
    Optional<User> findByUsername(String username);

    /** 判断用户名是否已存在 */
    boolean existsByUsername(String username);
}
package com.antifraud.admin.service.impl;

import com.antifraud.admin.domain.UserProfile;
import com.antifraud.admin.mapper.UserProfileMapper;
import com.antifraud.admin.service.IUserProfileService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 用户画像Service业务层处理
 * 
 * @author antiFraud
 */
@Service
public class UserProfileServiceImpl implements IUserProfileService
{
    @Resource
    private UserProfileMapper userProfileMapper;

    /**
     * 查询用户画像
     * 
     * @param id 用户画像主键
     * @return 用户画像
     */
    @Override
    public UserProfile selectUserProfileById(Long id)
    {
        return userProfileMapper.selectUserProfileById(id);
    }

    /**
     * 查询用户画像列表
     * 
     * @param profile 用户画像
     * @return 用户画像
     */
    @Override
    public List<UserProfile> selectUserProfileList(UserProfile profile)
    {
        return userProfileMapper.selectUserProfileList(profile);
    }

    /**
     * 新增用户画像
     * 
     * @param profile 用户画像
     * @return 结果
     */
    @Override
    public int insertUserProfile(UserProfile profile)
    {
        return userProfileMapper.insertUserProfile(profile);
    }

    /**
     * 修改用户画像
     * 
     * @param profile 用户画像
     * @return 结果
     */
    @Override
    public int updateUserProfile(UserProfile profile)
    {
        return userProfileMapper.updateUserProfile(profile);
    }

    /**
     * 批量删除用户画像
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    @Override
    public int deleteUserProfileByIds(Long[] ids)
    {
        return userProfileMapper.deleteUserProfileByIds(ids);
    }

    /**
     * 删除用户画像信息
     * 
     * @param id 用户画像主键
     * @return 结果
     */
    @Override
    public int deleteUserProfileById(Long id)
    {
        return userProfileMapper.deleteUserProfileById(id);
    }
}
package com.antifraud.admin.service;

import com.antifraud.admin.domain.UserProfile;
import java.util.List;

/**
 * 用户画像Service接口
 * 
 * @author antiFraud
 */
public interface IUserProfileService
{
    /**
     * 查询用户画像
     * 
     * @param id 用户画像主键
     * @return 用户画像
     */
    public UserProfile selectUserProfileById(Long id);

    /**
     * 查询用户画像列表
     * 
     * @param profile 用户画像
     * @return 用户画像集合
     */
    public List<UserProfile> selectUserProfileList(UserProfile profile);

    /**
     * 新增用户画像
     * 
     * @param profile 用户画像
     * @return 结果
     */
    public int insertUserProfile(UserProfile profile);

    /**
     * 修改用户画像
     * 
     * @param profile 用户画像
     * @return 结果
     */
    public int updateUserProfile(UserProfile profile);

    /**
     * 批量删除用户画像
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteUserProfileByIds(Long[] ids);

    /**
     * 删除用户画像信息
     * 
     * @param id 用户画像主键
     * @return 结果
     */
    public int deleteUserProfileById(Long id);
}
package com.antifraud.admin.mapper;

import com.antifraud.admin.domain.UserProfile;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 用户画像Mapper接口
 * 
 * @author antiFraud
 */
@Mapper
public interface UserProfileMapper
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
     * 删除用户画像
     * 
     * @param id 用户画像主键
     * @return 结果
     */
    public int deleteUserProfileById(Long id);

    /**
     * 批量删除用户画像
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteUserProfileByIds(Long[] ids);
}
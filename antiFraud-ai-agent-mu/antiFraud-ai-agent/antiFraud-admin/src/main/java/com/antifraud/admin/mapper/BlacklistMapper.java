package com.antifraud.admin.mapper;

import com.antifraud.admin.domain.Blacklist;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 黑名单Mapper接口
 * 
 * @author antiFraud
 */
@Mapper
public interface BlacklistMapper
{
    /**
     * 查询黑名单
     * 
     * @param id 黑名单主键
     * @return 黑名单
     */
    public Blacklist selectBlacklistById(Long id);

    /**
     * 查询黑名单列表
     * 
     * @param blacklist 黑名单
     * @return 黑名单集合
     */
    public List<Blacklist> selectBlacklistList(Blacklist blacklist);

    /**
     * 新增黑名单
     * 
     * @param blacklist 黑名单
     * @return 结果
     */
    public int insertBlacklist(Blacklist blacklist);

    /**
     * 修改黑名单
     * 
     * @param blacklist 黑名单
     * @return 结果
     */
    public int updateBlacklist(Blacklist blacklist);

    /**
     * 删除黑名单
     * 
     * @param id 黑名单主键
     * @return 结果
     */
    public int deleteBlacklistById(Long id);

    /**
     * 批量删除黑名单
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteBlacklistByIds(Long[] ids);
}
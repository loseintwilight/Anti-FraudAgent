package com.antifraud.admin.service.impl;

import com.antifraud.admin.domain.Blacklist;
import com.antifraud.admin.mapper.BlacklistMapper;
import com.antifraud.admin.service.IBlacklistService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 黑名单Service业务层处理
 * 
 * @author antiFraud
 */
@Service
public class BlacklistServiceImpl implements IBlacklistService
{
    @Resource
    private BlacklistMapper blacklistMapper;

    /**
     * 查询黑名单
     * 
     * @param id 黑名单主键
     * @return 黑名单
     */
    @Override
    public Blacklist selectBlacklistById(Long id)
    {
        return blacklistMapper.selectBlacklistById(id);
    }

    /**
     * 查询黑名单列表
     * 
     * @param blacklist 黑名单
     * @return 黑名单
     */
    @Override
    public List<Blacklist> selectBlacklistList(Blacklist blacklist)
    {
        return blacklistMapper.selectBlacklistList(blacklist);
    }

    /**
     * 新增黑名单
     * 
     * @param blacklist 黑名单
     * @return 结果
     */
    @Override
    public int insertBlacklist(Blacklist blacklist)
    {
        return blacklistMapper.insertBlacklist(blacklist);
    }

    /**
     * 修改黑名单
     * 
     * @param blacklist 黑名单
     * @return 结果
     */
    @Override
    public int updateBlacklist(Blacklist blacklist)
    {
        return blacklistMapper.updateBlacklist(blacklist);
    }

    /**
     * 批量删除黑名单
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    @Override
    public int deleteBlacklistByIds(Long[] ids)
    {
        return blacklistMapper.deleteBlacklistByIds(ids);
    }

    /**
     * 删除黑名单信息
     * 
     * @param id 黑名单主键
     * @return 结果
     */
    @Override
    public int deleteBlacklistById(Long id)
    {
        return blacklistMapper.deleteBlacklistById(id);
    }
}
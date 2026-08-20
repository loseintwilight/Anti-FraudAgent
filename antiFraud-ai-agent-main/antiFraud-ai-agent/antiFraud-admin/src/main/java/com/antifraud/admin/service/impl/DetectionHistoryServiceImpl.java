package com.antifraud.admin.service.impl;

import com.antifraud.admin.domain.DetectionHistory;
import com.antifraud.admin.mapper.DetectionHistoryMapper;
import com.antifraud.admin.service.IDetectionHistoryService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 检测记录Service业务层处理
 * 
 * @author antiFraud
 */
@Service
public class DetectionHistoryServiceImpl implements IDetectionHistoryService
{
    @Resource
    private DetectionHistoryMapper detectionHistoryMapper;

    /**
     * 查询检测记录
     * 
     * @param id 检测记录主键
     * @return 检测记录
     */
    @Override
    public DetectionHistory selectDetectionHistoryById(Long id)
    {
        return detectionHistoryMapper.selectDetectionHistoryById(id);
    }

    /**
     * 查询检测记录列表
     * 
     * @param history 检测记录
     * @return 检测记录
     */
    @Override
    public List<DetectionHistory> selectDetectionHistoryList(DetectionHistory history)
    {
        return detectionHistoryMapper.selectDetectionHistoryList(history);
    }

    /**
     * 新增检测记录
     * 
     * @param history 检测记录
     * @return 结果
     */
    @Override
    public int insertDetectionHistory(DetectionHistory history)
    {
        return detectionHistoryMapper.insertDetectionHistory(history);
    }

    /**
     * 修改检测记录
     * 
     * @param history 检测记录
     * @return 结果
     */
    @Override
    public int updateDetectionHistory(DetectionHistory history)
    {
        return detectionHistoryMapper.updateDetectionHistory(history);
    }

    /**
     * 批量删除检测记录
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    @Override
    public int deleteDetectionHistoryByIds(Long[] ids)
    {
        return detectionHistoryMapper.deleteDetectionHistoryByIds(ids);
    }

    /**
     * 删除检测记录信息
     * 
     * @param id 检测记录主键
     * @return 结果
     */
    @Override
    public int deleteDetectionHistoryById(Long id)
    {
        return detectionHistoryMapper.deleteDetectionHistoryById(id);
    }
}
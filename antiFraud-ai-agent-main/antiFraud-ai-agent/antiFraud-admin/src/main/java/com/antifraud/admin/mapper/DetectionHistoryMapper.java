package com.antifraud.admin.mapper;

import com.antifraud.admin.domain.DetectionHistory;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * 检测记录Mapper接口
 * 
 * @author antiFraud
 */
@Mapper
public interface DetectionHistoryMapper
{
    /**
     * 查询检测记录
     * 
     * @param id 检测记录主键
     * @return 检测记录
     */
    public DetectionHistory selectDetectionHistoryById(Long id);

    /**
     * 查询检测记录列表
     * 
     * @param history 检测记录
     * @return 检测记录集合
     */
    public List<DetectionHistory> selectDetectionHistoryList(DetectionHistory history);

    /**
     * 新增检测记录
     * 
     * @param history 检测记录
     * @return 结果
     */
    public int insertDetectionHistory(DetectionHistory history);

    /**
     * 修改检测记录
     * 
     * @param history 检测记录
     * @return 结果
     */
    public int updateDetectionHistory(DetectionHistory history);

    /**
     * 删除检测记录
     * 
     * @param id 检测记录主键
     * @return 结果
     */
    public int deleteDetectionHistoryById(Long id);

    /**
     * 批量删除检测记录
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteDetectionHistoryByIds(Long[] ids);
}
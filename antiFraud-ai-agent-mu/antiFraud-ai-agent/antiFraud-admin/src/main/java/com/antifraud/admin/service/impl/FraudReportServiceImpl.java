package com.antifraud.admin.service.impl;

import com.antifraud.admin.domain.FraudReport;
import com.antifraud.admin.mapper.FraudReportMapper;
import com.antifraud.admin.service.IFraudReportService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 反诈报告Service业务层处理
 * 
 * @author antiFraud
 */
@Service
public class FraudReportServiceImpl implements IFraudReportService
{
    @Resource
    private FraudReportMapper fraudReportMapper;

    /**
     * 查询反诈报告
     * 
     * @param id 反诈报告主键
     * @return 反诈报告
     */
    @Override
    public FraudReport selectFraudReportById(Long id)
    {
        return fraudReportMapper.selectFraudReportById(id);
    }

    /**
     * 查询反诈报告列表
     * 
     * @param report 反诈报告
     * @return 反诈报告
     */
    @Override
    public List<FraudReport> selectFraudReportList(FraudReport report)
    {
        return fraudReportMapper.selectFraudReportList(report);
    }

    /**
     * 新增反诈报告
     * 
     * @param report 反诈报告
     * @return 结果
     */
    @Override
    public int insertFraudReport(FraudReport report)
    {
        return fraudReportMapper.insertFraudReport(report);
    }

    /**
     * 修改反诈报告
     * 
     * @param report 反诈报告
     * @return 结果
     */
    @Override
    public int updateFraudReport(FraudReport report)
    {
        return fraudReportMapper.updateFraudReport(report);
    }

    /**
     * 批量删除反诈报告
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    @Override
    public int deleteFraudReportByIds(Long[] ids)
    {
        return fraudReportMapper.deleteFraudReportByIds(ids);
    }

    /**
     * 删除反诈报告信息
     * 
     * @param id 反诈报告主键
     * @return 结果
     */
    @Override
    public int deleteFraudReportById(Long id)
    {
        return fraudReportMapper.deleteFraudReportById(id);
    }
}
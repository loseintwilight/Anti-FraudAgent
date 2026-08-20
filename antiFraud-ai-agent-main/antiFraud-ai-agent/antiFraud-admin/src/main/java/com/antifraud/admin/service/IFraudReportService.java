package com.antifraud.admin.service;

import com.antifraud.admin.domain.FraudReport;
import java.util.List;

/**
 * 反诈报告Service接口
 * 
 * @author antiFraud
 */
public interface IFraudReportService
{
    /**
     * 查询反诈报告
     * 
     * @param id 反诈报告主键
     * @return 反诈报告
     */
    public FraudReport selectFraudReportById(Long id);

    /**
     * 查询反诈报告列表
     * 
     * @param report 反诈报告
     * @return 反诈报告集合
     */
    public List<FraudReport> selectFraudReportList(FraudReport report);

    /**
     * 新增反诈报告
     * 
     * @param report 反诈报告
     * @return 结果
     */
    public int insertFraudReport(FraudReport report);

    /**
     * 修改反诈报告
     * 
     * @param report 反诈报告
     * @return 结果
     */
    public int updateFraudReport(FraudReport report);

    /**
     * 批量删除反诈报告
     * 
     * @param ids 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteFraudReportByIds(Long[] ids);

    /**
     * 删除反诈报告信息
     * 
     * @param id 反诈报告主键
     * @return 结果
     */
    public int deleteFraudReportById(Long id);
}
package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.FraudReport;
import com.antifraud.admin.service.IFraudReportService;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import jakarta.validation.Valid;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 反诈报告Controller
 * 
 * @author antiFraud
 */
@RestController
@RequestMapping("/api/v1/report")
@Tag(name = "反诈报告管理", description = "报告查询与删除")
public class FraudReportController
{
    @Resource
    private IFraudReportService fraudReportService;

    /**
     * 查询反诈报告列表
     */
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/list")
    @Operation(summary = "报告列表")
    public AjaxResult list(FraudReport report,
                           @RequestParam(defaultValue = "1") int pageNum,
                           @RequestParam(defaultValue = "10") int pageSize)
    {
        PageHelper.startPage(pageNum, pageSize);
        List<FraudReport> list = fraudReportService.selectFraudReportList(report);
        PageInfo<FraudReport> pageInfo = new PageInfo<>(list);
        return AjaxResult.success(pageInfo);
    }

    /**
     * 获取反诈报告详细信息
     */
    @PreAuthorize("hasRole('admin')")
    @GetMapping(value = "/{id}")
    @Operation(summary = "报告详情")
    public AjaxResult getInfo(@PathVariable Long id)
    {
        FraudReport report = fraudReportService.selectFraudReportById(id);
        return report != null ? AjaxResult.success(report) : AjaxResult.error("报告不存在");
    }

    /**
     * 新增反诈报告
     */
    @PreAuthorize("hasRole('admin')")
    @PostMapping
    @Operation(summary = "新增报告")
    public AjaxResult add(@Valid @RequestBody FraudReport report)
    {
        int result = fraudReportService.insertFraudReport(report);
        return result > 0 ? AjaxResult.success("新增成功") : AjaxResult.error("新增失败");
    }

    /**
     * 修改反诈报告
     */
    @PreAuthorize("hasRole('admin')")
    @PutMapping
    @Operation(summary = "修改报告")
    public AjaxResult edit(@Valid @RequestBody FraudReport report)
    {
        int result = fraudReportService.updateFraudReport(report);
        return result > 0 ? AjaxResult.success("修改成功") : AjaxResult.error("修改失败");
    }

    /**
     * 删除反诈报告
     */
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/{id}")
    @Operation(summary = "删除报告")
    public AjaxResult remove(@PathVariable Long id)
    {
        int result = fraudReportService.deleteFraudReportById(id);
        return result > 0 ? AjaxResult.success("删除成功") : AjaxResult.error("删除失败");
    }
}
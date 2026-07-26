package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.DetectionHistory;
import com.antifraud.admin.service.IDetectionHistoryService;
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
 * 检测记录Controller
 * 
 * @author antiFraud
 */
@RestController
@RequestMapping("/api/v1/detection")
@Tag(name = "检测记录管理", description = "检测记录查询与删除")
public class DetectionHistoryController
{
    @Resource
    private IDetectionHistoryService detectionHistoryService;

    /**
     * 查询检测记录列表
     */
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/list")
    @Operation(summary = "检测记录列表")
    public AjaxResult list(DetectionHistory history,
                           @RequestParam(defaultValue = "1") int pageNum,
                           @RequestParam(defaultValue = "10") int pageSize)
    {
        PageHelper.startPage(pageNum, pageSize);
        List<DetectionHistory> list = detectionHistoryService.selectDetectionHistoryList(history);
        PageInfo<DetectionHistory> pageInfo = new PageInfo<>(list);
        return AjaxResult.success(pageInfo);
    }

    /**
     * 获取检测记录详细信息
     */
    @PreAuthorize("hasRole('admin')")
    @GetMapping(value = "/{id}")
    @Operation(summary = "检测记录详情")
    public AjaxResult getInfo(@PathVariable Long id)
    {
        DetectionHistory history = detectionHistoryService.selectDetectionHistoryById(id);
        return history != null ? AjaxResult.success(history) : AjaxResult.error("记录不存在");
    }

    /**
     * 新增检测记录
     */
    @PreAuthorize("hasRole('admin')")
    @PostMapping
    @Operation(summary = "新增检测记录")
    public AjaxResult add(@Valid @RequestBody DetectionHistory history)
    {
        int result = detectionHistoryService.insertDetectionHistory(history);
        return result > 0 ? AjaxResult.success("新增成功") : AjaxResult.error("新增失败");
    }

    /**
     * 修改检测记录
     */
    @PreAuthorize("hasRole('admin')")
    @PutMapping
    @Operation(summary = "修改检测记录")
    public AjaxResult edit(@Valid @RequestBody DetectionHistory history)
    {
        int result = detectionHistoryService.updateDetectionHistory(history);
        return result > 0 ? AjaxResult.success("修改成功") : AjaxResult.error("修改失败");
    }

    /**
     * 删除检测记录
     */
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/{id}")
    @Operation(summary = "删除检测记录")
    public AjaxResult remove(@PathVariable Long id)
    {
        int result = detectionHistoryService.deleteDetectionHistoryById(id);
        return result > 0 ? AjaxResult.success("删除成功") : AjaxResult.error("删除失败");
    }
}
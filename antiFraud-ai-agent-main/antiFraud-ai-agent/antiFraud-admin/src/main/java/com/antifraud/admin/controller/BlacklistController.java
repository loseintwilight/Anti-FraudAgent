package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.Blacklist;
import com.antifraud.admin.service.IBlacklistService;
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
 * 黑名单Controller
 * 
 * @author antiFraud
 */
@RestController
@RequestMapping("/api/v1/blacklist")
@Tag(name = "黑名单管理", description = "黑名单增删改查")
public class BlacklistController
{
    @Resource
    private IBlacklistService blacklistService;

    /**
     * 查询黑名单列表
     */
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/list")
    @Operation(summary = "黑名单列表")
    public AjaxResult list(Blacklist blacklist,
                           @RequestParam(defaultValue = "1") int pageNum,
                           @RequestParam(defaultValue = "10") int pageSize)
    {
        PageHelper.startPage(pageNum, pageSize);
        List<Blacklist> list = blacklistService.selectBlacklistList(blacklist);
        PageInfo<Blacklist> pageInfo = new PageInfo<>(list);
        return AjaxResult.success(pageInfo);
    }

    /**
     * 获取黑名单详细信息
     */
    @PreAuthorize("hasRole('admin')")
    @GetMapping(value = "/{id}")
    @Operation(summary = "黑名单详情")
    public AjaxResult getInfo(@PathVariable Long id)
    {
        Blacklist blacklist = blacklistService.selectBlacklistById(id);
        return blacklist != null ? AjaxResult.success(blacklist) : AjaxResult.error("记录不存在");
    }

    /**
     * 新增黑名单
     */
    @PreAuthorize("hasRole('admin')")
    @PostMapping
    @Operation(summary = "新增黑名单")
    public AjaxResult add(@Valid @RequestBody Blacklist blacklist)
    {
        int result = blacklistService.insertBlacklist(blacklist);
        return result > 0 ? AjaxResult.success("新增成功") : AjaxResult.error("新增失败");
    }

    /**
     * 修改黑名单
     */
    @PreAuthorize("hasRole('admin')")
    @PutMapping
    @Operation(summary = "修改黑名单")
    public AjaxResult edit(@Valid @RequestBody Blacklist blacklist)
    {
        int result = blacklistService.updateBlacklist(blacklist);
        return result > 0 ? AjaxResult.success("修改成功") : AjaxResult.error("修改失败");
    }

    /**
     * 启用/禁用黑名单
     */
    @PreAuthorize("hasRole('admin')")
    @PutMapping("/status")
    @Operation(summary = "启用/禁用黑名单")
    public AjaxResult editStatus(@RequestBody Blacklist blacklist)
    {
        int result = blacklistService.updateBlacklist(blacklist);
        return result > 0 ? AjaxResult.success("操作成功") : AjaxResult.error("操作失败");
    }

    /**
     * 删除黑名单
     */
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/{id}")
    @Operation(summary = "删除黑名单")
    public AjaxResult remove(@PathVariable Long id)
    {
        int result = blacklistService.deleteBlacklistById(id);
        return result > 0 ? AjaxResult.success("删除成功") : AjaxResult.error("删除失败");
    }
}
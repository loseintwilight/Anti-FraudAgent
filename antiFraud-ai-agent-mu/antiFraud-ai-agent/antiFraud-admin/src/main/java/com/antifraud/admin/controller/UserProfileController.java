package com.antifraud.admin.controller;

import com.antifraud.admin.domain.AjaxResult;
import com.antifraud.admin.domain.UserProfile;
import com.antifraud.admin.service.IUserProfileService;
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
 * 用户画像Controller
 * 
 * @author antiFraud
 */
@RestController
@RequestMapping("/api/v1/profile")
@Tag(name = "用户画像管理", description = "用户画像查询")
public class UserProfileController
{
    @Resource
    private IUserProfileService userProfileService;

    /**
     * 查询用户画像列表
     */
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/list")
    @Operation(summary = "用户画像列表")
    public AjaxResult list(UserProfile profile,
                           @RequestParam(defaultValue = "1") int pageNum,
                           @RequestParam(defaultValue = "10") int pageSize)
    {
        PageHelper.startPage(pageNum, pageSize);
        List<UserProfile> list = userProfileService.selectUserProfileList(profile);
        PageInfo<UserProfile> pageInfo = new PageInfo<>(list);
        return AjaxResult.success(pageInfo);
    }

    /**
     * 获取用户画像详细信息
     */
    @PreAuthorize("hasRole('admin')")
    @GetMapping(value = "/{id}")
    @Operation(summary = "用户画像详情")
    public AjaxResult getInfo(@PathVariable Long id)
    {
        UserProfile profile = userProfileService.selectUserProfileById(id);
        return profile != null ? AjaxResult.success(profile) : AjaxResult.error("记录不存在");
    }

    /**
     * 新增用户画像
     */
    @PreAuthorize("hasRole('admin')")
    @PostMapping
    @Operation(summary = "新增用户画像")
    public AjaxResult add(@Valid @RequestBody UserProfile profile)
    {
        int result = userProfileService.insertUserProfile(profile);
        return result > 0 ? AjaxResult.success("新增成功") : AjaxResult.error("新增失败");
    }

    /**
     * 修改用户画像
     */
    @PreAuthorize("hasRole('admin')")
    @PutMapping
    @Operation(summary = "修改用户画像")
    public AjaxResult edit(@Valid @RequestBody UserProfile profile)
    {
        int result = userProfileService.updateUserProfile(profile);
        return result > 0 ? AjaxResult.success("修改成功") : AjaxResult.error("修改失败");
    }

    /**
     * 删除用户画像
     */
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/{id}")
    @Operation(summary = "删除用户画像")
    public AjaxResult remove(@PathVariable Long id)
    {
        int result = userProfileService.deleteUserProfileById(id);
        return result > 0 ? AjaxResult.success("删除成功") : AjaxResult.error("删除失败");
    }
}
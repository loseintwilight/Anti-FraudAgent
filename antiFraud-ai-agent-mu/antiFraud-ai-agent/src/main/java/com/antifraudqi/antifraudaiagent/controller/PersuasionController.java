package com.antifraudqi.antifraudaiagent.controller;

import com.antifraudqi.antifraudaiagent.service.PersuasionService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * AI 劝导话术接口
 * 根据升级方案 V2.3（Section 3.3.2）
 * 当风险评估为 HIGH 或 EXTREME 时自动生成口语化劝阻话术
 */
@Slf4j
@RestController
@RequestMapping("/persuasion")
public class PersuasionController {

    @Resource
    private PersuasionService persuasionService;

    /**
     * 生成劝导话术
     *
     * @param request 请求参数
     *               fraudType: 诈骗类型
     *               riskLevel: 风险等级 (HIGH/EXTREME)
     *               userRole: 用户角色 (elderly/youth/child/accountant/worker)
     * @return 包含劝导话术的响应
     */
    @PostMapping("/generate")
    public Map<String, Object> generatePersuasion(@RequestBody Map<String, String> request) {
        Map<String, Object> result = new HashMap<>();
        try {
            String fraudType = request.getOrDefault("fraudType", "");
            String riskLevel = request.getOrDefault("riskLevel", "HIGH");
            String userRole = request.getOrDefault("userRole", "default");

            String message = persuasionService.generatePersuasion(fraudType, riskLevel, userRole);

            result.put("success", true);
            result.put("message", message);
            result.put("fraudType", fraudType);
            result.put("riskLevel", riskLevel);
            result.put("userRole", userRole);

            if (message != null) {
                log.info("劝导话术生成成功: fraudType={}, riskLevel={}, userRole={}", fraudType, riskLevel, userRole);
            } else {
                log.info("无需劝导: riskLevel={}", riskLevel);
            }
        } catch (Exception e) {
            log.error("生成劝导话术失败", e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }

    /**
     * 获取所有支持劝导的诈骗类型列表
     *
     * @return 诈骗类型列表
     */
    @GetMapping("/types")
    public Map<String, Object> getPersuasionTypes() {
        Map<String, Object> result = new HashMap<>();
        try {
            result.put("success", true);
            result.put("data", persuasionService.getAllPersuasionMessages().keySet());
        } catch (Exception e) {
            log.error("获取劝导类型失败", e);
            result.put("success", false);
            result.put("error", e.getMessage());
        }
        return result;
    }
}
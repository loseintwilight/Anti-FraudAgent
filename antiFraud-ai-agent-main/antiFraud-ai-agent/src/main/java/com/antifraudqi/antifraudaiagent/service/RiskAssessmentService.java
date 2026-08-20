package com.antifraudqi.antifraudaiagent.service;

import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * 风险评估服务
 * 调用 Python 微服务 REST API 进行诈骗风险评估
 */
@Slf4j
@Service
public class RiskAssessmentService {

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    @Resource
    private RestTemplate restTemplate;

    /**
     * 对用户的输入文本进行风险评估
     *
     * @param userId   用户ID
     * @param inputText 输入文本
     * @return 风险评估结果，包含风险评分、风险等级、诈骗类型等信息
     */
    public Map<String, Object> assessRisk(String userId, String inputText) {
        String url = pythonServiceUrl + "/api/v1/risk/score";
        Map<String, Object> request = new HashMap<>();
        request.put("user_id", userId);
        request.put("text", inputText);

        try {
            log.info("调用 Python 微服务进行风险评估: userId={}", userId);
            Map<String, Object> response = restTemplate.postForObject(url, request, Map.class);
            log.info("风险评估成功: userId={}, result={}", userId, response);
            return response;
        } catch (Exception e) {
            log.error("调用 Python 微服务风险评估失败: userId={}", userId, e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("error", "风险评估服务暂时不可用: " + e.getMessage());
            errorResult.put("riskScore", 0);
            errorResult.put("riskLevel", "UNKNOWN");
            return errorResult;
        }
    }
}

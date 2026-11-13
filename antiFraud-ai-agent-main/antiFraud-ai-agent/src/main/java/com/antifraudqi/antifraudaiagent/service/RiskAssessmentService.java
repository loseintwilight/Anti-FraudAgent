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

    /**
     * 按 Python app/api/schemas.py 中 UserBehavior 的字段定义构造行为对象。
     * Java 侧暂无采集到的真实行为数据，各字段取 schema 默认值；
     * age 是唯一必填且无默认值的字段，取 0（与 Python UserProfile.age 缺省一致，表示未知）。
     */
    private Map<String, Object> buildBehavior() {
        Map<String, Object> behavior = new HashMap<>();
        behavior.put("age", 0);
        behavior.put("gender", "unknown");
        behavior.put("occupation", "unknown");
        behavior.put("education", "unknown");
        behavior.put("province", "unknown");
        behavior.put("city", "unknown");
        behavior.put("call_duration_minutes", 0.0);
        behavior.put("call_count_outgoing", 0);
        behavior.put("call_count_incoming", 0);
        behavior.put("unknown_call_ratio", 0.0);
        behavior.put("sms_count_received", 0);
        behavior.put("sms_count_sent", 0);
        behavior.put("sms_with_link_ratio", 0.0);
        behavior.put("recent_transaction_amount", 0.0);
        behavior.put("total_transaction_amount_7d", 0.0);
        behavior.put("transaction_count_7d", 0);
        behavior.put("transaction_to_new_accounts", 0);
        behavior.put("night_transaction_count", 0);
        behavior.put("app_usage_minutes", 0.0);
        behavior.put("installed_apps_count", 0);
        behavior.put("recently_installed_apps", 0);
        behavior.put("financial_app_count", 0);
        behavior.put("visited_suspicious_sites", 0);
        behavior.put("clicked_unknown_links", 0);
        behavior.put("vpn_or_proxy_used", false);
        behavior.put("public_wifi_connected", false);
        behavior.put("account_age_days", 0);
        behavior.put("has_verified_realname", false);
        behavior.put("device_rooted", false);
        behavior.put("reported_count", 0);
        behavior.put("fraud_hotline_called", false);
        return behavior;
    }
}

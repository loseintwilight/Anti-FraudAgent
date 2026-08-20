package com.antifraudqi.antifraudaiagent.controller;

import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.*;

/**
 * AI 控制器
 * 代理所有 AI 请求到 Python LangChain 微服务
 * 所有 AI 功能由 Python 微服务中的 LangChain 实现
 */
@RestController
@RequestMapping("/ai")
@Slf4j
public class AiController {

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    @Resource
    private RestTemplate restTemplate;

    // ===================== AI 对话 =====================

    @PostMapping("/love_app/chat/sync")
    public Map<String, Object> doChatWithLoveAppSync(@RequestBody Map<String, String> request) {
        String message = request.getOrDefault("message", "");
        String conversationId = request.getOrDefault("conversation_id", "default");

        String url = pythonServiceUrl + "/api/v1/ai/chat";
        Map<String, Object> body = new HashMap<>();
        body.put("message", message);
        body.put("conversation_id", conversationId);

        try {
            log.info("调用 Python 微服务 AI 对话: conversationId={}", conversationId);
            Map<String, Object> response = restTemplate.postForObject(url, body, Map.class);
            return response != null ? response : Map.of("success", false, "response", "服务无响应");
        } catch (Exception e) {
            log.error("调用 Python 微服务 AI 对话失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("response", "AI 对话服务暂时不可用: " + e.getMessage());
            return errorResult;
        }
    }

    // ===================== 带工具对话 =====================

    @PostMapping("/love_app/chat/tools")
    public Map<String, Object> doChatWithTools(@RequestBody Map<String, String> request) {
        String message = request.getOrDefault("message", "");
        String conversationId = request.getOrDefault("conversation_id", "default");

        String url = pythonServiceUrl + "/api/v1/ai/chat/tools";
        Map<String, Object> body = new HashMap<>();
        body.put("message", message);
        body.put("conversation_id", conversationId);

        try {
            log.info("调用 Python 微服务 AI 工具对话: conversationId={}", conversationId);
            Map<String, Object> response = restTemplate.postForObject(url, body, Map.class);
            return response != null ? response : Map.of("success", false, "response", "服务无响应");
        } catch (Exception e) {
            log.error("调用 Python 微服务 AI 工具对话失败", e);
            return Map.of("success", false, "response", "AI 工具对话服务暂时不可用");
        }
    }

    // ===================== 对话报告生成 =====================

    @PostMapping("/love_app/chat/report")
    public Map<String, Object> doChatWithReport(@RequestBody Map<String, String> request) {
        String message = request.getOrDefault("message", "");
        String conversationId = request.getOrDefault("conversation_id", "default");
        String userName = request.getOrDefault("user_name", "用户");

        String url = pythonServiceUrl + "/api/v1/ai/chat/report";
        Map<String, Object> body = new HashMap<>();
        body.put("message", message);
        body.put("conversation_id", conversationId);
        body.put("user_name", userName);

        try {
            log.info("调用 Python 微服务 AI 对话报告生成: conversationId={}", conversationId);
            Map<String, Object> response = restTemplate.postForObject(url, body, Map.class);
            return response != null ? response : Map.of("success", false, "response", "服务无响应");
        } catch (Exception e) {
            log.error("调用 Python 微服务 AI 对话报告生成失败", e);
            return Map.of("success", false, "response", "报告生成服务暂时不可用");
        }
    }

    // ===================== 视觉大模型图片分析 =====================

    @PostMapping("/vision/analyze")
    public Map<String, Object> analyzeImage(@RequestBody Map<String, String> request) {
        String imageBase64 = request.getOrDefault("imageBase64", "");
        String prompt = request.getOrDefault("prompt", null);

        String url = pythonServiceUrl + "/api/v1/ai/vision/analyze";
        Map<String, Object> body = new HashMap<>();
        body.put("image_base64", imageBase64);
        if (prompt != null && !prompt.isEmpty()) {
            body.put("prompt", prompt);
        }

        try {
            log.info("调用 Python 微服务视觉大模型分析图片...");
            Map<String, Object> response = restTemplate.postForObject(url, body, Map.class);
            return response != null ? response : Map.of("success", false, "text", "图片分析服务无响应");
        } catch (Exception e) {
            log.error("调用 Python 微服务视觉大模型分析失败", e);
            return Map.of(
                    "success", false,
                    "text", "图片内容分析中遇到问题，请尝试手动描述图片内容。",
                    "error", e.getMessage()
            );
        }
    }

    // ===================== RAG 对话 =====================

    @PostMapping("/rag/chat")
    public Map<String, Object> doRagChat(@RequestBody Map<String, String> request) {
        String message = request.getOrDefault("message", "");
        String conversationId = request.getOrDefault("conversation_id", "default");

        String url = pythonServiceUrl + "/api/v1/ai/rag/chat";
        Map<String, Object> body = new HashMap<>();
        body.put("message", message);
        body.put("conversation_id", conversationId);

        try {
            log.info("调用 Python 微服务 RAG 对话: conversationId={}", conversationId);
            Map<String, Object> response = restTemplate.postForObject(url, body, Map.class);
            return response != null ? response : Map.of("success", false, "response", "服务无响应");
        } catch (Exception e) {
            log.error("调用 Python 微服务 RAG 对话失败", e);
            return Map.of("success", false, "response", "RAG 对话服务暂时不可用");
        }
    }

    // ===================== 清除对话历史 =====================

    @PostMapping("/love_app/clear")
    public Map<String, Object> clearMemory(@RequestParam(defaultValue = "default") String conversationId) {
        String url = pythonServiceUrl + "/api/v1/ai/clear?conversation_id=" + conversationId;

        try {
            log.info("清除对话历史: conversationId={}", conversationId);
            Map<String, Object> response = restTemplate.postForObject(url, null, Map.class);
            return response != null ? response : Map.of("success", true, "message", "对话历史已清除");
        } catch (Exception e) {
            log.error("清除对话历史失败", e);
            return Map.of("success", false, "message", "清除对话历史失败");
        }
    }

    // ===================== LLM 统计 =====================

    @GetMapping("/stats")
    public Map<String, Object> getLLMStats() {
        String url = pythonServiceUrl + "/api/v1/ai/stats";

        try {
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);
            return response != null ? response : Map.of("success", false, "message", "服务无响应");
        } catch (Exception e) {
            log.error("获取 LLM 统计失败", e);
            return Map.of("success", false, "message", "获取 LLM 统计失败");
        }
    }
}
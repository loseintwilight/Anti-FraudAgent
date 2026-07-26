package com.antifraudqi.antifraudaiagent.service;

import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

/**
 * 视频分析服务
 * 调用 Python LangChain 微服务进行视觉大模型分析
 */
@Service
@Slf4j
public class QwenVLVideoAnalysisService {

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    @Resource
    private RestTemplate restTemplate;

    private static final String VIDEO_ANALYSIS_PROMPT = """
        【重要】你是一个专业的反诈骗视频内容分析助手。请严格按照以下步骤分析视频画面：
        
        第一步：逐字读取并输出视频中可见的 ALL 文字内容
        - 包括大标题、小标题、正文、按钮文字、水印文字等
        - 如果文字模糊或较小，请尽力辨认
        - 按原文格式输出，不要省略、不要概括、不要猜测
        
        第二步：描述视频场景
        - 视频中有哪些人物、物品、环境
        - 人物的动作、表情、穿着
        - 场景的背景、氛围
        
        第三步：基于实际提取的文字和场景判断诈骗类型
        - 根据第一步提取的真实文字内容判断
        - 结合第二步的场景描述综合分析
        - 不要根据画面外观猜测
        
        输出格式要求：
        === 视频文字（原样输出）===
        （这里填写第一步提取的所有文字）
        
        === 场景描述 ===
        （这里填写第二步的场景描述）
        
        === 诈骗类型判断 ===
        （这里填写基于文字和场景的综合判断）
        """;

    public String analyzeImage(String imageBase64) {
        try {
            // 调用 Python 微服务视觉分析接口
            String url = pythonServiceUrl + "/api/v1/ai/vision/analyze";
            Map<String, Object> body = new HashMap<>();
            body.put("image_base64", imageBase64);
            body.put("prompt", VIDEO_ANALYSIS_PROMPT);

            log.info("调用 Python 微服务视觉大模型进行图片分析...");
            Map<String, Object> response = restTemplate.postForObject(url, body, Map.class);

            if (response != null && response.containsKey("text")) {
                String result = (String) response.get("text");
                log.info("视觉大模型图片分析成功");
                return result;
            }

            log.warn("视觉大模型返回空结果，使用备用方案");
            return getFallbackResult();

        } catch (Exception e) {
            log.error("调用 Python 微服务视觉分析失败", e);
            return getFallbackResult();
        }
    }

    public String analyzeVideoFrames(List<String> frameBase64List) {
        if (frameBase64List == null || frameBase64List.isEmpty()) {
            log.warn("视频帧列表为空");
            return getFallbackResult();
        }

        StringBuilder analysisResults = new StringBuilder();
        int successCount = 0;

        for (int i = 0; i < frameBase64List.size(); i++) {
            String base64 = frameBase64List.get(i);
            try {
                log.info("正在分析第{}/{}帧...", i + 1, frameBase64List.size());
                String result = analyzeImage(base64);
                analysisResults.append(String.format("【第%d帧分析结果】\n%s\n\n", i + 1, result));
                successCount++;
            } catch (Exception e) {
                log.error("第{}帧分析失败", i + 1, e);
                analysisResults.append(String.format("【第%d帧】分析失败: %s\n\n", i + 1, e.getMessage()));
            }
        }

        log.info("视频帧分析完成，成功{}/{}帧", successCount, frameBase64List.size());

        if (successCount == 0) {
            return getFallbackResult();
        }

        return analysisResults.toString();
    }

    private String getFallbackResult() {
        return "视频/图片内容分析中遇到问题，请尝试手动描述视频或图片内容。";
    }
}
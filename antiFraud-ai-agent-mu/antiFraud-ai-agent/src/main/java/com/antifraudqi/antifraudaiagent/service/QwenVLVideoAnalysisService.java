package com.antifraudqi.antifraudaiagent.service;

import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversation;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationParam;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationResult;
import com.alibaba.dashscope.common.MultiModalMessage;
import com.alibaba.dashscope.common.Role;
import com.alibaba.dashscope.exception.ApiException;
import com.alibaba.dashscope.exception.NoApiKeyException;
import com.alibaba.dashscope.exception.UploadFileException;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@Slf4j
public class QwenVLVideoAnalysisService {

    @Value("${spring.ai.dashscope.api-key}")
    private String dashScopeApiKey;

    @Value("${spring.ai.dashscope.vision.model:qwen-vl-max}")
    private String visionModel;

    private static final MultiModalConversation MULTI_MODAL_CONVERSATION = new MultiModalConversation();

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
            String imageDataUrl = "data:image/jpeg;base64," + imageBase64;

            MultiModalMessage userMessage = MultiModalMessage.builder()
                    .role(Role.USER.getValue())
                    .content(Arrays.asList(
                            Collections.singletonMap("image", imageDataUrl),
                            Collections.singletonMap("text", VIDEO_ANALYSIS_PROMPT)
                    )).build();

            MultiModalConversationParam param = MultiModalConversationParam.builder()
                    .apiKey(dashScopeApiKey)
                    .model(visionModel)
                    .message(userMessage)
                    .build();

            log.info("调用视觉大模型 {} 进行图片分析...", visionModel);
            MultiModalConversationResult result = MULTI_MODAL_CONVERSATION.call(param);

            String explanation = Optional.ofNullable(result.getOutput())
                    .map(output -> output.getChoices().get(0))
                    .map(choice -> choice.getMessage())
                    .map(message -> message.getContent().get(0))
                    .map(content -> (String) content.get("text"))
                    .orElse(null);

            if (explanation != null && !explanation.isEmpty()) {
                log.info("视觉大模型图片分析成功: {}", explanation);
                return explanation;
            }

            log.warn("视觉大模型返回空结果，使用备用方案");
            return getFallbackResult();

        } catch (NoApiKeyException e) {
            log.error("DashScope API Key 未配置", e);
            return getFallbackResult();
        } catch (UploadFileException e) {
            log.error("图片上传失败", e);
            return getFallbackResult();
        } catch (ApiException e) {
            log.error("DashScope API 调用失败", e);
            return getFallbackResult();
        } catch (Exception e) {
            log.error("视觉大模型分析异常", e);
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

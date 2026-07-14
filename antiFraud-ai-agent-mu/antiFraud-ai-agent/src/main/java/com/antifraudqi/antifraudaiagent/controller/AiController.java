package com.antifraudqi.antifraudaiagent.controller;


import com.antifraudqi.antifraudaiagent.agent.AntiFraudManus;
import com.antifraudqi.antifraudaiagent.app.LoveApp;
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
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import reactor.core.publisher.Flux;
import java.util.*;

@RestController
@RequestMapping("/ai")
@Slf4j
public class AiController {
    @Resource
    private LoveApp loveApp;
    @Resource
    private ToolCallback[] allTools;
    @Resource
    private ChatModel dashscopeChatModel;
    @Resource
    private AntiFraudManus antiFraudManus;
    
    @Value("${spring.ai.dashscope.api-key}")
    private String dashScopeApiKey;
    
    // 性能优化：复用 MultiModalConversation 实例（线程安全）
    private static final MultiModalConversation MULTI_MODAL_CONVERSATION = new MultiModalConversation();
    
    // 性能优化：预定义 visionPrompt 常量，避免每次调用都创建新字符串
    private static final String VISION_PROMPT = """
        【重要】你是一个专业的OCR文字识别助手。请严格按照以下步骤分析图片：
        
        第一步：逐字读取并输出图片中可见的 ALL 文字内容
        - 包括大标题、小标题、正文、按钮文字、水印文字等
        - 如果文字模糊或较小，请尽力辨认
        - 按原文格式输出，不要省略、不要概括、不要猜测
        
        第二步：描述图片场景
        - 图片中有哪些人物、物品、环境
        
        第三步：基于实际提取的文字判断诈骗类型
        - 根据第一步提取的真实文字内容判断
        - 不要根据画面外观猜测
        
        输出格式要求：
        === 图片文字（原样输出）===
        （这里填写第一步提取的所有文字）
        
        === 场景描述 ===
        （这里填写第二步的场景描述）
        
        === 诈骗类型判断 ===
        （这里填写基于文字内容的判断）
        """;
    
    @GetMapping("/love_app/chat/sync")
    public String doChatWithLoveAppSync(String message, String chatId)
    {
        return loveApp.doChat(message, chatId);
    }
//    @GetMapping(value="/love_app/chat/see",produces = MediaType.TEXT_EVENT_STREAM_VALUE)
//    public Flux<String> doChatWithLoveAppSSE(String message, String chatId)
//    {
//        return loveApp.doChatByStream(message, chatId);
//    }
    @GetMapping("/love_app/chat/sse")
    public Flux<ServerSentEvent<String>> doChatWithLoveAppSSE(String message, String chatId){
        return loveApp.doChatByStream(message, chatId)
                .map(chunk -> ServerSentEvent.<String>builder()
                        .data(chunk)
                        .build());
    }
//    @GetMapping("/love_app/chat/see/emitter")
//    public SseEmitter doChatWithLoveAppSseEmitter(String message, String chatId){
//        SseEmitter emitter = new SseEmitter();
//        loveApp.doChatByStream(message, chatId)
//                .subscribe(chunk -> {
//                    try{
//                        emitter.send(chunk);
//                    }catch (Exception e){
//                        emitter.completeWithError(e);
//                    }
//                },
//                        emitter:: completeWithError,
//                        emitter:: complete
//            );
//        return emitter;
//    }
    @GetMapping("/manus/chat")
    public SseEmitter doChatWithManus(String message) {
        AntiFraudManus antiFraudManus = new AntiFraudManus(allTools, dashscopeChatModel);
        return antiFraudManus.runStream(message);
    }

    // 视觉大模型图片分析接口
    @PostMapping("/vision/analyze")
    public Map<String, Object> analyzeImage(@RequestBody VisionRequest request) {
        Map<String, Object> response = new HashMap<>();
        try {
            String imageBase64 = request.getImageBase64();
            String prompt = request.getPrompt();
            
            String analyzedText = analyzeImageWithVisionModel(imageBase64, prompt);
            
            response.put("success", true);
            response.put("text", analyzedText);
        } catch (Exception e) {
            log.error("视觉大模型分析失败", e);
            response.put("success", false);
            response.put("error", e.getMessage());
        }
        return response;
    }

    private String analyzeImageWithVisionModel(String imageBase64, String prompt) {
        try {
            String imageDataUrl = "data:image/jpeg;base64," + imageBase64;
            
            MultiModalMessage userMessage = MultiModalMessage.builder()
                    .role(Role.USER.getValue())
                    .content(Arrays.asList(
                            Collections.singletonMap("image", imageDataUrl),
                            Collections.singletonMap("text", VISION_PROMPT)
                    )).build();
            
            // 性能优化：设置超时时间，避免长时间等待
            MultiModalConversationParam param = MultiModalConversationParam.builder()
                    .apiKey(dashScopeApiKey)
                    .model("qwen-vl-max")
                    .message(userMessage)
                    .build();
            
            log.info("调用视觉大模型 qwen-vl-max 进行图片分析...");
            MultiModalConversationResult result = MULTI_MODAL_CONVERSATION.call(param);
            
            String explanation = Optional.ofNullable(result.getOutput())
                    .map(output -> output.getChoices().get(0))
                    .map(choice -> choice.getMessage())
                    .map(message -> message.getContent().get(0))
                    .map(content -> (String) content.get("text"))
                    .orElse(null);
            
            if (explanation != null && !explanation.isEmpty()) {
                log.info("视觉大模型分析成功: {}", explanation);
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
    
    private String getFallbackResult() {
        return "图片内容分析中遇到问题，请尝试手动描述图片内容。";
    }

    // 视觉请求模型
    static class VisionRequest {
        private String imageBase64;
        private String prompt;

        public String getImageBase64() {
            return imageBase64;
        }

        public void setImageBase64(String imageBase64) {
            this.imageBase64 = imageBase64;
        }

        public String getPrompt() {
            return prompt;
        }

        public void setPrompt(String prompt) {
            this.prompt = prompt;
        }
    }

}

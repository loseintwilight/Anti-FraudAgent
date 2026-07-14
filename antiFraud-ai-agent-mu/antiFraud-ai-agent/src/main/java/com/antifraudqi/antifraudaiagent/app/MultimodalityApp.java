package com.antifraudqi.antifraudaiagent.app;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import cn.hutool.core.io.resource.ClassPathResource;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversation;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationParam;
import com.alibaba.dashscope.aigc.multimodalconversation.MultiModalConversationResult;
import com.alibaba.dashscope.common.MultiModalMessage;
import com.alibaba.dashscope.common.Role;
import com.alibaba.dashscope.exception.ApiException;
import com.alibaba.dashscope.exception.NoApiKeyException;
import com.alibaba.dashscope.exception.UploadFileException;
import com.alibaba.dashscope.utils.JsonUtils;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.input.Prompt;
import org.springframework.util.MimeTypeUtils;

import javax.print.attribute.standard.Media;

public class MultimodalityApp {
    public static void explainImage(String ImageUrl) throws NoApiKeyException, UploadFileException {
        MultiModalConversation conv = new MultiModalConversation();
        MultiModalMessage userMessage = MultiModalMessage.builder()
                .role(Role.USER.getValue())
                .content(Arrays.asList(
                        Collections.singletonMap("image", ImageUrl),
                        Collections.singletonMap("text", "请用中文解释这个图片。")
                )).build();
        MultiModalConversationParam param = MultiModalConversationParam.builder()
                // 若没有配置环境变量，请用百炼 API Key 将下行替换为：.apiKey("sk-xxx")
                .apiKey(System.getenv("DASHSCOPE_API_KEY") != null ? System.getenv("DASHSCOPE_API_KEY") : "***REMOVED***")
                // 此处以 qwen-vl-plus 为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                .model("qwen-vl-max")
                .message(userMessage)
                .build();
        MultiModalConversationResult result = conv.call(param);

        String explanation = Optional.ofNullable(result.getOutput())
                .map(output -> output.getChoices().get(0))
                .map(choice -> choice.getMessage())
                .map(message -> message.getContent().get(0))
                .map(content -> (String) content.get("text"))
                .orElse("未获取到 AI 响应");

        System.out.println("\n=== 图片解释 ===");
        System.out.println(explanation);
        System.out.println("================\n");
        System.out.println("\n=== 图片解释 ===");
        System.out.println(explanation);
        System.out.println("================\n");
    }


    public static void main(String[] args) {
        System.out.println("🚀 图片解释助手启动...\n");

        System.out.println("解释单张图片");
        try {
            explainImage("https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg");
        } catch (NoApiKeyException | UploadFileException e) {
            System.err.println("图片解释失败：" + e.getMessage());
        }

    }
}
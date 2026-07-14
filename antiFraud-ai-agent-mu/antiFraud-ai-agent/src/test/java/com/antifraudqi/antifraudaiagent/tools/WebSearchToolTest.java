package com.antifraudqi.antifraudaiagent.tools;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;
@SpringBootTest
class WebSearchToolTest {
    @Value("${search-api.api-key}")
    private String apiKey;
    @Test
    void searchWeb() {
        WebSearchTool webSearchTool = new WebSearchTool(apiKey);
        String query = "反诈骗智能体 常见电信网络诈骗类型";
        String result = webSearchTool.searchWeb(query);
        Assertions.assertNotNull(result);
    }
}
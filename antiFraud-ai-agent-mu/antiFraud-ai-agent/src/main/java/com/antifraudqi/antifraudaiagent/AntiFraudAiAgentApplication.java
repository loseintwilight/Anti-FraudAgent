package com.antifraudqi.antifraudaiagent;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;

@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
@EnableAutoConfiguration(excludeName = {
        "org.springframework.ai.autoconfigure.mcp.client.McpAutoConfiguration",
        "org.springframework.ai.autoconfigure.mcp.client.common.McpClientCommonAutoConfiguration",
        "org.springframework.ai.autoconfigure.mcp.client.httpclient.McpClientHttpClientAutoConfiguration",
        "org.springframework.ai.autoconfigure.mcp.client.sse.McpClientSseAutoConfiguration",
        "org.springframework.ai.autoconfigure.mcp.client.tool.McpToolCallbackAutoConfiguration",
        "org.springframework.ai.autoconfigure.mcp.client.McpToolCallbackAutoConfiguration"
})
public class AntiFraudAiAgentApplication {

    public static void main(String[] args) {
        SpringApplication.run(AntiFraudAiAgentApplication.class, args);
    }

}

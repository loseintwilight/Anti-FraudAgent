package com.antifraudqi.antifraudaiagent.tools;

import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ToolRegistration {

    @Value("${search-api.api-key}")
    private String searchApiKey;

    @Bean
    public FileOperationTool fileOperationTool() {
        return new FileOperationTool();
    }

    @Bean
    public WebSearchTool webSearchTool() {
        return new WebSearchTool(searchApiKey);
    }

    @Bean
    public WebScrapingTool webScrapingTool() {
        return new WebScrapingTool();
    }

    @Bean
    public TerminateTool terminateTool() {
        return new TerminateTool();
    }

    @Bean
    public ResourceDownloadTool resourceDownloadTool() {
        return new ResourceDownloadTool();
    }

    @Bean
    public TerminalOperationTool terminalOperationTool() {
        return new TerminalOperationTool();
    }

    @Bean
    public PDFGenerationTool pdfGenerationTool() {
        return new PDFGenerationTool();
    }

    @Bean
    public ToolCallback[] allTools(FileOperationTool fileOperationTool,
                                   WebSearchTool webSearchTool,
                                   WebScrapingTool webScrapingTool,
                                   TerminateTool terminateTool,
                                   ResourceDownloadTool resourceDownloadTool,
                                   TerminalOperationTool terminalOperationTool,
                                   PDFGenerationTool pdfGenerationTool) {
        ToolCallbackProvider toolCallbackProvider = MethodToolCallbackProvider.builder()
                .toolObjects(fileOperationTool, webSearchTool, webScrapingTool, terminateTool,
                        resourceDownloadTool, terminalOperationTool, pdfGenerationTool)
                .build();
        return toolCallbackProvider.getToolCallbacks();
    }
}

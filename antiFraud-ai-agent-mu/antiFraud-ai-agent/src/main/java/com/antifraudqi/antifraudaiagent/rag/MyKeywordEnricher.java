package com.antifraudqi.antifraudaiagent.rag;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.document.Document;
import org.springframework.ai.model.transformer.KeywordMetadataEnricher;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class MyKeywordEnricher {
    private static final Logger log = LoggerFactory.getLogger(MyKeywordEnricher.class);
    private final ChatModel dashscopeChatModel;

    public MyKeywordEnricher(ChatModel dashscopeChatModel) {
        this.dashscopeChatModel = dashscopeChatModel;
    }

    public List<Document> enrichDocuments(List<Document> documents) {
        if (documents == null || documents.isEmpty()) {
            return documents;
        }
        
        List<Document> enrichedDocuments = new ArrayList<>();
        KeywordMetadataEnricher enricher = new KeywordMetadataEnricher(dashscopeChatModel, 5);
        
        int batchSize = 3;
        for (int i = 0; i < documents.size(); i += batchSize) {
            int end = Math.min(i + batchSize, documents.size());
            List<Document> batch = documents.subList(i, end);
            
            try {
                List<Document> enrichedBatch = enricher.apply(batch);
                enrichedDocuments.addAll(enrichedBatch);
                log.info("关键词提取进度: {}/{}", end, documents.size());
                
                if (end < documents.size()) {
                    Thread.sleep(500);
                }
            } catch (Exception e) {
                log.warn("关键词提取失败（批次 {}/{}），跳过该批次: {}", 
                        (i / batchSize + 1), 
                        (documents.size() + batchSize - 1) / batchSize, 
                        e.getMessage());
                enrichedDocuments.addAll(batch);
            }
        }
        
        return enrichedDocuments;
    }
}

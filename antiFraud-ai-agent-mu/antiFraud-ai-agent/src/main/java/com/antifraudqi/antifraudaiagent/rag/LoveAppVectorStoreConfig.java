package com.antifraudqi.antifraudaiagent.rag;

import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.document.Document;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Collections;
import java.util.List;
import com.antifraudqi.antifraudaiagent.rag.MyKeywordEnricher;

@Configuration
public class LoveAppVectorStoreConfig {
    private static final Logger log = LoggerFactory.getLogger(LoveAppVectorStoreConfig.class);
    
    @Resource
    private LoveAppDocumentLoader loveAppDocumentLoader;
    @Resource
    private MyTokenTextSplitter myTokenTextSplitter;
    @Resource
    private MyKeywordEnricher myKeywordEnricher;
    
    @Bean
    VectorStore loveAppVectorStore(EmbeddingModel dashscopeEmbeddingModel, MyKeywordEnricher myKeywordEnricher) {
        SimpleVectorStore simpleVectorStore = SimpleVectorStore.builder(dashscopeEmbeddingModel)
                .build();
        try {
            List<Document> documents = loveAppDocumentLoader.loadMarkdowns();
            documents = myTokenTextSplitter.splitCustomized(documents);
            try {
                documents = myKeywordEnricher.enrichDocuments(documents);
            } catch (Exception e) {
                log.warn("关键词提取失败，跳过关键词提取: {}", e.getMessage());
            }
            simpleVectorStore.add(documents);
            log.info("知识库文档加载完成，共 {} 个文档片段", documents.size());
        } catch (Exception e) {
            log.warn("知识库加载失败（可能是网络问题）: {}，将使用空知识库", e.getMessage());
        }
        return simpleVectorStore;
    }
}

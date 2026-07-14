package com.antifraudqi.antifraudaiagent.app;

import jakarta.annotation.Resource;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;
@SpringBootTest
class MultimodalityAppTest {
    @Resource
    private MultimodalityApp multimodalityApp;

     void setMultimodalityApp(MultimodalityApp multimodalityApp) {
        this.multimodalityApp = multimodalityApp;
    }
}
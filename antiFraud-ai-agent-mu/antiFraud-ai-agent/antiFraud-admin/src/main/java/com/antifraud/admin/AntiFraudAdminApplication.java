package com.antifraud.admin;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.antifraud.admin.mapper")
public class AntiFraudAdminApplication {

    public static void main(String[] args) {
        SpringApplication.run(AntiFraudAdminApplication.class, args);
    }
}
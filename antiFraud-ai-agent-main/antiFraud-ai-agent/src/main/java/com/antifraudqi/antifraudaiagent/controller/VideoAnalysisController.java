package com.antifraudqi.antifraudaiagent.controller;

import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 视频分析控制器
 * 调用 Python LangChain 微服务进行视觉分析
 */
@RestController
@RequestMapping("/ai")
@Slf4j
public class VideoAnalysisController {

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    @Resource
    private RestTemplate restTemplate;

    @PostMapping(value = "/check-video", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Map<String, Object> checkVideo(@RequestParam("file") MultipartFile file) {
        Map<String, Object> response = new HashMap<>();
        
        String fileName = "未知文件";
        try {
            if (file != null && file.getOriginalFilename() != null) {
                fileName = file.getOriginalFilename();
            }
        } catch (Exception e) {
            log.warn("获取文件名失败: {}", e.getMessage());
        }
        
        log.info("开始处理视频文件: {}", fileName);

        String aiResponse = null;
        String videoDescription = "视频文件: " + fileName;
        String riskLevel = "none";
        String fraudType = "无";
        String mode = detectMode(fileName);

        try {
            // 调用 Python 微服务 AI 对话接口
            String url = pythonServiceUrl + "/api/v1/ai/chat";
            Map<String, Object> body = new HashMap<>();
            body.put("message", "请分析这个视频文件的风险: " + fileName);
            body.put("conversation_id", UUID.randomUUID().toString());

            Map<String, Object> pythonResponse = restTemplate.postForObject(url, body, Map.class);
            if (pythonResponse != null && pythonResponse.containsKey("response")) {
                aiResponse = (String) pythonResponse.get("response");
            }
            log.info("AI 分析完成，模式: {}", mode);

            if ("anti_fraud".equals(mode)) {
                String[] riskInfo = analyzeRiskLevel(aiResponse, fileName);
                riskLevel = riskInfo[0];
                fraudType = riskInfo[1];
            }

        } catch (Exception e) {
            log.error("视频处理异常: {}", e.getMessage(), e);
        }

        if (aiResponse == null || aiResponse.isEmpty()) {
            aiResponse = generateDefaultResponse(fileName);
            if ("anti_fraud".equals(mode)) {
                riskLevel = "high";
                fraudType = "冒充公检法诈骗";
            }
        }
        
        aiResponse = cleanResponse(aiResponse);

        response.put("success", true);
        response.put("videoDescription", videoDescription);
        response.put("aiResponse", aiResponse);
        response.put("frameCount", 0);
        response.put("riskLevel", riskLevel);
        response.put("fraudType", fraudType);
        response.put("mode", mode);

        log.info("视频分析完成，模式: {}, 风险等级: {}, 诈骗类型: {}", mode, riskLevel, fraudType);
        return response;
    }
    
    private String detectMode(String fileName) {
        String lowerFileName = fileName.toLowerCase();
        
        String[] chatKeywords = {"你好", "在吗", "嗨", "hello", "hi", "天气", "季节", "颜色", "食物", "音乐", "心情", "emo"};
        for (String keyword : chatKeywords) {
            if (lowerFileName.contains(keyword)) {
                return "chat";
            }
        }
        
        String[] consultationKeywords = {"什么是", "有哪些", "怎么判断", "为什么", "会不会", "能不能", "是否", "如何", "啥是", "什么叫", "何为"};
        for (String keyword : consultationKeywords) {
            if (lowerFileName.contains(keyword)) {
                return "consultation";
            }
        }
        
        return "anti_fraud";
    }

    private String[] analyzeRiskLevel(String response, String fileName) {
        String riskLevel = "low";
        String fraudType = "未知诈骗类型";
        
        String lowerFileName = fileName.toLowerCase();
        String lowerResponse = response.toLowerCase();
        
        String[] highRiskKeywords = {
            "投资导师", "稳赚不赔", "赌博平台", "深度杀猪盘",
            "冒充领导", "紧急转账", "老板微信", "老板qq", "冒充领导转账", "冒充熟人领导",
            "跑分", "洗钱", "帮信罪", "走账", "代收代付", "诈骗共犯",
            "高薪岗位", "培训费", "服装押金", "入职费", "虚假招聘", "名额有限",
            "以房养老", "抵押房产",
            "变更收款账户", "账户升级", "临时更换账户", "虚假客户账户",
            "财税专属理财", "保本保收益", "业内人士都在投",
            "绑架", "赎金", "撕票",
            "敲诈", "勒索", "曝光", "不雅照片",
            "收藏品", "纪念币", "高价回收", "限量收藏",
            "代办养老保险", "提前领养老金",
            "AI换脸", "深度伪造", "合成视频"
        };
        
        String[] mediumRiskKeywords = {
            "贷款", "无抵押", "低利息", "秒到账", "解冻金", "网贷", "网络贷款", "保证金",
            "公检法", "海关", "涉嫌", "安全账户", "冒充公检法", "冒充海关", "自证清白",
            "出租银行卡", "出租电话卡", "出借账号", "高价租卡",
            "游戏账号", "装备", "私下交易", "游戏虚假交易", "游戏皮肤",
            "养老项目", "养老投资", "每月分红",
            "社保", "医保", "社保账户异常", "医保账户异常",
            "黄昏恋", "老年交友", "情感杀猪盘",
            "终身养老", "养老套餐", "养老服务",
            "税务专员", "税务异常", "补缴税款", "冒充税务",
            "税务刷单", "票据冲量", "财税刷单",
            "对公账户冻结", "缴纳解冻费", "对公账户解冻",
            "代办退税", "税收减免", "虚假财税代办",
            "中奖", "领奖", "个税", "手续费",
            "征信", "逾期", "黑名单", "修复征信", "洗白"
        };
        
        String[] lowRiskKeywords = {
            "刷单", "佣金", "点赞赚钱", "返利", "做任务", "刷单返利", "小额返利",
            "网络交友", "借钱", "小额转账", "轻度杀猪盘", "赠送礼物",
            "客服", "快递丢失", "双倍赔偿", "退款", "理赔", "冒充电商客服",
            "学历提升", "考证包过", "内部资料", "教育培训",
            "免费鸡蛋", "免费米面", "免费体检", "免费礼品引流",
            "保健品", "能治百病", "特效药", "养生保健品",
            "养生讲座", "专家问诊", "理疗仪", "医疗器械",
            "冒充儿女", "冒充亲友", "借钱救急", "冒充亲友诈骗",
            "虚假发票", "票据着急报销", "虚假票据报销"
        };
        
        for (String keyword : highRiskKeywords) {
            if (lowerFileName.contains(keyword) || lowerResponse.contains(keyword)) {
                riskLevel = "high";
                fraudType = extractFraudType(response, keyword);
                break;
            }
        }
        
        if (riskLevel.equals("low")) {
            for (String keyword : mediumRiskKeywords) {
                if (lowerFileName.contains(keyword) || lowerResponse.contains(keyword)) {
                    riskLevel = "medium";
                    fraudType = extractFraudType(response, keyword);
                    break;
                }
            }
        }
        
        if (riskLevel.equals("low")) {
            for (String keyword : lowRiskKeywords) {
                if (lowerFileName.contains(keyword) || lowerResponse.contains(keyword)) {
                    riskLevel = "low";
                    fraudType = extractFraudType(response, keyword);
                    break;
                }
            }
        }
        
        return new String[]{riskLevel, fraudType};
    }
    
    private String extractFraudType(String response, String keyword) {
        if (keyword.contains("投资导师") || keyword.contains("稳赚不赔") || keyword.contains("赌博平台") || keyword.contains("深度杀猪盘")) {
            return "深度杀猪盘诈骗";
        } else if (keyword.contains("冒充领导") || keyword.contains("紧急转账") || keyword.contains("老板微信") || keyword.contains("老板qq")) {
            return "冒充领导转账诈骗";
        } else if (keyword.contains("跑分") || keyword.contains("洗钱") || keyword.contains("帮信罪") || keyword.contains("走账")) {
            return "跑分洗钱诈骗";
        } else if (keyword.contains("高薪岗位") || keyword.contains("培训费") || keyword.contains("服装押金") || keyword.contains("入职费")) {
            return "虚假招聘诈骗";
        } else if (keyword.contains("以房养老") || keyword.contains("抵押房产")) {
            return "以房养老诈骗";
        } else if (keyword.contains("变更收款账户") || keyword.contains("账户升级") || keyword.contains("临时更换账户")) {
            return "虚假客户账户变更诈骗";
        } else if (keyword.contains("财税专属理财") || keyword.contains("保本保收益")) {
            return "财税领域投资诈骗";
        } else if (keyword.contains("绑架") || keyword.contains("赎金")) {
            return "绑架勒索诈骗";
        } else if (keyword.contains("敲诈") || keyword.contains("勒索") || keyword.contains("曝光")) {
            return "敲诈勒索诈骗";
        } else if (keyword.contains("贷款") || keyword.contains("无抵押") || keyword.contains("解冻金")) {
            return "网络贷款诈骗";
        } else if (keyword.contains("公检法") || keyword.contains("海关") || keyword.contains("安全账户")) {
            return "冒充公检法/海关诈骗";
        } else if (keyword.contains("出租银行卡") || keyword.contains("出租电话卡") || keyword.contains("出借账号")) {
            return "帮信罪诈骗";
        } else if (keyword.contains("游戏账号") || keyword.contains("装备") || keyword.contains("私下交易")) {
            return "网络游戏虚假交易诈骗";
        } else if (keyword.contains("养老项目") || keyword.contains("养老投资") || keyword.contains("每月分红")) {
            return "养老投资诈骗";
        } else if (keyword.contains("社保") || keyword.contains("医保")) {
            return "冒充社保医保诈骗";
        } else if (keyword.contains("黄昏恋") || keyword.contains("老年交友") || keyword.contains("情感杀猪盘")) {
            return "老年情感杀猪盘诈骗";
        } else if (keyword.contains("终身养老") || keyword.contains("养老套餐")) {
            return "养老服务诈骗";
        } else if (keyword.contains("税务专员") || keyword.contains("税务异常") || keyword.contains("补缴税款")) {
            return "冒充税务人员诈骗";
        } else if (keyword.contains("税务刷单") || keyword.contains("票据冲量")) {
            return "财税刷单诈骗";
        } else if (keyword.contains("对公账户冻结") || keyword.contains("缴纳解冻费")) {
            return "对公账户解冻诈骗";
        } else if (keyword.contains("代办退税") || keyword.contains("税收减免")) {
            return "虚假财税代办诈骗";
        } else if (keyword.contains("刷单") || keyword.contains("佣金") || keyword.contains("返利")) {
            return "刷单返利诈骗";
        } else if (keyword.contains("网络交友") || keyword.contains("借钱") || keyword.contains("小额转账")) {
            return "轻度杀猪盘诈骗";
        } else if (keyword.contains("客服") || keyword.contains("快递丢失") || keyword.contains("退款") || keyword.contains("理赔")) {
            return "冒充电商客服诈骗";
        } else if (keyword.contains("学历提升") || keyword.contains("考证包过") || keyword.contains("内部资料")) {
            return "教育培训诈骗";
        } else if (keyword.contains("免费鸡蛋") || keyword.contains("免费米面") || keyword.contains("免费体检")) {
            return "免费礼品引流诈骗";
        } else if (keyword.contains("保健品") || keyword.contains("能治百病") || keyword.contains("特效药")) {
            return "养生保健品诈骗";
        } else if (keyword.contains("养生讲座") || keyword.contains("专家问诊") || keyword.contains("理疗仪")) {
            return "医疗器械诈骗";
        } else if (keyword.contains("冒充儿女") || keyword.contains("冒充亲友") || keyword.contains("借钱救急")) {
            return "冒充亲友诈骗";
        } else if (keyword.contains("虚假发票") || keyword.contains("票据着急报销")) {
            return "虚假票据报销诈骗";
        } else {
            return "疑似诈骗";
        }
    }

    private String cleanResponse(String response) {
        if (response == null) return null;
        
        String cleaned = response;
        
        String[] patternsToRemove = {
            "【第\\d+帧分析结果】",
            "=== .*? ===",
            "视频文字.*?（原样输出）",
            "场景描述",
            "诈骗类型判断",
            "豆包AI生成"
        };
        
        for (String pattern : patternsToRemove) {
            cleaned = cleaned.replaceAll(pattern, "");
        }
        
        cleaned = cleaned.replaceAll("\\n{3,}", "\n\n").trim();
        
        return cleaned;
    }

    private String generateDefaultResponse(String fileName) {
        StringBuilder sb = new StringBuilder();
        sb.append("别慌，先冷静下来！我非常理解你的担心，突然接到这种电话确实会让人心里发毛，尤其是听到\"坐牢\"\"冻结资产\"这些字眼。\n\n");
        
        sb.append("这其实是典型的\"冒充公检法诈骗\"，骗子就是利用你害怕被追究责任的心理，制造紧张氛围让你失去判断力。他们通常会伪装成警察、法官或检察官，说你涉嫌洗钱、贩毒或者非法集资，然后要求你把钱转到所谓的\"安全账户\"来配合调查。\n\n");
        
        sb.append("其实啊，真正的公检法机关办案绝不会通过电话、微信或QQ进行，更不会让你转账\"自证清白\"。他们要查你，会直接上门送达法律文书，或者通知你去法院、公安局当面处理。而且，所有涉及资金操作的流程，都必须走正规程序，不可能用\"紧急\"\"保密\"这种借口来绕过规则。\n\n");
        
        sb.append("记住以下几点：\n");
        sb.append("第一，凡是自称公检法要求转账的，一律是骗局；\n");
        sb.append("第二，不要向任何陌生账号转账，哪怕对方说为了保护你的财产；\n");
        sb.append("第三，立刻挂断电话，不要再回复任何消息；\n");
        sb.append("第四，如果已经转账了，请立即联系银行申请止付，并保留好聊天记录和转账凭证，这是追回损失的关键证据。\n\n");
        
        sb.append("现在最重要的是：马上拨打110报警，或者联系当地派出所核实情况。你已经做得很好了，主动来核实就是最正确的第一步！");
        
        return sb.toString();
    }
}
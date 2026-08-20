package com.antifraudqi.antifraudaiagent.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * AI 劝导话术服务
 * 根据升级方案 V2.3（Section 3.3.2）
 * 当风险评估为 HIGH 或 EXTREME 时，自动生成口语化劝阻话术
 */
@Slf4j
@Service
public class PersuasionService {

    /**
     * 诈骗类型 -> 人群 -> 劝导话术 映射表
     */
    private static final Map<String, Map<String, String>> PERSUASION_MESSAGES = new ConcurrentHashMap<>();

    static {
        // ===== 冒充公检法诈骗 =====
        Map<String, String> impersonation = new ConcurrentHashMap<>();
        impersonation.put("elderly", "老伙计，听我一句劝！真正的警察不会打电话让你转账的。你先挂掉电话，有什么事情咱当面说清楚！千万别把养老钱转给陌生人。");
        impersonation.put("youth", "哥们，这是典型的冒充公检法诈骗！公检法机关绝对不会通过电话办案，更不会让你转账「自证清白」，千万别信！直接挂断拉黑。");
        impersonation.put("child", "小朋友，警察叔叔不会打电话让小孩子的转账的！这是骗子，快告诉爸爸妈妈，不要自己处理。");
        impersonation.put("accountant", "注意：冒充公检法诈骗！公检法机关不会通过电话办案、不设安全账户、不要求转账。请立即挂断电话，切勿向任何陌生账户转账。");
        impersonation.put("worker", "这是冒充公检法诈骗！千万别信！公检法机关不会打电话让你转账，更不会让你「配合调查」转钱到安全账户。直接挂断！");
        impersonation.put("default", "请注意：冒充公检法诈骗！请立即挂断电话，不要向任何陌生账户转账！");
        PERSUASION_MESSAGES.put("冒充公检法诈骗", impersonation);

        // ===== 刷单返利诈骗 =====
        Map<String, String> shuadan = new ConcurrentHashMap<>();
        shuadan.put("youth", "我知道你想搞点钱，但刷单这种「先垫资后返利」的全是诈骗！小额返利是诱饵，等你大额投入就拉黑跑路了。及时止损！");
        shuadan.put("elderly", "老伙计，刷单返利都是骗人的！先让你尝点甜头，等你投大钱进去就再也联系不上人了。千万别信！");
        shuadan.put("child", "小朋友，刷单返利是骗人的！不要相信网上说的「轻松赚钱」，都是骗你零花钱的。");
        shuadan.put("worker", "刷单返利诈骗！已经垫付的钱不要再追加了，立刻停止操作！正规兼职不会让你先交钱，任何垫资都是诈骗。");
        shuadan.put("accountant", "刷单返利属于典型诈骗手段，所有「先垫资后返利」的兼职均为诈骗，请立即停止操作并报警。");
        shuadan.put("default", "这是刷单返利诈骗！已经垫付的钱不要再追加了，立刻停止操作！");
        PERSUASION_MESSAGES.put("刷单返利诈骗", shuadan);

        // ===== 杀猪盘/投资理财诈骗 =====
        Map<String, String> shazhupan = new ConcurrentHashMap<>();
        shazhupan.put("youth", "网恋对象带你投资赚钱？这是「杀猪盘」诈骗！不要转账，不要投资，立刻拉黑！真正的投资不会通过网恋对象推荐。");
        shazhupan.put("elderly", "老伙计，网上认识的「朋友」让你投资赚钱，这是骗局！先骗感情后骗钱，千万别信。养老钱来之不易。");
        shazhupan.put("accountant", "这是典型的杀猪盘诈骗，通过网络交友诱导投资/赌博，百分百为诈骗。请立即停止所有转账操作。");
        shazhupan.put("worker", "杀猪盘诈骗！网上认识的「投资导师」带你赚钱，全是假的！平台后台能操控，你投进去的钱一分都拿不回来。");
        shazhupan.put("default", "网恋对象带你投资赚钱？这是「杀猪盘」诈骗！不要转账，不要投资，立刻拉黑！");
        PERSUASION_MESSAGES.put("杀猪盘诈骗", shazhupan);

        // ===== 冒充客服诈骗 =====
        Map<String, String> kefu = new ConcurrentHashMap<>();
        kefu.put("elderly", "老伙计，这是冒充客服诈骗！电商平台不会主动打电话给你退款，更不会要银行卡号和验证码。挂掉电话！");
        kefu.put("youth", "冒充客服诈骗！任何主动联系你说「退款」「理赔」的，都直接去官方APP核实，不要通过对方给的链接操作。");
        kefu.put("default", "这是冒充客服诈骗！不要通过对方提供的链接操作，直接在官方APP核实，索要验证码的全是诈骗！");
        PERSUASION_MESSAGES.put("冒充客服诈骗", kefu);

        // ===== 网络贷款诈骗 =====
        Map<String, String> loan = new ConcurrentHashMap<>();
        loan.put("youth", "网贷诈骗！「无抵押秒到账」都是诱饵，让你先交保证金、解冻费的全是诈骗！正规贷款不会提前收费。");
        loan.put("worker", "网贷诈骗！急需用钱也不能信「先交钱再放款」的套路，保证金、解冻费、刷流水全是骗人的。去正规银行！");
        loan.put("default", "这是网络贷款诈骗！凡是贷款前要求交保证金、解冻费、刷流水的都是诈骗！");
        PERSUASION_MESSAGES.put("网络贷款诈骗", loan);

        // ===== 冒充熟人领导诈骗 =====
        Map<String, String> familiar = new ConcurrentHashMap<>();
        familiar.put("accountant", "冒充领导诈骗！紧急要求转账的，请务必电话或当面核实身份，切勿仅凭微信/QQ消息转账！");
        familiar.put("elderly", "老伙计，冒充熟人借钱诈骗！如果有人打电话说「我是你儿子/女儿」要钱，先挂掉电话打过去核实。");
        familiar.put("default", "这是冒充熟人领导诈骗！请务必通过电话、视频等方式核实对方身份，切勿盲目转账！");
        PERSUASION_MESSAGES.put("冒充熟人领导诈骗", familiar);

        // ===== AI换脸诈骗 =====
        Map<String, String> aiFace = new ConcurrentHashMap<>();
        aiFace.put("default", "AI换脸诈骗！现在的AI技术可以伪造他人面部和声音，视频通话借钱也要通过其他方式二次核实！");
        aiFace.put("elderly", "老伙计，现在的AI能模仿人的声音和样子！视频里看到熟人借钱也要打电话确认，千万别直接转账。");
        aiFace.put("youth", "AI换脸诈骗！视频通话都能是假的，遇到熟人借钱一定要通过电话、见面等方式再核实一遍。");
        PERSUASION_MESSAGES.put("AI换脸诈骗", aiFace);

        // ===== 游戏诈骗 =====
        Map<String, String> game = new ConcurrentHashMap<>();
        game.put("child", "小朋友，网上说「免费送游戏皮肤」的都是骗子！不要相信，不要扫码，不要告诉爸爸妈妈的支付密码！");
        game.put("youth", "游戏诈骗！「免费皮肤」「低价代充」「解除防沉迷」全是骗局，不要给陌生人账号密码，不要扫码转账。");
        game.put("default", "这是游戏诈骗！凡是「免费送皮肤」「低价代充」的都不要信，找官方渠道交易。");
        PERSUASION_MESSAGES.put("游戏诈骗", game);

        // ===== 保健品诈骗 =====
        Map<String, String> health = new ConcurrentHashMap<>();
        health.put("elderly", "老伙计，保健品不能治病！「能治百病」「特效药」「纯中药」都是骗人的，看病要去正规医院。别花冤枉钱！");
        health.put("default", "这是保健品诈骗！凡是声称「能治百病」的保健品均为诈骗，请到正规医院就诊。");
        PERSUASION_MESSAGES.put("保健品诈骗", health);

        // ===== 征信修复诈骗 =====
        Map<String, String> credit = new ConcurrentHashMap<>();
        credit.put("youth", "征信修复诈骗！征信记录由央行统一管理，任何声称可以「人工修复征信」「洗白逾期」的都是诈骗。");
        credit.put("default", "这是征信修复诈骗！征信记录由央行统一管理，无法人工修复，切勿相信！");
        PERSUASION_MESSAGES.put("征信修复诈骗", credit);

        // ===== 跑分洗钱诈骗 =====
        Map<String, String> running = new ConcurrentHashMap<>();
        running.put("youth", "跑分洗钱是严重违法犯罪！不要为了「一笔提成」出租银行卡、电话卡，这属于帮信罪，会坐牢的！");
        running.put("worker", "跑分洗钱是违法！帮忙转账走账就能拿提成，这是洗钱犯罪，一分钱都不要碰！");
        running.put("default", "跑分洗钱属于违法犯罪行为，参与跑分将面临刑事责任，请立即拒绝并报警！");
        PERSUASION_MESSAGES.put("跑分洗钱诈骗", running);

        // ===== 中奖诈骗 =====
        Map<String, String> prize = new ConcurrentHashMap<>();
        prize.put("elderly", "老伙计，你没参加过的活动怎么会中奖？让你先交税、交手续费才能领奖的，全是骗子！");
        prize.put("child", "小朋友，网上说「免费领奖品」要先交钱的都是骗子！不要转账，不要扫码！");
        prize.put("default", "这是中奖诈骗！凡是「未参与却中奖」且要求先交税费、手续费才能领奖的，都是诈骗！");
        PERSUASION_MESSAGES.put("中奖诈骗", prize);

        // ===== 默认通用劝导 =====
        Map<String, String> defaultMsg = new ConcurrentHashMap<>();
        defaultMsg.put("elderly", "老伙计，您可能正在遭遇诈骗！请先停下来，不要转账，不要告诉对方验证码，有什么问题先跟家人商量，或拨打110咨询。");
        defaultMsg.put("youth", "哥们，冷静一下！这很可能是诈骗。先别转账，别给验证码，凡事多留个心眼，拿不准的可以打96110反诈专线问问。");
        defaultMsg.put("child", "小朋友，遇到这种事情先不要慌！不要告诉陌生人你的信息，赶紧告诉爸爸妈妈或者老师！");
        defaultMsg.put("accountant", "提醒：您可能正在遭遇诈骗！请先暂停所有转账操作，核实对方身份后再处理。涉及公司资金请务必遵守财务审批流程。");
        defaultMsg.put("worker", "先别急！这很可能是诈骗。你先停下来想一想，正规的事不会让你这么着急转账的。拿不准可以打96110咨询。");
        defaultMsg.put("default", "请注意：您可能正在遭遇诈骗！请先暂停当前操作，不要转账，不要提供验证码，谨慎核实对方身份。");
        PERSUASION_MESSAGES.put("default", defaultMsg);
    }

    /**
     * 根据诈骗类型、风险等级和用户角色生成劝导话术
     *
     * @param fraudType  诈骗类型
     * @param riskLevel  风险等级 (HIGH/EXTREME)
     * @param userRole   用户角色 (elderly/youth/child/accountant/worker)
     * @return 劝导话术字符串
     */
    public String generatePersuasion(String fraudType, String riskLevel, String userRole) {
        log.info("生成劝导话术: fraudType={}, riskLevel={}, userRole={}", fraudType, riskLevel, userRole);

        // 低风险不劝导
        if ("LOW".equalsIgnoreCase(riskLevel) || "MEDIUM".equalsIgnoreCase(riskLevel)) {
            return null;
        }

        // 获取诈骗类型对应的劝导话术
        Map<String, String> typeMessages = PERSUASION_MESSAGES.get(fraudType);
        if (typeMessages == null) {
            typeMessages = PERSUASION_MESSAGES.get("default");
        }

        // 获取用户角色对应的话术，如果没有则使用default
        String message = typeMessages.get(userRole);
        if (message == null) {
            message = typeMessages.get("default");
        }
        if (message == null) {
            message = PERSUASION_MESSAGES.get("default").get("default");
        }

        // 高风险追加紧急提示
        if ("EXTREME".equalsIgnoreCase(riskLevel)) {
            message += "\n\n\u26a0\uFE0F 紧急提醒：您当前面临极高风险！请立即停止操作，不要转账，并拨打 110 报警！";
        }

        log.info("劝导话术生成成功");
        return message;
    }

    /**
     * 获取诈骗类型对应的劝导话术
     * 用于前端展示可选劝导内容
     */
    public Map<String, Map<String, String>> getAllPersuasionMessages() {
        return PERSUASION_MESSAGES;
    }
}
package com.antifraud.admin.domain;

import java.util.HashMap;
import java.util.Map;

/**
 * 统一响应结果封装（若依风格）
 */
public class AjaxResult extends HashMap<String, Object> {

    private static final long serialVersionUID = 1L;

    /** 状态码 */
    public static final String CODE_TAG = "code";
    /** 返回消息 */
    public static final String MSG_TAG = "msg";
    /** 数据对象 */
    public static final String DATA_TAG = "data";

    /** 成功状态码 */
    public static final int SUCCESS = 200;
    /** 失败状态码 */
    public static final int FAIL = 500;
    /** 未授权状态码 */
    public static final int UNAUTHORIZED = 401;
    /** 无权限状态码 */
    public static final int FORBIDDEN = 403;

    /**
     * 初始化一个新创建的 AjaxResult 对象
     */
    public AjaxResult() {
    }

    /**
     * 初始化一个新创建的 AjaxResult 对象
     */
    public AjaxResult(int code, String msg) {
        super.put(CODE_TAG, code);
        super.put(MSG_TAG, msg);
    }

    /**
     * 初始化一个新创建的 AjaxResult 对象
     */
    public AjaxResult(int code, String msg, Object data) {
        super.put(CODE_TAG, code);
        super.put(MSG_TAG, msg);
        if (data != null) {
            super.put(DATA_TAG, data);
        }
    }

    /**
     * 返回成功消息
     */
    public static AjaxResult success() {
        return AjaxResult.success("操作成功");
    }

    /**
     * 返回成功数据
     */
    public static AjaxResult success(Object data) {
        return AjaxResult.success("操作成功", data);
    }

    /**
     * 返回成功消息
     */
    public static AjaxResult success(String msg) {
        return AjaxResult.success(msg, null);
    }

    /**
     * 返回成功消息
     */
    public static AjaxResult success(String msg, Object data) {
        return new AjaxResult(SUCCESS, msg, data);
    }

    /**
     * 返回错误消息
     */
    public static AjaxResult error() {
        return AjaxResult.error("操作失败");
    }

    /**
     * 返回错误消息
     */
    public static AjaxResult error(String msg) {
        return AjaxResult.error(msg, null);
    }

    /**
     * 返回错误消息
     */
    public static AjaxResult error(String msg, Object data) {
        return new AjaxResult(FAIL, msg, data);
    }

    /**
     * 返回错误消息
     */
    public static AjaxResult error(int code, String msg) {
        return new AjaxResult(code, msg, null);
    }

    /**
     * 返回未授权消息
     */
    public static AjaxResult unauthorized(String msg) {
        return new AjaxResult(UNAUTHORIZED, msg, null);
    }

    /**
     * 返回无权限消息
     */
    public static AjaxResult forbidden(String msg) {
        return new AjaxResult(FORBIDDEN, msg, null);
    }

    @Override
    public AjaxResult put(String key, Object value) {
        super.put(key, value);
        return this;
    }

    /**
     * 获取状态码
     */
    public int getCode() {
        return (int) super.get(CODE_TAG);
    }

    /**
     * 获取返回消息
     */
    public String getMsg() {
        return (String) super.get(MSG_TAG);
    }

    /**
     * 获取数据对象
     */
    public Object getData() {
        return super.get(DATA_TAG);
    }
}
package com.antifraudqi.antifraudaiagent.service;

import lombok.extern.slf4j.Slf4j;
import org.bytedeco.javacv.FFmpegFrameGrabber;
import org.bytedeco.javacv.Frame;
import org.bytedeco.javacv.Java2DFrameConverter;
import org.springframework.stereotype.Component;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

@Slf4j
@Component
public class VideoFrameExtractor {

    private static final int DEFAULT_MAX_FRAMES = 5;
    private static final int MAX_VIDEO_SIZE = 100 * 1024 * 1024; // 100MB

    public List<String> extractKeyFrames(byte[] videoData, int maxFrames) {
        List<String> base64Frames = new ArrayList<>();
        
        if (videoData == null || videoData.length == 0) {
            log.error("视频数据为空");
            return base64Frames;
        }
        
        if (videoData.length > MAX_VIDEO_SIZE) {
            log.warn("视频文件过大: {} bytes, 超过限制 {} bytes", videoData.length, MAX_VIDEO_SIZE);
        }
        
        FFmpegFrameGrabber grabber = null;
        Java2DFrameConverter converter = null;

        try {
            ByteArrayInputStream inputStream = new ByteArrayInputStream(videoData);
            grabber = new FFmpegFrameGrabber(inputStream);
            grabber.start();
            
            converter = new Java2DFrameConverter();
            
            int totalFrames = grabber.getLengthInFrames();
            log.info("视频总帧数: {}", totalFrames);
            
            if (totalFrames <= 0) {
                totalFrames = 100;
                log.warn("无法获取视频总帧数，使用默认值: {}", totalFrames);
            }
            
            int frameInterval = Math.max(1, totalFrames / maxFrames);
            int startOffset = frameInterval / 2;
            
            log.info("抽帧参数: 总帧数={}, 抽帧间隔={}, 起始偏移={}, 目标帧数={}", 
                    totalFrames, frameInterval, startOffset, maxFrames);

            int frameIndex = 0;
            int extractedCount = 0;
            Frame frame;

            while ((frame = grabber.grabImage()) != null && extractedCount < maxFrames) {
                if (frameIndex >= startOffset && (frameIndex - startOffset) % frameInterval == 0) {
                    BufferedImage image = converter.convert(frame);
                    if (image != null) {
                        ByteArrayOutputStream baos = new ByteArrayOutputStream();
                        ImageIO.write(image, "jpg", baos);
                        byte[] imageBytes = baos.toByteArray();
                        String base64 = Base64.getEncoder().encodeToString(imageBytes);
                        base64Frames.add(base64);
                        extractedCount++;
                        log.info("成功抽取第{}帧 (视频帧索引: {})", extractedCount, frameIndex);
                    }
                }
                frameIndex++;
            }

            log.info("视频抽帧完成，共抽取{}帧", base64Frames.size());

        } catch (Exception e) {
            log.error("视频抽帧失败: {}", e.getMessage(), e);
        } finally {
            if (converter != null) {
                try {
                    converter.close();
                } catch (Exception e) {
                    log.warn("关闭转换器失败", e);
                }
            }
            if (grabber != null) {
                try {
                    grabber.stop();
                    grabber.close();
                } catch (Exception e) {
                    log.warn("释放视频资源失败", e);
                }
            }
        }

        return base64Frames;
    }
}

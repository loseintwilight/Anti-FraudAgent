package com.antifraudqi.antifraudaiagent.tools;

import cn.hutool.core.io.FileUtil;
import cn.hutool.core.io.IORuntimeException;
import com.antifraudqi.antifraudaiagent.constant.FileConstant;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Component;

@Component
public class FileOperationTool {
    private final String FILE_DIR = FileConstant.FILE_SAVE_DIR + "/file";
    @Tool(description = "Read content from a file")
    public String readFile(@ToolParam(description = "Name of the file to read") String fileName){
        String filePath = FILE_DIR + "/" + fileName;
        try {
            String result = FileUtil.readUtf8String(filePath);
            System.out.println("读取到的文件内容：" + result);
            return result;
        } catch (IORuntimeException e) {
            return "Error reading file: " + e.getMessage();
        }
    }

    @Tool(description = "Write content to a file")
    public String writeFile(@ToolParam(description = "Name of the file to write") String fileName,
                             @ToolParam(description = "Content to write to the file") String content){
        try {
            String filePath = FILE_DIR + "/" + fileName;
            FileUtil.mkdir(FILE_DIR);
            FileUtil.writeUtf8String(content, filePath);
            return "File written successfully to:" + filePath;
        } catch (IORuntimeException e) {
            return "Error writing to file: " + e.getMessage();
        }
    }
}

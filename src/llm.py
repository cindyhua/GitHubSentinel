import os
import json
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块
from enum import Enum

class PromptType(Enum):
    HACK_NEWS = "prompts/hack_news_hour_report_prompt.txt"
    GITHUB = "prompts/github_report_prompt.txt"

class LLM:
    def __init__(self, config_json: str):
        # 解析 JSON 配置
        config = json.loads(config_json)

        # 设置默认值，然后用配置中的值覆盖
        self.model = config.get('model', 'deepseek-chat')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 1500)
        # 创建一个OpenAI客户端实例
        self.client = OpenAI(api_key="sk-d1b9c9c5bb674469afac87b36e73c25b", base_url="https://api.deepseek.com")
        
        # 获取 report_type 并转换为 PromptType 枚举
        report_type_str = config.get('report_type', 'GITHUB')
        self.report_type = PromptType[report_type_str]

        # 读取指定的 prompt 文件
        prompt_file = self.report_type.value
        prompt_path = os.path.join(os.path.dirname(__file__), '..', prompt_file)
        with open(prompt_path, "r", encoding='utf-8') as file:
            self.system_prompt = file.read()

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 使用从TXT文件加载的提示信息
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": markdown_content},
        ]


        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt已保存到 daily_progress/prompt.txt")

            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("使用 GPT 模型开始生成报告。")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model=self.model,  # 指定使用的模型版本
                messages=messages
            )
            LOG.debug("messages:{}",messages)
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error(f"生成报告时发生错误：{e}")
            raise

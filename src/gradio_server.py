import gradio as gr  # 导入gradio库用于创建GUI

from config import Config, ReportType  # 确保从 config 模块导入 ReportType
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器
import json  # 导入json模块用于处理JSON配置

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)

subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(report_type, repo, days):
    llm_config = {
        "report_type": report_type,
        # 其他需要的配置项...
    }
    llm = LLM(json.dumps(llm_config))
    report_generator = ReportGenerator(llm)

    if report_type == ReportType.GITHUB.value:
        raw_file_path = github_client.export_progress_by_date_range(repo, days)
    elif report_type == ReportType.HACK_NEWS.value:
        # 这里需要实现 HackerNews 的逻辑
        # 假设我们有一个 hackernews_client
        from hackNews_client import HackerNewsClient
        hackernews_client = HackerNewsClient()
        raw_file_path = hackernews_client.fetch_and_save(1,days)
    else:
        raise ValueError(f"Unsupported report type: {report_type}")
    
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)
    return report, report_file_path

def update_subscription_list(report_type):
    print("report_type:" + report_type)
    if report_type == ReportType.GITHUB.value:
        subscriptions = subscription_manager.list_subscriptions()
        return gr.Dropdown(choices=subscriptions)
    elif report_type == ReportType.HACK_NEWS.value:
        return gr.Dropdown(choices=["HackerNews"], value="HackerNews")
    else:
        return gr.Dropdown(choices=[], value=None) 

# Create Gradio interface
with gr.Blocks(title="GitHubSentinel") as demo:
    with gr.Row():
        report_type = gr.Dropdown(
            choices=config.report_types,
            label="报告类型",
            info="选择报告类型"
        )
        subscription_list = gr.Dropdown(
            choices=subscription_manager.list_subscriptions(),  # 初始为空，将根据报告类型动态更新
            label="订阅列表",
            info="已订阅项目"
        )
        days = gr.Slider(
            value=2, 
            minimum=1, 
            maximum=7, 
            step=1, 
            label="报告周期", 
            info="生成项目过去一段时间进展，单位：天"
        )
    
    with gr.Row():
        submit_btn = gr.Button("生成报告")
    
    with gr.Row():
        output_markdown = gr.Markdown()
        output_file = gr.File(label="下载报告")
    
    submit_btn.click(
        fn=export_progress_by_date_range,
        inputs=[report_type, subscription_list, days],
        outputs=[output_markdown, output_file]
    )
    
    report_type.change(
        fn=update_subscription_list,
        inputs=[report_type],
        outputs=[subscription_list]
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
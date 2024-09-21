import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
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
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def update_subscription_list(report_type):
    if report_type == "GITHUB":
        return gr.Dropdown.update(choices=subscription_manager.list_subscriptions(), interactive=True)
    else:
        return gr.Dropdown.update(choices=[], value=None, interactive=False)

# 创建Gradio界面
demo = gr.Interface(
    fn=export_progress_by_date_range,  # 指定界面调用的函数
    title="GitHubSentinel",  # 设置界面标题
    inputs=[
        gr.Dropdown(
            choices=config.report_types,
            label="报告类型",
            info="选择报告类型"
        ),
        gr.Dropdown(
            choices=subscription_manager.list_subscriptions(),
            label="订阅列表",
            info="已订阅GitHub项目"
        ),
        gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),
    ],
    outputs=[gr.Markdown(), gr.File(label="下载报告")],  # 输出格式：Markdown文本和文件下载
)

demo.inputs[0].change(fn=update_subscription_list, inputs=[demo.inputs[0]], outputs=[demo.inputs[1]])

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
"""
麦田智囊 CLI工具
命令行接口 — 通过 AgentFactory 统一创建 Agent，确保依赖注入生效
"""

import os
from typing import TYPE_CHECKING, Dict

import click
from dotenv import load_dotenv

from maitian_agent.agents.factory import AgentFactory

if TYPE_CHECKING:
    from maitian_agent.agents.base import BaseAgent

load_dotenv()


def _create_factory() -> AgentFactory:
    """创建 AgentFactory 实例，统一管理所有 Agent 的依赖注入。

    CLI 入口通过此函数获取 Factory，确保 RAG/记忆/工具等
    依赖在所有 Agent 中一致生效。

    Returns:
        配置好的 AgentFactory 实例。
    """
    return AgentFactory()


def _get_agents() -> Dict[str, "BaseAgent"]:
    """通过 AgentFactory.create_all() 获取所有 Agent 实例。

    Returns:
        Dict[agent_type, BaseAgent] — 所有已注册的 Agent。
    """
    factory = _create_factory()
    return factory.create_all()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """麦田智囊 - 乡村教育Agent系统 CLI工具"""
    pass


@cli.command()
@click.option("--subject", "-s", required=True, help="学科")
@click.option("--grade", "-g", required=True, help="年级")
@click.option("--topic", "-t", required=True, help="课题")
@click.option("--context", "-c", default="", help="乡村特色情境")
def lesson_prep(subject: str, grade: str, topic: str, context: str) -> None:
    """极速备课：生成乡土化教案。

    通过 AgentFactory 创建 QuickLessonPrepAgent，确保 RAG/记忆/画像注入生效。
    输入参数组装为 Dict，遵循 run(Dict→Dict) 接口契约。
    """
    click.echo(f"正在为 {subject} {grade} 生成教案...")
    agents = _get_agents()
    agent = agents["quick_lesson_prep"]
    result = agent.run(
        {
            "subject": subject,
            "grade": grade,
            "topic": topic,
            "rural_context": context,
        }
    )
    click.echo("\n" + "=" * 50)
    click.echo("生成的教案：")
    click.echo("=" * 50)
    click.echo(result.get("result", result))


@cli.command()
@click.option("--image", "-i", required=True, help="手写教案图片路径")
def wisdom_transfer(image: str) -> None:
    """智慧传承：识别并结构化手写教案。

    通过 AgentFactory 创建 WisdomTransferAgent，确保 OCR/记忆注入生效。
    输入参数组装为 Dict，遵循 run(Dict→Dict) 接口契约。
    """
    if not os.path.exists(image):
        click.echo(f"错误：文件 {image} 不存在")
        return

    click.echo(f"正在处理 {image} ...")
    agents = _get_agents()
    agent = agents["wisdom_transfer"]
    result = agent.run({"image_path": image})
    click.echo("\n" + "=" * 50)
    click.echo("处理结果：")
    click.echo("=" * 50)
    click.echo(result.get("result", result))


@cli.command()
@click.option("--input", "-i", required=True, help="用户输入")
def route(input: str) -> None:
    """意图路由：识别用户意图。

    通过 AgentFactory 创建 RouterAgent，遵循 run(Dict→Dict) 接口契约。
    """
    agents = _get_agents()
    agent = agents["router"]
    result = agent.run({"user_input": input})
    click.echo(f"\n识别结果：{result.get('intent')}")
    click.echo(f"描述：{result.get('info', {}).get('description', '')}")


@cli.command()
def agents_list() -> None:
    """列出所有可用Agent。

    通过 AgentFactory.create_all() 获取所有已注册的 Agent。
    """
    agents = _get_agents()
    click.echo("\n可用Agent列表：")
    for agent_type, agent in agents.items():
        click.echo(f"  - {agent_type}: {agent.name}")


if __name__ == "__main__":
    cli()

from openai import OpenAI
from llm_easy_tools import get_tool_defs

from agentiq.logger import logger
from agentiq.core.tool import Tool
from agentiq.settings import BASE_URL, API_KEY, MODEL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def generate(messages: list[dict], tools: list[Tool]):
    logger.info(messages)

    response = client.chat.completions.create(
        model=MODEL, messages=messages, tools=get_tool_defs(tool.tool_function for tool in tools)
    )

    logger.info(response)
    return response.choices[0]

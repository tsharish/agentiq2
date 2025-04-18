import json
from types import FunctionType

from agentiq.settings import BASE_URL
from agentiq.core.llm import generate
from agentiq.core.tool import Tool

INSTRUCTION = "You are an AI assistant that can use tools to perform actions. Explain your reasoning to the user before using a tool. "


class Agent:
    def __init__(self, tools: list[Tool], system_message: str | FunctionType | None = None) -> None:
        self.session_id = 0
        self.memory: dict[int, list[dict]] = {}
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.system_message = system_message

    def run(self, message: str, session_id: int | None = None):
        if session_id is None:
            self.session_id += 1
            session_id = self.session_id

            if isinstance(self.system_message, str):
                system_message = INSTRUCTION + self.system_message
            elif isinstance(self.system_message, FunctionType):
                system_message = INSTRUCTION + self.system_message()
            elif self.system_message is None:
                system_message = INSTRUCTION
            else:
                raise TypeError(
                    "System message must either be a string or a function that returns a string"
                )

            self.memory[session_id] = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": message},
            ]
        elif session_id not in self.memory:
            raise ValueError(f"Session ID {session_id} does not exist.")
        else:
            self.memory[session_id].append({"role": "user", "content": message})

        response = generate(messages=self.memory[session_id], tools=self.tools)

        max_iterations = 10  # Safety check to prevent infinite loops
        while response.message.tool_calls is not None and max_iterations > 0:
            max_iterations -= 1

            if response.message.content:
                yield json.dumps(
                    {"session_id": session_id, "content": response.message.content}
                ) + "\n"

            if BASE_URL and "googleapis" in BASE_URL:
                # https://ai.google.dev/gemini-api/docs/function-calling?example=meeting (Step 4)
                self.memory[session_id].append(
                    {
                        "role": "assistant",
                        "content": str(self._format_assistant_response(response.message)),
                    }
                )
            else:
                # https://platform.openai.com/docs/guides/function-calling#function-calling-steps
                self.memory[session_id].append(response.message)

            for tool_call in response.message.tool_calls:
                tool = self.tool_map[tool_call.function.name]
                if not tool:
                    raise ValueError(f"Tool {tool_call.function.name} not found.")

                yield json.dumps(
                    {
                        "session_id": session_id,
                        "content": f"Invoking tool {tool_call.function.name}",
                    }
                ) + "\n"

                try:
                    tool_inputs = json.loads(tool_call.function.arguments)
                    tool_output = tool.run(**tool_inputs)
                except Exception as e:
                    tool_output = f"Tool execution error: {str(e)}"

                if BASE_URL and "googleapis" in BASE_URL:
                    self.memory[session_id].append(
                        {
                            "role": "user",
                            "content": str(
                                {"name": tool_call.function.name, "response": tool_output}
                            ),
                        }
                    )
                else:
                    self.memory[session_id].append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_output),
                        }
                    )

            response = generate(messages=self.memory[session_id], tools=self.tools)

        self.memory[session_id].append({"role": "assistant", "content": response.message.content})

        if response.message.content:
            yield json.dumps({"session_id": session_id, "content": response.message.content}) + "\n"

    def _format_assistant_response(self, message: any):
        """Formats the ChatCompletionMessage to be returned to a model along with the tool call results"""
        return [
            {
                "id": tool_call.id,
                "name": tool_call.function.name,
                "args": tool_call.function.arguments,
            }
            for tool_call in message.tool_calls
        ]

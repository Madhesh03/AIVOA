import json
import re
from typing import Any, AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.groq_client import get_groq_client
from app.ai.tools import ToolExecutor


class AgentExecutor:
    def __init__(self, session: AsyncSession, user_id: str):
        self.session = session
        self.user_id = user_id
        self.llm = get_groq_client()
        self.executor = ToolExecutor(session, user_id)
        self.conversation_history: list[BaseMessage] = []
        self.last_interaction_id: str | None = None  # Track last created/referenced interaction

    def _get_tool_definitions(self) -> str:
        last_id_note = f"CURRENT CONTEXT: The last interaction ID from this session is: {self.last_interaction_id}" if self.last_interaction_id else "NOTE: Track the interaction_id returned from log_interaction and use it in follow-up edits"

        tools_def = f"""Available tools:

1. log_interaction(hcp_name: str, interaction_type: str, channel: str, subject: str,
   interaction_date: Optional[str] = None, notes: Optional[str] = None,
   sentiment: Optional[str] = None, products: Optional[list[str]] = None) -> dict
   - Log a new interaction. Types: meeting, call, email, conference, sample_drop
   - Channels: in_person, phone, video, email
   - Sentiments: positive, neutral, negative
   - Returns: success, interaction_id, form_prefill

2. edit_interaction(interaction_id: str, [fields to update]) -> dict
   - Edit an existing interaction by ID
   - IMPORTANT: Always provide the interaction_id explicitly
   - {last_id_note}

3. search_interactions(query: str, hcp_name: Optional[str] = None, limit: int = 5) -> dict
   - Search for interactions by keyword

4. summarize_interaction(interaction_id: str, summary: str) -> dict
   - Add AI summary to an interaction

5. suggest_followups(interaction_id: str, followup_actions: list[dict]) -> dict
   - Add follow-up actions to an interaction

IMPORTANT FORMAT:
- When logging: <tool_call>log_interaction(hcp_name="...", interaction_type="...", channel="...", subject="...")</tool_call>
- When editing: <tool_call>edit_interaction(interaction_id="UUID-HERE", sentiment="neutral")</tool_call>
- Always use the last created interaction_id when the user refers to "that interaction" or "the one we just logged"
"""
        return tools_def

    def _parse_tool_calls(self, content: str) -> list[dict[str, Any]]:
        tool_calls = []
        pattern = r'<tool_call>\s*(\w+)\((.*?)\)\s*</tool_call>'
        matches = re.findall(pattern, content, re.DOTALL)

        for tool_name, args_str in matches:
            try:
                args_dict: dict[str, Any] = {}
                arg_pattern = r'(\w+)=(["\']?)(.+?)\2(?:,|$)'
                arg_matches = re.findall(arg_pattern, args_str)

                for arg_name, quote, arg_value in arg_matches:
                    if arg_value.lower() == "true":
                        args_dict[arg_name] = True
                    elif arg_value.lower() == "false":
                        args_dict[arg_name] = False
                    elif arg_value.isdigit():
                        args_dict[arg_name] = int(arg_value)
                    else:
                        args_dict[arg_name] = arg_value.strip('"\'')

                tool_calls.append({"tool": tool_name, "args": args_dict})
            except Exception:
                pass

        return tool_calls

    async def _execute_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        try:
            if tool_name == "log_interaction":
                return await self.executor.log_interaction(**args)
            elif tool_name == "edit_interaction":
                return await self.executor.edit_interaction(**args)
            elif tool_name == "search_interactions":
                return await self.executor.search_interactions(**args)
            elif tool_name == "summarize_interaction":
                return await self.executor.summarize_interaction(**args)
            elif tool_name == "suggest_followups":
                return await self.executor.suggest_followups(**args)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_message(
        self, user_message: str
    ) -> AsyncIterator[dict[str, Any]]:
        self.conversation_history.append(HumanMessage(content=user_message))

        system_prompt = f"""You are an AI assistant for a healthcare professional (HCP) CRM system.
Help users log, edit, search, and manage HCP interactions naturally.

{self._get_tool_definitions()}

IMPORTANT INSTRUCTIONS:
1. When a user describes an HCP interaction (e.g., "Met Dr. X about topic"), ALWAYS call log_interaction immediately
2. Extract these required fields from the description:
   - hcp_name: The doctor/healthcare professional's name
   - interaction_type: meeting, call, email, conference, or sample_drop (best guess from context)
   - channel: in_person, phone, video, or email (best guess from context)
   - subject: Brief title of the interaction
3. ALWAYS extract and include sentiment based on tone/context:
   - "positive": if user mentions good feedback, enthusiasm, positive tone, "very positive", etc.
   - "negative": if user mentions concerns, complaints, negative tone, etc.
   - "neutral": if neither positive nor negative, or unclear
4. Include other optional fields if mentioned: interaction_date, notes, products
5. Use your best judgment to infer missing fields based on context
6. If a user asks to search, use search_interactions
7. After any tool execution, provide a brief friendly summary

SENTIMENT EXTRACTION EXAMPLES:
- "very positive" → sentiment="positive"
- "she was enthusiastic" → sentiment="positive"
- "concern about pricing" → sentiment="negative"
- "routine follow-up" → sentiment="neutral"
- "She was very positive and asked for samples" → sentiment="positive"

Always try to call a tool when the user provides enough information. Don't ask for clarification—make reasonable inferences."""

        messages = [
            {"role": "system", "content": system_prompt},
        ] + [
            {
                "role": ("user" if isinstance(msg, HumanMessage) else "assistant"),
                "content": msg.content,
            }
            for msg in self.conversation_history
        ]

        try:
            response = await self.llm.ainvoke(messages)
            ai_message_content = response.content

            tool_calls = self._parse_tool_calls(ai_message_content)

            # Strip the machine-readable <tool_call> blocks from the text shown
            # to the user; keep the raw content for conversation history.
            display_content = re.sub(
                r"<tool_call>.*?</tool_call>", "", ai_message_content, flags=re.DOTALL
            ).strip()
            if not display_content:
                display_content = (
                    "Done — I've updated the form on the left. Review and confirm to log."
                    if tool_calls
                    else ""
                )

            yield {
                "type": "token",
                "data": {"content": display_content},
            }

            if tool_calls:
                tool_results = []
                for tool_call in tool_calls:
                    yield {
                        "type": "tool_start",
                        "data": {
                            "tool": tool_call["tool"],
                            "input": tool_call["args"],
                        },
                    }

                    result = await self._execute_tool(tool_call["tool"], tool_call["args"])

                    # Track last interaction ID for follow-up edits
                    if result.get("success") and result.get("interaction_id"):
                        self.last_interaction_id = result["interaction_id"]

                    yield {
                        "type": "tool_result",
                        "data": {
                            "tool": tool_call["tool"],
                            "success": result.get("success", False),
                            "result": result,
                            "form_prefill": result.get("form_prefill"),
                            "interaction_id": result.get("interaction_id"),
                        },
                    }

                    tool_results.append(
                        ToolMessage(
                            tool_call_id=tool_call["tool"],
                            content=json.dumps(result),
                        )
                    )

                self.conversation_history.append(AIMessage(content=ai_message_content))
                for tool_result in tool_results:
                    self.conversation_history.append(tool_result)
            else:
                self.conversation_history.append(AIMessage(content=ai_message_content))

            yield {"type": "done", "data": {"status": "complete"}}

        except Exception as e:
            yield {
                "type": "error",
                "data": {"error": str(e)},
            }
            self.conversation_history.append(
                AIMessage(content=f"Error: {str(e)}")
            )


def create_agent_executor(
    session: AsyncSession, user_id: str
) -> AgentExecutor:
    return AgentExecutor(session, user_id)

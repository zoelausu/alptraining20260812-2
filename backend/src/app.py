"""Agno AgentOS + AGUI backend — Vercel AI Gateway via OpenAILike."""

import json
import logging
import os
from typing import Any

from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("agent_chat.agui")
logging.basicConfig(level=logging.INFO, format="%(message)s")


def _gateway_model() -> OpenAILike:
    return OpenAILike(
        id=os.environ.get("AI_GATEWAY_MODEL_ID", "google/gemini-3.5-flash-lite"),
        api_key=os.environ.get("AI_GATEWAY_API_KEY", ""),
        base_url=os.environ.get(
            "AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1"
        ),
    )


chat_agent = Agent(
    model=_gateway_model(),
    instructions="Respond in the same language the user uses.",
)

agent_os = AgentOS(
    agents=[chat_agent],
    interfaces=[AGUI(agent=chat_agent)],
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
)

app = agent_os.get_app()


class AguiStructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Emit structured JSON logs for AG-UI runs (Constitution VI)."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if request.method == "POST" and request.url.path.endswith("/agui"):
            body = await request.body()
            thread_id = None
            run_id = None
            if body:
                try:
                    payload = json.loads(body)
                    thread_id = payload.get("threadId")
                    run_id = payload.get("runId")
                except json.JSONDecodeError:
                    pass

            async def receive() -> dict[str, Any]:
                return {"type": "http.request", "body": body, "more_body": False}

            request = Request(request.scope, receive)

            logger.info(
                json.dumps(
                    {
                        "event": "agui_run_start",
                        "thread_id": thread_id,
                        "run_id": run_id,
                        "path": request.url.path,
                    }
                )
            )

        response = await call_next(request)
        return response


app.add_middleware(AguiStructuredLoggingMiddleware)


if __name__ == "__main__":
    port = int(os.environ.get("AGENT_OS_PORT", "7777"))
    agent_os.serve(app="app:app", reload=True, port=port)

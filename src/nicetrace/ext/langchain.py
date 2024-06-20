# from ..tracing import with_trace
from typing import Any, Optional
from ..tracing import start_trace_block, end_trace_block

#
# def wrap_openai(client):
#     client.chat.completions.create = with_trace(client.chat.completions.create, name="OpenAI chat query")
#     client.completions.create = with_trace(client.completions.create, name="OpenAI query")

try:
    from langchain_core.callbacks.base import BaseCallbackHandler

    class Tracer(BaseCallbackHandler):
        def __init__(self):
            self.running_nodes = {}

        def on_llm_start(
            self,
            serialized: dict[str, Any],
            prompts: list[str],
            *,
            run_id,
            parent_run_id=None,
            tags=None,
            metadata: Optional[dict[str, Any]] = None,
            **kwargs: Any,
        ) -> Any:
            kwargs = serialized["kwargs"]
            inputs = {}
            if len(prompts) == 1:
                inputs["prompt"] = prompts[0]
            else:
                inputs["prompts"] = prompts
            inputs["config"] = (
                metadata  # {"name": serialized["name"], "model_name": kwargs["model_name"], "temperature": kwargs["temperature"]}
            )
            pair = start_trace_block(
                f"Query {kwargs['model_name']}", kind="query", inputs=inputs
            )
            self.running_nodes[run_id] = pair

        def on_llm_end(
            self,
            response,
            *,
            run_id,
            parent_run_id=None,
            tags: Optional[list[str]] = None,
            **kwargs: Any,
        ) -> None:
            node, token = self.running_nodes.pop(run_id)
            generations = [g.text for gg in response.generations for g in gg]
            if len(generations) == 1:
                node.set_output(generations[0])
            else:
                node.set_output(generations)
            end_trace_block(node, token, None)

        def on_llm_error(
            self,
            error: BaseException,
            *,
            run_id,
            parent_run_id=None,
            tags: Optional[list[str]] = None,
            **kwargs: Any,
        ) -> None:
            node, token = self.running_nodes.pop(run_id)
            end_trace_block(node, token, None)
except ImportError:
    # Langchain not installed
    pass

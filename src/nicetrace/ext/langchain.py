# from ..tracing import with_trace
from typing import Any, Optional
from ..tracing import start_trace_block, end_trace_block, Metadata

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
            inputs = {}
            if len(prompts) == 1:
                inputs["prompt"] = prompts[0]
            else:
                inputs["prompts"] = prompts

            if "kwargs" in serialized and "model_name" in serialized["kwargs"]:
                model_name = serialized["kwargs"]["model_name"]
            else:
                model_name = metadata.get("ls_model_name")
            inputs["serialized"] = serialized
            inputs["metadata"] = metadata
            pair = start_trace_block(
                f"Query {model_name}",
                kind="query",
                inputs=inputs,
                meta=Metadata(icon="query"),
            )
            self.running_nodes[run_id.hex] = pair

        def on_llm_end(
            self,
            response,
            *,
            run_id,
            parent_run_id=None,
            tags: Optional[list[str]] = None,
            **kwargs: Any,
        ) -> None:
            node, token = self.running_nodes.pop(run_id.hex)
            generations = [g.text for gg in response.generations for g in gg]
            if len(generations) == 1:
                node.add_output("", generations[0])
            else:
                node.add_output("", generations)

            if response.llm_output is not None:
                if "token_usage" in response.llm_output:
                    usage = response.llm_output["token_usage"]
                    node.meta.counters = {
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                    }
                elif "usage" in response.llm_output:
                    usage = response.llm_output["usage"]
                    node.meta.counters = {
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                    }
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
            node, token = self.running_nodes.pop(run_id.hex)
            end_trace_block(node, token, None)

except ImportError:
    # Langchain not installed
    pass

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable


from app.config.settings import settings
logger = settings.get_logger()
load_dotenv()


def _as_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def extract_usage(response):
    """Normalize token usage returned by LangChain/OpenRouter."""
    usage = getattr(response, "usage_metadata", None) or {}
    metadata = getattr(response, "response_metadata", None) or {}
    token_usage = metadata.get("token_usage") or metadata.get("usage") or {}

    input_tokens = _as_int(
        usage.get("input_tokens")
        or token_usage.get("prompt_tokens")
        or token_usage.get("input_tokens")
    )
    output_tokens = _as_int(
        usage.get("output_tokens")
        or token_usage.get("completion_tokens")
        or token_usage.get("output_tokens")
    )
    total_tokens = _as_int(
        usage.get("total_tokens")
        or token_usage.get("total_tokens")
        or (input_tokens + output_tokens)
    )

    # Prefer a provider-reported cost if OpenRouter returns one.
    provider_cost = token_usage.get("cost", metadata.get("cost"))
    if provider_cost is None:
        provider_cost = metadata.get("usage", {}).get("cost") if isinstance(
            metadata.get("usage"), dict
        ) else None

    # Otherwise estimate using explicit per-million-token rates.
    input_rate = float(__import__("os").getenv("INPUT_COST_PER_1M_TOKENS", "0"))
    output_rate = float(__import__("os").getenv("OUTPUT_COST_PER_1M_TOKENS", "0"))
    input_cost = input_tokens * input_rate / 1_000_000
    output_cost = output_tokens * output_rate / 1_000_000
    estimated_cost = input_cost + output_cost

    if provider_cost is not None:
        try:
            total_cost = float(provider_cost)
            cost_source = "provider_reported"
            # The split is unknown unless the provider supplies it separately.
            input_cost = float(token_usage.get("input_cost", input_cost) or input_cost)
            output_cost = float(token_usage.get("output_cost", output_cost) or output_cost)
        except (TypeError, ValueError):
            total_cost = estimated_cost
            cost_source = "configured_rate_estimate"
    else:
        total_cost = estimated_cost
        cost_source = "configured_rate_estimate"

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens or input_tokens + output_tokens,
        "input_cost_usd": input_cost,
        "output_cost_usd": output_cost,
        "total_cost_usd": total_cost,
        "cost_source": cost_source,
        "model": metadata.get("model_name") or metadata.get("model") or "",
        "provider": "openrouter",
    }


class HealthcareAgent:
    def __init__(self):
        logger.info("Initializing Healthcare LangChain Agent...")
        self.llm = settings.get_model_client()
        self.output_parser = StrOutputParser()
        self.last_usage = {}
        logger.success("Healthcare LangChain Agent Initialized")

    @traceable(
        name="healthcare_faq_agent",
        run_type="chain",
        tags=["healthcare", "faq", "openrouter"],
        metadata={"component": "HealthcareAgent"},
    )
    async def ask(self, prompt: str) -> str:
        """LangSmith records prompt/output; usage is captured at the LLM call."""
        logger.info("Invoking Healthcare LLM...")
        response = await self.llm.ainvoke(prompt)
        self.last_usage = extract_usage(response)
        answer = self.output_parser.invoke(response)
        logger.info(
            "LLM usage: input_tokens={} output_tokens={} total_tokens={} "
            "input_cost_usd={} output_cost_usd={} total_cost_usd={} source={}",
            self.last_usage["input_tokens"],
            self.last_usage["output_tokens"],
            self.last_usage["total_tokens"],
            self.last_usage["input_cost_usd"],
            self.last_usage["output_cost_usd"],
            self.last_usage["total_cost_usd"],
            self.last_usage["cost_source"],
        )
        return answer


healthcare_agent = HealthcareAgent()

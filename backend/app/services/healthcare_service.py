from app.config.settings import settings
logger = settings.get_logger()

from app.implementations.healthcare_impl import HealthcareImplementation
import mlflow
from datetime import datetime
import time

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Healthcare_FAQ_ChatBot_Interface")


class HealthcareService:
    def __init__(self):
        logger.info("Initializing Healthcare Service")
        self.healthcare_impl = HealthcareImplementation()
        logger.success("Healthcare Service Initialized")

    async def ask_question(self, question: str, session_id: str) -> dict:
        if not question:
            raise ValueError("Question cannot be empty")
        if not session_id:
            raise ValueError("Session ID cannot be empty")

        start_time = datetime.now()
        start_ts = time.perf_counter()
        run_name = f"Healthcare_FAQ_{start_time.strftime('%Y%m%d_%H%M%S')}"

        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("start_time", start_time.strftime("%Y-%m-%d %H:%M:%S"))
            mlflow.log_param("session_id", session_id)
            mlflow.log_param("input_text", question)
            mlflow.set_tag("source", "FastAPI")
            mlflow.set_tag("endpoint", "healthcare/faq")
            mlflow.set_tag("framework", "LangChain")
            mlflow.set_tag("provider", "OpenRouter")
            mlflow.set_tag("langsmith_project", __import__("os").getenv(
                "LANGCHAIN_PROJECT", "healthcare-faq-chatbot"
            ))

            response = await self.healthcare_impl.process_question(
                question=question, session_id=session_id
            )
            mlflow.log_param("output", response)

            # Persist full answer as an artifact instead of an oversized MLflow param.
            mlflow.log_text(str(response.get("answer", "")), "llm_output.txt")
            usage = response.get("metadata", {}).get("llm_usage", {})
            for metric in (
                "input_tokens", "output_tokens", "total_tokens",
                "input_cost_usd", "output_cost_usd", "total_cost_usd",
            ):
                mlflow.log_metric(metric, float(usage.get(metric, 0) or 0))
            mlflow.set_tag("cost_source", str(usage.get("cost_source", "unknown")))
            mlflow.set_tag("model", str(usage.get("model") or "configured-model"))

            elapsed = time.perf_counter() - start_ts
            mlflow.log_metric("execution_time_seconds", round(elapsed, 4))
            mlflow.log_param("end_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        logger.success(f"Request Completed Successfully | Session={session_id}")
        return response

# Healthcare FAQ Chatbot

A FastAPI-based Healthcare FAQ Chatbot that uses an OpenAI-compatible LLM endpoint through LangChain, in-memory conversation state, MLflow request tracking, and Loguru-based application logging.

> **Important:** This README reflects the implementation found in the supplied ZIP archive. A few components are present in the project but are not currently wired into the runtime flow; these are documented explicitly below.

---

## 1. Overview

The application exposes a REST API for answering general healthcare questions.

At a high level, the request flow is:

```text
Client
  |
  v
FastAPI
  |
  v
Healthcare Router
  |
  v
Healthcare Service
  |
  +---- MLflow Tracking
  |
  v
Healthcare Implementation
  |
  +---- Chat Memory
  |
  v
Healthcare Agent
  |
  v
LangChain ChatOpenAI
  |
  v
OpenAI-compatible / OpenRouter LLM
```

The application is intended for **general healthcare information and FAQ-style assistance**, not diagnosis or treatment.

---

## 2. Key Features

- FastAPI REST API
- Healthcare FAQ endpoint
- LangChain-based LLM integration
- OpenAI-compatible model configuration
- OpenRouter-compatible configuration through `base_url`
- Session-based in-memory chat history
- MLflow experiment tracking
- Loguru console and file logging
- Pydantic request/response models
- Healthcare safety-oriented prompt
- Follow-up question generation at the API response layer
- Modular Router → Service → Implementation → Agent architecture
- Environment-variable-based LLM configuration

---

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application language |
| FastAPI | REST API framework |
| Pydantic | Request/response validation |
| LangChain | LLM integration |
| `langchain-openai` | `ChatOpenAI` integration |
| OpenAI-compatible API | LLM provider interface |
| OpenRouter | Supported through configurable `base_url` |
| MLflow | Experiment/request tracking |
| Loguru | Application logging |
| python-dotenv | Environment variable loading |
| Uvicorn | ASGI application server |

---

## 4. Project Structure

```text
app/
├── agents/
│   └── healthcare_agent.py
│
├── config/
│   └── llm_config.py
│
├── implementations/
│   └── healthcare_impl.py
│
├── memory/
│   └── chat_memory.py
│
├── models/
│   ├── request_model.py
│   └── response_model.py
│
├── prompts/
│   └── healthcare_prompt.py
│
├── routers/
│   └── healthcare_router.py
│
├── services/
│   └── healthcare_service.py
│
├── utils/
│   └── logger.py
│
└── main.py
```

The ZIP also contains Python `__pycache__` directories and compiled `.pyc` files. These are runtime artifacts and normally should not be committed to source control.

---

# 5. Architecture

## 5.1 Router Layer

File:

```text
app/routers/healthcare_router.py
```

Responsibilities:

- Define the HTTP endpoint.
- Receive and validate the `FAQRequest`.
- Call `HealthcareService`.
- Convert service output into `FAQResponse`.
- Translate validation errors into HTTP 400.
- Translate unexpected errors into HTTP 500.

Endpoint:

```http
POST /api/v1/faq
```

---

## 5.2 Service Layer

File:

```text
app/services/healthcare_service.py
```

Responsibilities:

- Perform basic validation.
- Start MLflow tracking.
- Capture request execution time.
- Call the implementation layer.
- Log request/response information to MLflow.
- Return the generated response.

MLflow experiment:

```text
Healthcare_FAQ_ChatBot_Interface
```

Tracking URI:

```text
http://localhost:5000
```

---

## 5.3 Implementation Layer

File:

```text
app/implementations/healthcare_impl.py
```

Responsibilities:

- Retrieve session conversation history.
- Store the user question.
- Invoke the Healthcare Agent.
- Store the generated assistant response.
- Build the application-level response dictionary.

Current response dictionary:

```python
{
    "answer": answer,
    "follow_up_questions": [
        "Would you like more details?",
        "Do you have additional symptoms?"
    ],
    "confidence_score": 0.95,
    "metadata": {
        "session_id": session_id,
        "history_count": len(history) + 2
    }
}
```

---

## 5.4 Agent Layer

File:

```text
app/agents/healthcare_agent.py
```

The `HealthcareAgent`:

1. Initializes the configured LLM.
2. Creates a `StrOutputParser`.
3. Receives a prompt string.
4. Calls:

```python
await self.llm.ainvoke(prompt)
```

5. Converts the result into a string.
6. Returns the generated answer.

The current agent is therefore a relatively thin LLM wrapper rather than a multi-agent workflow.

---

## 5.5 LLM Configuration

File:

```text
app/config/llm_config.py
```

The LLM is created using:

```python
ChatOpenAI(
    model=os.getenv("model"),
    api_key=os.getenv("openrouter_api_key"),
    base_url=os.getenv("base_url")
)
```

The project therefore expects configuration through environment variables.

---

# 6. Environment Variables

Create a `.env` file in the project root.

Example:

```env
model=your-model-name
openrouter_api_key=your-api-key
base_url=https://openrouter.ai/api/v1
```

For production, do **not** commit `.env` or API keys to source control.

Recommended:

```text
.env
.env.*
!.env.example
```

Add secrets through the deployment platform's secret-management mechanism.

---

# 7. Installation

## 7.1 Prerequisites

Recommended environment:

- Python 3.10+
- pip
- Virtual environment
- MLflow server if MLflow tracking is required
- Access to an OpenAI-compatible LLM provider

---

## 7.2 Create Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 7.3 Install Dependencies

The supplied archive does not include a `requirements.txt`.

Install the major dependencies:

```bash
pip install fastapi uvicorn pydantic python-dotenv loguru mlflow langchain langchain-openai
```

For reproducible deployments, create and commit a pinned `requirements.txt`:

```bash
pip freeze > requirements.txt
```

It is preferable to curate and pin only the packages actually required by the application rather than committing every package from a development environment.

---

# 8. Running the Application

From the directory containing the `app` package:

```bash
uvicorn app.main:app --reload
```

Typical local URL:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Root endpoint:

```text
http://localhost:8000/
```

---

# 9. API

## 9.1 Health / Root Endpoint

### Request

```http
GET /
```

### Example Response

```json
{
  "application": "Healthcare FAQ Chatbot",
  "version": "1.0.0",
  "status": "running"
}
```

---

# 10. Healthcare FAQ API

## Endpoint

```http
POST /api/v1/faq
```

### Request Body

```json
{
  "question": "What are common symptoms of dehydration?",
  "session_id": "session-001",
  "user_id": "user-001",
  "language": "English",
  "conversation_id": "conversation-001"
}
```

### Request Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `question` | string | Yes | Healthcare question, 3–1000 characters |
| `session_id` | string | Yes | Conversation/session identifier |
| `user_id` | string | No | User identifier |
| `language` | string | No | Preferred response language |
| `conversation_id` | string | No | Conversation tracking identifier |

---

## 10.1 Example cURL

```bash
curl -X POST "http://localhost:8000/api/v1/faq" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are common symptoms of dehydration?",
    "session_id": "session-001",
    "language": "English"
  }'
```

---

# 11. Response Model

The declared response model is:

```python
class FAQResponse(BaseModel):
    status: str
    answer: str
    session_id: str
    follow_up_questions: Optional[List[str]] = None
    disclaimer: Optional[str] = ...
```

The implementation also attempts to return:

- `confidence_score`
- `metadata`

However, these fields are **not declared in `FAQResponse`**.

Therefore, the current API contract and implementation are inconsistent.

A recommended response model is:

```python
class FAQResponse(BaseModel):
    status: str
    answer: str
    session_id: str
    follow_up_questions: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    disclaimer: Optional[str] = None
    metadata: Optional[dict] = None
```

---

# 12. Conversation Memory

File:

```text
app/memory/chat_memory.py
```

The application currently uses:

```python
defaultdict(list)
```

as its memory store.

Conceptually:

```text
session_id
    |
    +-- user message
    +-- assistant message
    +-- user message
    +-- assistant message
```

Supported operations:

```python
add_user_message()
add_assistant_message()
get_history()
clear_history()
get_conversation_summary()
```

## Important Limitation

This is **process-local in-memory storage**.

Consequences:

- Data disappears when the application restarts.
- Multiple application instances do not share memory.
- It is not suitable for durable production conversation storage.
- Memory growth can become a resource concern.
- It does not provide database-level security, auditing, retention, or access control.

For production, consider PostgreSQL, Redis, or another managed persistence layer.

A production architecture could be:

```text
FastAPI
   |
Healthcare Service
   |
Conversation Repository
   |
   +---- PostgreSQL
   |
   +---- Redis (optional cache)
```

---

# 13. Healthcare Prompt

File:

```text
app/prompts/healthcare_prompt.py
```

The project defines a `HEALTHCARE_PROMPT_TEMPLATE` containing instructions to:

- Provide general healthcare information.
- Explain symptoms and possible causes.
- Provide disease overviews.
- Explain medications and common side effects.
- Ask follow-up questions.
- Encourage professional consultation.
- Avoid diagnosis.
- Avoid prescribing medication.
- Identify situations where emergency care may be required.
- Include a medical disclaimer.

## Important Implementation Gap

Although the prompt template is defined, the current implementation does **not actually use it** when invoking the agent.

Current flow:

```text
question
   |
   v
healthcare_agent.ask(question)
   |
   v
LLM
```

The intended flow appears to be:

```text
question
   |
   v
Healthcare Prompt Template
   |
   v
Formatted Healthcare Prompt
   |
   v
Healthcare Agent
   |
   v
LLM
```

This should be fixed before relying on the prompt's safety and response-format instructions.

---

# 14. MLflow Tracking

The service configures:

```text
Tracking URI:
http://localhost:5000
```

Experiment:

```text
Healthcare_FAQ_ChatBot_Interface
```

The application creates an MLflow run for each FAQ request.

Tracked information includes:

### Parameters

```text
start_time
input_text
response
end_time
```

### Tags

```text
source = FastAPI
endpoint = healthcare/faq
```

### Metrics

```text
execution_time_seconds
```

## MLflow Server

Start MLflow separately if required:

```bash
mlflow server --host 0.0.0.0 --port 5000
```

Then open:

```text
http://localhost:5000
```

## Production Consideration

The current implementation logs the complete question and response into MLflow.

For healthcare applications, this can create privacy and compliance concerns if users submit personally identifiable information or protected health information.

Recommended approach:

```text
Raw User Data
      |
      v
PHI/PII Detection
      |
      v
Redaction / Tokenization
      |
      v
MLflow
```

Avoid logging sensitive healthcare information unless there is a documented, authorized, compliant reason to do so.

---

# 15. Logging

File:

```text
app/utils/logger.py
```

The project uses Loguru.

Three logging destinations/configurations are defined:

### Console

```text
INFO+
```

### Application Log

```text
logs/healthcare.log
```

Properties include:

- 10 MB rotation
- 30-day retention
- ZIP compression
- Backtrace
- Diagnostic information

### Error Log

```text
logs/error.log
```

Properties include:

- ERROR+
- 5 MB rotation
- 60-day retention
- ZIP compression

The logger also uses asynchronous enqueueing for file logging.

---

# 16. End-to-End Request Flow

A typical request follows this sequence:

```text
POST /api/v1/faq
        |
        v
FAQRequest validation
        |
        v
Healthcare Router
        |
        v
HealthcareService.ask_question()
        |
        +----------------------+
        |                      |
        v                      v
    Validation             MLflow Run
        |
        v
HealthcareImplementation.process_question()
        |
        +--> get_history(session_id)
        |
        +--> add_user_message()
        |
        v
HealthcareAgent.ask()
        |
        v
ChatOpenAI
        |
        v
LLM Provider
        |
        v
Generated Answer
        |
        +--> add_assistant_message()
        |
        v
Response Dictionary
        |
        v
FAQResponse
        |
        v
HTTP Response
```

---

# 17. Error Handling

The router handles:

### Validation Errors

```text
HTTP 400
```

### Unexpected Application Errors

```text
HTTP 500
```

Errors are logged using Loguru.

The service and implementation layers re-raise exceptions after logging.

For production, consider introducing structured application exceptions, for example:

```text
HealthcareApplicationError
LLMProviderError
MemoryError
ValidationError
SafetyGuardrailError
ExternalServiceError
```

This allows the API layer to return more precise and controlled error responses.

---

# 18. Security Considerations

This application handles healthcare-related questions, so security should be treated as a first-class concern.

Recommended additions include:

- Authentication
- Authorization/RBAC
- Rate limiting
- Request size limits
- Input validation
- Prompt-injection protection
- PII/PHI detection
- Sensitive-data redaction
- Secure secrets management
- TLS/HTTPS
- Audit logging
- API key rotation
- Output safety validation
- LLM provider timeout/retry policies
- Request correlation IDs
- Data retention policies

Do not expose the application directly to the public internet without appropriate security controls.

---

# 19. Healthcare Safety

The application is designed as an FAQ/information assistant.

It should not be treated as a clinical decision-making system.

Recommended safety architecture:

```text
User Question
     |
     v
Input Safety Guardrail
     |
     v
PHI/PII Detection
     |
     v
Prompt Injection Detection
     |
     v
Healthcare Agent
     |
     v
LLM
     |
     v
Output Safety Guardrail
     |
     v
Emergency/Risk Detection
     |
     +---- High Risk ---> Human / Clinical Escalation
     |
     v
User Response
```

Potential high-risk categories should include:

- Chest pain
- Severe breathing difficulty
- Stroke symptoms
- Severe allergic reaction
- Loss of consciousness
- Severe bleeding
- Suicidal/self-harm content
- Other emergency symptoms

The assistant should provide appropriate emergency guidance rather than attempting diagnosis or treatment.

---

# 20. Current Implementation Gaps

The following issues were identified during analysis of the supplied source code.

## 20.1 AutoGen is not actually used

`app/main.py` describes the application as:

```text
Healthcare FAQ Assistant using AutoGen, LangChain and FastAPI
```

However, the source code contains no AutoGen workflow.

The implemented LLM path is primarily:

```text
FastAPI → Service → Implementation → HealthcareAgent → LangChain ChatOpenAI
```

The description should either be corrected or AutoGen should be introduced deliberately.

---

## 20.2 Healthcare prompt is defined but unused

`healthcare_prompt.py` creates a `PromptTemplate`, but `HealthcareImplementation` calls:

```python
healthcare_agent.ask(question)
```

rather than formatting and passing the healthcare prompt.

Recommended:

```python
formatted_prompt = healthcare_prompt.format(
    question=question
)

answer = await healthcare_agent.ask(
    formatted_prompt
)
```

---

## 20.3 Conversation history is retrieved but not supplied to the LLM

The implementation performs:

```python
history = chat_memory.get_history(session_id)
```

but then sends only:

```python
question
```

to the agent.

Therefore, the LLM does not actually receive previous conversation turns.

A better approach is to construct a conversation-aware prompt or use LangChain message history.

---

## 20.4 Response schema mismatch

The implementation produces:

```text
confidence_score
metadata
```

but `FAQResponse` does not define these fields.

The request/response contract should be synchronized.

---

## 20.5 Confidence score is hard-coded

The implementation returns:

```python
"confidence_score": 0.95
```

This is not an actual model-derived confidence measurement.

A language model's generated answer should not be represented as having a verified 95% confidence merely because a constant was assigned.

Better options:

- Remove the field.
- Use a separately validated confidence estimation mechanism.
- Return a qualitative uncertainty indicator.
- Use retrieval evidence scores when a RAG architecture is introduced.

---

## 20.6 Follow-up questions are hard-coded

Current values:

```text
Would you like more details?
Do you have additional symptoms?
```

These are not generated based on the question or answer.

A future implementation could generate structured follow-up questions using the LLM and validate them.

---

## 20.7 LLM configuration naming is non-standard

The environment variables are:

```text
model
openrouter_api_key
base_url
```

A more conventional naming scheme would be:

```text
LLM_MODEL
OPENROUTER_API_KEY
OPENAI_API_BASE
```

The exact naming is a design choice, but consistent uppercase environment-variable naming is easier to maintain.

---

## 20.8 No dependency lock file

The archive does not contain a dependency specification such as:

```text
requirements.txt
pyproject.toml
poetry.lock
uv.lock
```

A production deployment should use pinned dependencies.

---

## 20.9 No automated tests are included

The archive does not contain a visible test suite.

Recommended structure:

```text
tests/
├── test_healthcare_router.py
├── test_healthcare_service.py
├── test_healthcare_impl.py
├── test_healthcare_agent.py
├── test_memory.py
└── test_llm_config.py
```

---

## 20.10 No persistent memory

The current memory is process-local.

For production:

```text
PostgreSQL
```

could store durable conversations, while:

```text
Redis
```

could be used for short-lived/session caching.

---

# 21. Recommended Production Architecture

A stronger production architecture could evolve toward:

```text
                    ┌─────────────────────┐
                    │      Client/UI      │
                    └──────────┬──────────┘
                               |
                               v
                    ┌─────────────────────┐
                    │ API Gateway / WAF   │
                    └──────────┬──────────┘
                               |
                               v
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │ Authentication/RBAC │
                    └──────────┬──────────┘
                               |
                               v
                    ┌─────────────────────┐
                    │ Healthcare Service  │
                    └──────────┬──────────┘
                               |
             ┌─────────────────┼──────────────────┐
             |                 |                  |
             v                 v                  v
      ┌────────────┐   ┌──────────────┐   ┌──────────────┐
      │ Guardrails │   │ Conversation │   │ Observability│
      │ / Safety   │   │   Memory     │   │ / MLflow     │
      └─────┬──────┘   └──────┬───────┘   └──────────────┘
            |                 |
            v                 v
      ┌────────────┐   ┌──────────────┐
      │ Healthcare │   │ PostgreSQL /  │
      │   Agent    │   │    Redis      │
      └─────┬──────┘   └──────────────┘
            |
            v
      ┌────────────┐
      │ RAG / Tools│
      └─────┬──────┘
            |
            v
      ┌────────────┐
      │    LLM     │
      └────────────┘
```

---

# 22. Recommended Future Enhancements

## Phase 1 — Correctness

- Wire `healthcare_prompt` into the agent.
- Pass conversation history to the LLM.
- Synchronize Pydantic response models.
- Remove or redesign hard-coded confidence.
- Generate context-aware follow-up questions.
- Add automated tests.
- Add `requirements.txt` or `pyproject.toml`.

## Phase 2 — Production Memory

- Replace `ChatMemory` with PostgreSQL.
- Add Redis for session caching if required.
- Add conversation expiration/retention.
- Add conversation ownership and authorization.

## Phase 3 — Healthcare RAG

Introduce trusted healthcare knowledge sources:

```text
User Question
      |
      v
Query Understanding
      |
      v
Retriever
      |
      v
Medical Knowledge Base
      |
      v
Evidence
      |
      v
LLM
      |
      v
Grounded Answer + Citations
```

Potential sources should be authoritative and appropriately licensed.

## Phase 4 — Agentic Healthcare Workflow

Possible specialized components:

```text
                    Healthcare Orchestrator
                             |
       ┌─────────────┬───────┼────────┬─────────────┐
       |             |       |        |             |
       v             v       v        v             v
  Symptom Agent  Drug Agent  RAG   Safety Agent  Triage Agent
       |             |       |        |             |
       └─────────────┴───────┴────────┴─────────────┘
                             |
                             v
                       Final Response
```

For higher-risk clinical scenarios, introduce Human-in-the-Loop review rather than autonomous clinical decisions.

---

# 23. Observability Recommendations

The current application already has Loguru and MLflow.

A mature observability stack could add:

```text
Logs
  └── Loguru / JSON Logs

Metrics
  └── Prometheus

Tracing
  └── OpenTelemetry

LLM Observability
  └── MLflow / LangSmith / equivalent

Dashboards
  └── Grafana
```

Useful metrics include:

- Request count
- Error rate
- P50/P95/P99 latency
- LLM latency
- Token usage
- Estimated LLM cost
- Model/provider errors
- Safety-guardrail triggers
- RAG retrieval quality
- Human escalation rate
- Session length
- Response generation latency

Sensitive healthcare data should not be exposed in telemetry.

---

# 24. Suggested Git Repository Hygiene

Add a `.gitignore` similar to:

```gitignore
__pycache__/
*.py[cod]

.venv/
venv/

.env
.env.*
!.env.example

logs/
*.log

.mlflow/
mlruns/

.pytest_cache/
.coverage
htmlcov/

.idea/
.vscode/
```

Do not commit:

- API keys
- `.env`
- Patient/healthcare data
- Runtime logs containing sensitive information
- Python bytecode
- Local MLflow artifacts
- Temporary files

---

# 25. Suggested `.env.example`

```env
# LLM Configuration
model=your-model-name
openrouter_api_key=your-openrouter-api-key
base_url=https://openrouter.ai/api/v1

# Optional application configuration
APP_ENV=development

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
```

The actual API key should never be placed in this file.

---

# 26. Example Improved API Contract

A production-friendly response could look like:

```json
{
  "status": "success",
  "answer": "Dehydration can cause thirst, dry mouth, dark urine, fatigue, dizziness, and reduced urination.",
  "session_id": "session-001",
  "follow_up_questions": [
    "How long have these symptoms been present?",
    "Are you able to drink and keep fluids down?"
  ],
  "disclaimer": "This information is for educational purposes only and should not replace professional medical advice.",
  "metadata": {
    "request_id": "req-123",
    "model": "configured-model"
  }
}
```

For production, avoid presenting an unvalidated numeric confidence score.

---

# 27. Development Checklist

Before production deployment:

- [ ] Add dependency file
- [ ] Add `.env.example`
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Wire healthcare prompt into runtime
- [ ] Implement actual conversation-aware prompting
- [ ] Replace in-memory memory with persistent storage
- [ ] Remove hard-coded confidence score
- [ ] Improve follow-up question generation
- [ ] Add authentication
- [ ] Add authorization
- [ ] Add rate limiting
- [ ] Add PHI/PII protection
- [ ] Add prompt-injection protection
- [ ] Add output guardrails
- [ ] Add request correlation IDs
- [ ] Secure MLflow
- [ ] Redact sensitive MLflow data
- [ ] Configure production LLM timeouts/retries
- [ ] Add health/readiness endpoints
- [ ] Add structured JSON logging
- [ ] Add monitoring and alerting
- [ ] Containerize application
- [ ] Add CI/CD
- [ ] Conduct security and privacy review

---

# 28. Summary

The supplied project is a **modular FastAPI healthcare FAQ chatbot** with a clean basic separation between:

```text
Router
   ↓
Service
   ↓
Implementation
   ↓
Agent
   ↓
LLM
```

It also includes:

```text
Memory
MLflow
Loguru
Pydantic
Healthcare Prompt
```

The core application is functional in concept, but several components currently represent **partially implemented architecture rather than fully connected runtime behavior**.

The most important implementation corrections are:

1. Connect `healthcare_prompt` to the actual LLM call.
2. Pass conversation history to the LLM.
3. Align `FAQResponse` with the fields returned by the implementation.
4. Remove the hard-coded `0.95` confidence score or replace it with a defensible mechanism.
5. Replace process-local memory for production use.
6. Protect MLflow and logs from PHI/PII exposure.
7. Add automated tests and dependency management.
8. Correct the application description if AutoGen is not intended to be used.

With these changes, the project can evolve from a basic FAQ chatbot into a more robust **Healthcare RAG / Agentic AI Assistant** with persistent memory, safety guardrails, evidence grounding, observability, and human escalation.

# TicketIQ — Self-Optimizing Support Triage Agent

TicketIQ is a backend B2B SaaS support-ticket triage system that combines classical ML, sentiment analysis, RAG, LLM-based reasoning, workflow orchestration, and contextual bandit reinforcement learning.

The system receives a support ticket and automatically:

1. Classifies the ticket category.
2. Detects aspect-level sentiment.
3. Calculates urgency.
4. Retrieves relevant knowledge-base information.
5. Selects an LLM configuration using a contextual bandit.
6. Runs an agent that decides whether to answer, use a tool, or escalate.
7. Generates a final support response.
8. Persists workflow state and stage outputs.
9. Learns from binary user feedback.

---

## Architecture

```text
                         ┌──────────────────┐
                         │   POST /ticket   │
                         └────────┬─────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │  Ticket Persistence │
                        │      SQLite         │
                        └─────────┬──────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌──────────────┐           ┌──────────────┐
             │ Classifier   │           │  Sentiment   │
             │ TF-IDF +     │           │ Aspect +     │
             │ NumPy LR     │           │ VADER        │
             └──────┬───────┘           └──────┬───────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                         ┌─────────────────┐
                         │ Urgency Scoring │
                         └────────┬────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Contextual Bandit   │
                       │ Config A / Config B │
                       └─────────┬───────────┘
                                 │
                                 ▼
                         ┌─────────────────┐
                         │   RAG Retrieval │
                         │ SentenceTrans.  │
                         │ + FAISS         │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Support Agent   │
                         │ Reasoning Loop  │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
               Direct Answer   Tool Call    Human Escalation
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   LLM Response  │
                         │     Ollama      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Ticket Response │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ POST /feedback  │
                         │ RL Update       │
                         └─────────────────┘
````
<img width="951" height="476" alt="image" src="https://github.com/user-attachments/assets/8a85d051-4299-48dd-b995-5b80b706b38e" />

---

## Tech Stack

### Backend

* Python 3.11
* FastAPI
* Uvicorn
* Pydantic
* SQLite

### Machine Learning

* TF-IDF
* Custom Logistic Regression implemented with NumPy
* scikit-learn metrics for evaluation
* VADER sentiment analysis
* Rule-based aspect extraction

### RAG

* Sentence Transformers
* `all-MiniLM-L6-v2`
* FAISS
* Markdown knowledge-base documents

### LLM

* Ollama
* `llama3.1:8b`
* Provider abstraction for future API-based LLM providers

### Reinforcement Learning

* Contextual Bandit
* Epsilon-greedy action selection
* Actions:

  * `config_a`
  * `config_b`

### Workflow

* Custom DAG/workflow engine
* Python `asyncio`
* SQLite-based persistent stage state

### Development

* pytest
* pytest-cov
* Black
* Ruff
* pre-commit
* Docker
* GitHub Actions

---

# Project Structure

```text
ticketiq/
│
├── app/
│   ├── api/
│   │   ├── tickets.py
│   │   ├── feedback.py
│   │   └── status.py
│   │
│   ├── agent/
│   │   ├── agent.py
│   │   ├── tools.py
│   │   └── prompts.py
│   │
│   ├── llm/
│   │   ├── base.py
│   │   ├── ollama_provider.py
│   │   └── api_provider.py
│   │
│   ├── ml/
│   │   └── classifier.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   └── retriever.py
│   │
│   ├── rl/
│   │   └── bandit.py
│   │
│   ├── sentiment/
│   │   └── aspect_sentiment.py
│   │
│   ├── workflow/
│   │   ├── engine.py
│   │   ├── stage.py
│   │   └── pipeline.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── config.py
│   ├── storage.py
│   ├── urgency.py
│   └── main.py
│
├── data/
│   ├── generate_dataset.py
│   └── tickets.csv
│
├── knowledge_base/
│   ├── refunds.md
│   ├── billing.md
│   ├── account_access.md
│   ├── feature_requests.md
│   └── escalation.md
│
├── experiments/
│   └── rl_simulation.py
│
├── tests/
│   ├── test_agent.py
│   ├── test_bandit.py
│   ├── test_feedback.py
│   ├── test_llm.py
│   ├── test_prompts.py
│   ├── test_rag.py
│   ├── test_sentiment.py
│   ├── test_urgency.py
│   └── test_workflow.py
│
├── Dockerfile
├── requirements.txt
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```

---

# Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd ticketiq
```

## 2. Create a virtual environment

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

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Install Ollama

Install Ollama and pull the configured model:

```bash
ollama pull llama3.1:8b
```

Verify that Ollama is available:

```bash
ollama run llama3.1:8b
```

The application uses Ollama as the default LLM provider.

---

# Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## POST `/ticket`

Creates and processes a support ticket.

### Request

```json
{
  "subject": "Refund not received",
  "body": "I requested a refund but the money has not arrived yet.",
  "tier": "premium"
}
```
<img width="902" height="416" alt="image" src="https://github.com/user-attachments/assets/a9aba649-50ae-43a9-8647-c7a752cfd594" />

### Response

The response contains:

* transaction ID
* category
* aspect sentiment
* urgency
* retrieved knowledge-base snippets
* agent action
* tool calls
* reasoning trace
* final response
* selected pipeline configuration
* latency
---
<img width="878" height="404" alt="image" src="https://github.com/user-attachments/assets/06262101-6716-4a0d-a681-d9a62803928a" />

<img width="887" height="448" alt="image" src="https://github.com/user-attachments/assets/7060c811-3d19-462f-86e7-d3d7cf6a0c57" />

Example structure:

```json
{
  "category": "billing",
  "sentiment": {},
  "urgency": {},
  "retrieved_snippets": [],
  "action": "direct_answer",
  "tool_calls": [],
  "reasoning_trace": [],
  "final_response": "...",
  "pipeline_config": {
    "name": "config_a",
    "top_k": 3
  },
  "latency": 1.2
}
```

---

## POST `/feedback`

Updates the contextual bandit using binary feedback.

### Request

```json
{
  "transaction_id": "transaction-id",
  "feedback": 1
}
```
<img width="958" height="447" alt="image" src="https://github.com/user-attachments/assets/65777c68-9241-4d23-b811-dd303ec23002" />
<img width="922" height="472" alt="image" src="https://github.com/user-attachments/assets/d15c3d84-7d80-4968-92d7-317e69f6967c" />

Where:

```text
1 = positive feedback
0 = negative feedback
```

### Reward

The reward function is:

```text
reward = feedback × 10 - latency_seconds
```

The feedback directly updates the selected bandit action.

---

## GET `/ticket/{transaction_id}/status`

Returns persistent workflow state for the ticket.

Example stages include:

```text
classification
sentiment
urgency
bandit
rag
agent
response

```
<img width="940" height="390" alt="image" src="https://github.com/user-attachments/assets/3df0b10e-c152-4128-8c95-704e47bf4f16" />

<img width="904" height="473" alt="image" src="https://github.com/user-attachments/assets/90259d73-ce50-4497-a7e3-a0904428395d" />

Each stage maintains its status and output in SQLite.

---

# Machine Learning Classifier

TicketIQ classifies tickets into four categories:

```text
billing
technical
account
feature_request
```

The classifier uses:

```text
Ticket Text
     │
     ▼
TF-IDF
     │
     ▼
Custom Logistic Regression
     │
     ▼
Category
```

The Logistic Regression implementation is written manually using NumPy rather than calling `sklearn.model.fit()`.

The dataset contains 160 synthetic labeled tickets:

```text
40 billing
40 technical
40 account
40 feature_request
```

The evaluation uses a held-out test split and reports:

* Accuracy
* Precision
* Recall
* F1 score

### Important limitation

The synthetic dataset is intentionally small and highly separable, so its evaluation performance should not be interpreted as production performance.

A production system should be retrained and evaluated on historical, human-labeled support tickets.

---

# Aspect Sentiment

The sentiment pipeline combines:

1. Lightweight keyword-based aspect extraction.
2. VADER sentiment scoring.

Potential aspects include:

```text
billing
refund
payment
account
login
technical issue
feature
```

The output contains sentiment information for detected aspects.

---

# Urgency

Urgency combines:

* ticket category
* sentiment
* customer tier

The system produces:

```text
low
medium
high
critical
```

The urgency score is normalized to `[0, 1]`.

Higher negative sentiment, higher-priority categories, and higher customer tiers increase the urgency score.

---

# RAG Pipeline

TicketIQ uses a small Markdown knowledge base.

Documents include:

```text
refunds.md
billing.md
account_access.md
feature_requests.md
escalation.md
```

The retrieval pipeline is:

```text
Knowledge Base
      │
      ▼
Document chunks
      │
      ▼
Sentence Transformer
      │
      ▼
Embeddings
      │
      ▼
FAISS
      │
      ▼
Top-K relevant snippets
```

The embedding model is:

```text
all-MiniLM-L6-v2
```

The selected LLM configuration determines the retrieval depth.

---

# LLM Configurations

TicketIQ supports two distinct LLM strategies.

## Config A — Focused Support

Characteristics:

* concise response
* high relevance
* use retrieved knowledge
* avoid unsupported claims
* lower RAG top-K

```text
RAG top-K = 3
```

## Config B — Verified Support

Characteristics:

* verification-oriented reasoning
* checks whether account/order information is required
* stronger escalation guidance
* larger retrieval context

```text
RAG top-K = 5
```

Both configurations can use the same underlying Ollama model while using meaningfully different prompting and retrieval strategies.

---

# Agent

The support agent implements a lightweight reasoning loop.

Depending on the ticket, the agent can:

### 1. Directly answer

Used when the ticket can be resolved from the available knowledge.

### 2. Use a tool

Mock tools include:

```text
check_account_status
check_refund_eligibility
```

### 3. Escalate to a human

Critical or unsupported cases can be routed to human support.

The agent returns:

* action
* tool calls
* reasoning trace
* final response

The system avoids claiming that an external action was completed unless the corresponding tool confirms it.

---

# Contextual Bandit RL

TicketIQ uses an epsilon-greedy contextual bandit.

The state contains:

```text
category
urgency bucket
customer tier
```

Example:

```text
billing|medium|premium
```

Available actions:

```text
config_a
config_b
```

The bandit selects an action based on the current context and learned reward statistics.

### Feedback loop

```text
Ticket
   │
   ▼
Contextual Bandit
   │
   ▼
Configuration
   │
   ▼
LLM + RAG + Agent
   │
   ▼
Response
   │
   ▼
User Feedback
   │
   ▼
Reward
   │
   ▼
Bandit Update
```

The reward function is:

```text
reward = feedback × 10 - latency_seconds
```

This allows the system to trade off response quality feedback against latency.

---

# RL Distribution Shift Experiment

A simulation is provided in:

```text
experiments/rl_simulation.py
```

Run it with:

```bash
python -m experiments.rl_simulation
```

The experiment changes which configuration receives positive feedback during the simulation and demonstrates that the contextual bandit updates its action distribution after the environment changes.

---

# Workflow Engine

TicketIQ uses a custom lightweight DAG/workflow engine.

Stages maintain persistent state in SQLite.

Example:

```text
Classification ─────┐
                    │
Sentiment ──────────┤
                    ▼
                 Urgency
                    │
                    ▼
                  Bandit
                    │
                    ▼
                   RAG
                    │
                    ▼
                  Agent
                    │
                    ▼
                 Response
```

Classification and sentiment are independent upstream stages and can be executed through the workflow engine's parallel execution mechanism.

Each stage can have states such as:

```text
pending
running
completed
failed
```

Completed stages are persisted and can be reused without rerunning upstream work.

Failed stages can be rerun independently.

---

# Persistence

SQLite stores:

* tickets
* workflow stage states
* feedback
* ticket run information
* bandit state/action
* latency
* reward

The database file is intentionally excluded from Git.

---

# Testing

Run the complete test suite:

```bash
python -m pytest
```

Current test suite:

```text
21 passed
```

The tests cover:

* Agent behavior
* Contextual bandit
* Feedback endpoint
* LLM provider
* Prompt configurations
* RAG retrieval
* Sentiment
* Urgency
* Workflow dependencies and persistence

---

# Code Quality

Run Ruff:

```bash
python -m ruff check app tests experiments
```

Run Black:

```bash
python -m black app tests experiments
```

Run pre-commit:

```bash
pre-commit run --all-files
```

Pre-commit runs:

* Black
* Ruff

---

# Docker

Build the Docker image:

```bash
docker build -t ticketiq .
```

Run:

```bash
docker run -p 8000:8000 ticketiq
```

The API will be available at:

```text
http://localhost:8000
```

Note: Ollama is configured as the default local LLM provider and normally needs to be available separately when running the complete LLM pipeline.

---

# GitHub Actions

The repository includes:

```text
.github/workflows/ci.yml
```

The CI pipeline:

1. Checks out the repository.
2. Installs Python 3.11.
3. Installs dependencies.
4. Runs Ruff.
5. Runs pytest.

This provides automated linting and test validation on pushes and pull requests.

---

# Configuration

Configuration is centralized in:

```text
app/config.py
```

Important settings include:

```text
LLM_PROVIDER
OLLAMA_MODEL
DATABASE_PATH
EMBEDDING_MODEL
DEFAULT_TOP_K
MAX_TOP_K
EPSILON
REWARD_SCALE
```

Environment variables can be used to override configuration where supported.

---

# Design Decisions

## Why custom Logistic Regression?

The assignment requires implementing the training/inference mathematics rather than relying on `sklearn.model.fit()`.

Therefore, the classifier uses:

* TF-IDF feature extraction
* NumPy-based Logistic Regression
* sklearn only for evaluation metrics

## Why FAISS?

FAISS provides a simple and efficient vector similarity search implementation suitable for the small knowledge base used in this assignment.

## Why a contextual bandit?

The system does not need a long multi-step reward trajectory. The configuration decision can be evaluated directly from user feedback and latency, making a contextual bandit appropriate.

## Why SQLite?

SQLite provides persistent workflow and feedback state without requiring an external database service, keeping the assignment easy to run locally.

---

# Limitations and Production Improvements

This implementation is intentionally lightweight for the take-home assignment.

Potential production improvements include:

* Train the classifier on real historical support data.
* Add stronger aspect-level sentiment models.
* Use production customer/account tools instead of mock tools.
* Add authentication and authorization.
* Add structured observability and tracing.
* Use a production-grade database.
* Add distributed workers for high ticket volume.
* Add more robust LLM evaluation.
* Add human-reviewed feedback loops.
* Add stronger guardrails around LLM-generated responses.
* Improve concurrent execution of CPU-bound pipeline stages.
* Add more extensive API and end-to-end tests.

---

# Local Development Checklist

```bash
# Activate environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Run lint
python -m ruff check app tests experiments

# Run formatting
python -m black app tests experiments

# Run pre-commit
pre-commit run --all-files

# Start API
uvicorn app.main:app --reload
```

---

# Summary

TicketIQ demonstrates an end-to-end self-optimizing support triage pipeline combining:

```text
Classical ML
     +
Aspect Sentiment
     +
Urgency Scoring
     +
RAG
     +
LLM
     +
Agent
     +
Contextual Bandit RL
     +
Persistent DAG Workflow
     +
FastAPI
```

The system is designed to improve its LLM configuration selection over time using direct user feedback while maintaining persistent workflow state for every ticket.

```


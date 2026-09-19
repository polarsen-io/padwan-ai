# TypeSafe (JEV)

`TypeSafeClient` evaluates text or structured state against named Noul, Choice,
and Score questions using the [System One API](https://docs.typesafe.ai/sdk/python).
It has its own evaluation interface; use it directly rather than `LLMClient` or
`AgentSession`.

## Configuration

Set `TYPESAFE_API_KEY` in your environment or pass `api_key=` explicitly.
The client defaults to `model="jev-latest"`, `timeout=60`, and
`base_url="https://api.typesafe.ai/v1/"`. The client does not load `.env` itself.

Requests use niquests' built-in retry handling: up to two retries for connection
errors, timeouts, HTTP 408/429, and 5xx responses, respecting `Retry-After`.
Exhausted rate limits raise `TooManyRequestsError`; other provider errors raise
`LLMError` with `provider="typesafe"`.

## Evaluate several questions

```python
from padwan_llm import TypeSafeClient
from padwan_llm.typesafe import ChoiceQuestion, NoulQuestion, ScoreQuestion

async with TypeSafeClient() as client:
    response = await client.system_one(
        state={"ticket": "I was charged twice. Please fix this today."},
        questions={
            "billing": NoulQuestion(
                type="noul", instructions="Is this ticket about billing?"
            ),
            "tone": ChoiceQuestion(
                type="choice",
                instructions="What is the customer's tone?",
                criteria={"calm": None, "frustrated": None, "angry": None},
            ),
            "urgency": ScoreQuestion(
                type="score",
                instructions="How urgent is this ticket?",
                criteria=["can wait", "this week", "today"],
            ),
        },
    )

print(response["answers"])
print(response["model"], response["usage"])
```

Responses are typed dictionaries preserving the API's `model`, `answers`, and
`usage` fields. Noul answers contain a probability, Choice answers contain a
selected label and probabilities, and Score answers contain a score, legend,
and probabilities. Score legend and probability keys remain strings (`"0"`,
`"1"`, etc.). Usage exposes `input_tokens` and `output_tokens`.

`TypeSafeModel` and `TYPESAFE_MODELS` track the `jev-latest` and `jev-preview`
aliases. A pinned model ID is also accepted through the constructor or the
per-request `model=` argument. Responses identify the model that answered;
aliases can move between releases.

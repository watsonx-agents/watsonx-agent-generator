## `agent_creator/generator.py`
# -*- coding: utf-8 -*-
"""
agent_creator.generator
~~~~~~~~~~~~~~~~~~~~~~~

Rewrite an agent’s Python source for a new task using IBM Watsonx.ai.

Highlights
----------
* Reads env vars (WATSONX_APIKEY, WATSONX_URL, PROJECT_ID) from `.env`.
* Works with *all* known Watsonx SDK versions:
  - Uses `APIClient.foundation_model` when available.
  - Falls back to `ModelInference` when it is not.
* Handles both object- and string-style responses.
"""

import os
from dotenv import load_dotenv

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams


def _initialise_model(client: APIClient,
                      credentials: Credentials,
                      project_id: str,
                      model_id: str):
    """
    Return a model instance that exposes `.generate_text()` no matter which
    Watsonx-AI SDK build is installed.
    """
    try:
        # SDK ≥ 1.5.0
        return client.foundation_model(model_id)
    except AttributeError:
        # Older builds → fall back to ModelInference
        from ibm_watsonx_ai.foundation_models import ModelInference

        return ModelInference(
            model_id=model_id,
            credentials=credentials,
            project_id=project_id,
        )


def generate_agent(current_agent_code: str, task_description: str) -> str:
    """
    Return Python source so the agent can accomplish *task_description* while
    preserving the original structure.  Returns ``None`` on failure.
    """
    # ------------------------------------------------------------------ 1
    # Load credentials
    # ----------------------------------------------------------------------
    load_dotenv()

    api_key = os.getenv("WATSONX_APIKEY")
    url      = os.getenv("WATSONX_URL") or "https://us-south.ml.cloud.ibm.com"
    project  = os.getenv("PROJECT_ID")

    if not api_key:
        raise ValueError("WATSONX_APIKEY is missing or empty.")
    if not url:
        raise ValueError("WATSONX_URL is missing or empty.")
    if not project:
        raise ValueError("PROJECT_ID is missing or empty.")

    # ------------------------------------------------------------------ 2
    # Initialise client & model
    # ----------------------------------------------------------------------
    credentials = Credentials(url=url, api_key=api_key)
    client      = APIClient(credentials=credentials, project_id=project)

    model_id = "ibm/granite-13b-instruct-v2"
    model    = _initialise_model(client, credentials, project, model_id)

    # ------------------------------------------------------------------ 3
    # Build prompt
    # ----------------------------------------------------------------------
    prompt = f"""
You are an expert Python code generator specialising in *refactoring* existing
agent code-bases while keeping the public interface stable.

Current code
------------
```python
{current_agent_code}
```

New requirement
---------------
The agent must additionally be able to:

    “{task_description}”

Return **only** the complete, runnable Python source (no markdown fences,
no commentary).
"""

    # ------------------------------------------------------------------ 4
    # Generation parameters
    # ----------------------------------------------------------------------
    parameters = {
        GenParams.MAX_NEW_TOKENS: 1_024,
        GenParams.TEMPERATURE:    0.20,
        GenParams.DECODING_METHOD: "greedy",
    }

    # ------------------------------------------------------------------ 5
    # Call the model
    # ----------------------------------------------------------------------
    try:
        response = model.generate_text(prompt=prompt, params=parameters)

        # SDKs differ in return type
        if hasattr(response, "get_result"):
            return response.get_result()
        if isinstance(response, str):
            return response

        # Fallback – stringify any other object
        return str(response)

    except Exception as exc:  # pragma: no cover
        print(f"[generator] Error during code generation: {exc}")
        return None


# ---------------------------------------------------------------------- 6
# Quick CLI test
# --------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    TEST_FILE = "example_agent.py"
    if not os.path.exists(TEST_FILE):
        print(f"Place a sample agent in {TEST_FILE} for the smoke test.")
        exit(1)

    with open(TEST_FILE, "r", encoding="utf-8") as fh:
        original = fh.read()

    updated = generate_agent(original, "Say hello world")
    print(updated)

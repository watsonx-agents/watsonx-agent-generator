import os
from pathlib import Path
from dotenv import load_dotenv

# These imports assume you have a WatsonX.ai client library installed.
# You may need to adjust these imports based on your actual WatsonX.ai SDK.
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

def generate_agent(current_agent_code: str, task_description: str) -> str:
    """
    Generates updated Python code for the agent using WatsonX.ai,
    based on an existing code structure and a new task description.

    Args:
        current_agent_code (str): The current Python code of the agent.
        task_description (str): The new task description for the agent.

    Returns:
        str: The updated Python code for the agent.
    """
    # Load environment variables from .env
    load_dotenv()

    # Retrieve necessary credentials
    api_key = os.getenv("WATSONX_APIKEY")
    url = os.getenv("WATSONX_URL")
    project_id = os.getenv("PROJECT_ID")

    if not api_key:
        raise ValueError("WATSONX_APIKEY is missing or empty.")
    if not url:
        raise ValueError("WATSONX_URL is missing or empty.")
    if not project_id:
        raise ValueError("PROJECT_ID is missing or empty.")

    # Set up credentials and client
    credentials = Credentials(
        url=url,
        api_key=api_key
    )
    client = APIClient(credentials=credentials, project_id=project_id)

    model_id = "ibm/granite-13b-instruct-v2"

    # Construct prompt instructing the model to modify the code while keeping the original structure intact
    prompt = f"""You are an expert Python code generator specializing in updating agent LLM code.
You will be provided with the current Python code of an agent and a description of a new task it needs to perform.
Your goal is to modify the existing code to incorporate the new task while strictly maintaining the original structure and ensuring the code remains runnable.

Here is the current Python code of the agent:
{current_agent_code}

Based on this, please modify the code so that the agent can perform the following task:
"{task_description}"

Ensure that you:
- Do not drastically change the overall structure of the provided code.
- Maintain existing classes, functions, and import statements unless absolutely necessary.
- Integrate the new task within the existing framework.
Return the complete updated Python code as a single string.
"""

    # Define generation parameters
    parameters = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 1000,  # Adjust as needed
        GenParams.TEMPERATURE: 0.3,
    }

    model = ModelInference(
        model_id=model_id,
        credentials=credentials,
        project_id=project_id
    )

    try:
        response = model.generate_text(
            prompt=prompt,
            params=parameters
        )
        # Return the generated code from the response
        return response.get_result()
    except Exception as e:
        print(f"An error occurred during code generation: {e}")
        return None

if __name__ == "__main__":
    # For testing purposes, example usage:
    with open("example_agent.py", "r", encoding="utf-8") as f:
        current_code = f.read()
    new_task = "The agent should summarize and analyze user input, then respond with a concise summary."
    updated = generate_agent(current_code, new_task)
    print(updated)

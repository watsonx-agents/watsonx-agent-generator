import os
from pathlib import Path
from dotenv import load_dotenv

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# Load .env
load_dotenv()

# Load environment variables
api_key = os.getenv("WATSONX_APIKEY")
url = os.getenv("WATSONX_URL")
project_id = os.getenv("PROJECT_ID")

# Check required vars
if not api_key:
    raise ValueError("WATSONX_APIKEY is missing or empty.")
if not url:
    raise ValueError("WATSONX_URL is missing or empty.")
if not project_id:
    raise ValueError("PROJECT_ID is missing or empty.")

# Set up credentials
credentials = Credentials(
    url=url,
    api_key=api_key
)

# Optional: create and reuse client
client = APIClient(credentials=credentials, project_id=project_id)

# Set model and prompt
model_id = "ibm/granite-13b-instruct-v2"
prompt = "Write a short story about a robot who wants to be a painter."

# Define parameters using MetaNames
parameters = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 200,
}

# Initialize the inference model
model = ModelInference(
    model_id=model_id,
    credentials=credentials,
    project_id=project_id
)

# Run inference
response = model.generate_text(
    prompt=prompt,
    params=parameters
)

# Output
print("Model response:", response)

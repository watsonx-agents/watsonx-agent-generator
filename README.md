# WatsonX Agent Creator

The **WatsonX Agent Creator** project provides a simple and interactive way to generate agents on watsonx.ai on the fly.
It uses a wizard that collects user requirements and configures a new agent automatically based on a selected framework.
This tool supports multiple base frameworks and offers the option to customize the agent code using AI-powered logic.

## Supported Frameworks
When generating a new agent, you can choose from the following frameworks:

| # | Framework | Notes |
|---|-----------|-------|
| 1 | **watsonx sdk** | Adds `ibm-watsonx-ai` + Python < 3.13 constraint |
| 2 | **beeai** | Adds `beeai-framework` |
| 3 | **langraph** | Adds `langgraph` + `langchain-ibm` |
| 4 | **crewai** | Adds `crewai` starter code (soon) |
| 5 | **langflow** | Adds `langflow` playground |
| 6 | **no framework**| Uses the *base* template only |

Choosing a framework stores its extra requirements in
`assets/frameworks/<framework>/pyproject.fragment.toml`.

```bash
assets/frameworks//model
├── agent.py
└── init.py
```

If you select **no framework**, the wizard uses `assets/frameworks/base`.



## Agent Customization
After selecting a framework and setting up the base model files, the wizard offers an optional customization step.

* **YES** ⇒ you describe a new task → `agent_creator/generator.py` rewrites the original `agent.py` with help of Granite LLM → result saved as **`agent_custom.py`**.
* **NO** ⇒ the default `agent.py` remains unchanged.

## ▶ **NEW – Dependency & Lock-file Handling**

* Each generated agent is a standalone **Poetry** project (`pyproject.toml` + `poetry.lock`) under `app/`.
* The generator now builds the file in **PEP 621** format **and** keeps a legacy `[tool.poetry]` section for full compatibility.
* **Framework fragments** are merged automatically — caret (`^`) versions are converted to PEP 508 ranges for the `[project]` list but retained in the legacy table.
* The wizard calls `poetry lock`, guaranteeing a reproducible environment before you ever `cd` into the agent.



## Pipeline Overview

The complete pipeline of the agent-creation process works as follows:

1. **Framework Selection**
   - The system prompts you to choose a framework (or no framework) from a list of supported options.
   - Based on your selection, the corresponding model folder is created under `assets/frameworks`.

2. **Base Model Setup**
   - The default agent code is copied from `assets/model/agent.py` to the newly created framework folder.

3. **Agent Customization (Optional)**
   - You are asked if you wish to customize the agent.
   - If yes, the system loads the agent code, requests a new task description, and calls the generator in `agent_creator/generator.py` to produce a customized version.
   - The customized code is saved as **agent_custom.py**.

4. **Project Generation**
   - The remaining project components such as the Dockerfile, compose file, README, Git configuration, etc., are generated.

5. **Dependency Resolution & Lock-file creation** ▶ **NEW**

6. **Registration in `agents.json` / optional Git push**
   - A new repository is optionally created and pushed to the `watsonx-agents` GitHub organization.
   - The project’s metadata is updated in `agents.json`.


## Example of Usage

1. **Clone the Repository**

   ```bash
   git clone [https://github.com/watsonx-agents/watsonx-agent-generator](https://github.com/watsonx-agents/watsonx-agent-generator)
   ````

2.  **Create and Activate a Python Virtual Environment**

    ```bash
    cd watsonx-agent-generator
    source .venv/bin/activate
    ```

3.  **Create a New Agent**

    From the project’s main directory, run the following script:

    ```bash
    bash create_agent.sh
    ```

      - You will be prompted to select a framework.
      - Next, the system will set up the corresponding model files.
      - Optionally, you can choose to customize your agent by providing a new task description.
        If you do, an updated agent code will be generated in **agent\_custom.py**.

    A new repository will be created under the GitHub organization (with a name such as `agent_<agent_name>`),
    and the `agents.json` file will be updated with your new agent details.

▶ **NEW – Quick “inside the agent” tour**
After generation:

```bash
cd agents/<agent_name>/app
poetry install            # uses the freshly-baked lock file
poetry run uvicorn <agent_name>.main:app --reload
```

Visit http://localhost:\<agent\_port\>/docs to poke the FastAPI endpoint.
All environment variables live in the agent’s .env; secrets never leak into git.

## Example of a Generated Agent Structure

After generating a new agent, the directory structure might look like this:

```
.
├── Dockerfile
├── README.md
├── compose.yaml
├── .env      /.env.sample   # ▶ NEW
├── agent_custom.py          # Customized agent code (if customization was selected)
└── app
    ├── poetry.lock          # ▶ NEW
    ├── pyproject.toml
    └── <agent_name>         # Your agent's code folder (renamed from the temporary directory)
        ├── __init__.py
        ├── configs
        │   ├── __init__.py
        │   ├── constants.py
        │   ├── folders.py
        │   ├── logger.py
        │   └── settings.py
        ├── main.py
        └── model
            ├── __init__.py
            └── agent.py     # Base agent code copied from assets/model (unchanged if not customized)
└── agent_creator
    ├── generator.py         # Contains the AI-powered generate_agent() function
    └── ... (other scripts)
```

## Example Without a Framework

If you choose **no framework**, the project will create the `assets/frameworks/base/model` folder with the default agent code.
You can later update the **model/agent.py** file as needed for further customizations.

**model/agent.py Example:**

```python
"""
This file (agent.py) contains the main code for the agent.
All logic and functionalities of the agent should be defined here.
For modifications or enhancements, update this file.
This file serves as the single source of truth for agent behavior.

To create a new agent or add functionalities, update the code accordingly.
"""

def agent(question):
    """
    A simple agent function that takes a question as input
    and returns a default response.

    Parameters:
    - question (str): The question from the user.

    Returns:
    - str: A response indicating that the agent is under development.
    """
    response = "I am sorry, I am still in development 😥"
    return response
```

To test the agent without a framework:

1.  Navigate to the app folder:

    ```bash
    cd app
    ```

2.  Install the dependencies:

    ```bash
    poetry install
    ```

3.  Activate the poetry shell:

    ```bash
    poetry shell
    ```

4.  Run the agent's main script:

    ```bash
    poetry run python <agent_name>/main.py
    ```

    You can then access the API documentation and test endpoints via [http://localhost:2001/docs](http://localhost:2001/docs) (port 2001 is used as specified during setup).


▶ **NEW – Contributing / Extending**

### Add a new framework

1.  Create `assets/frameworks/<your_fw>/model/agent.py`
2.  Add `pyproject.fragment.toml` with any extra dependencies.
3.  Update `select_framework()` list in the generator script.

### Upgrade dependencies

Edit the fragment files or the generic bundle list in `agent_creator/main.py`; the generator will propagate the changes to every new agent.


## Summary

  - **Interactive Wizard:** Select a framework and optionally customize the agent task.
  - **AI-Powered Customization:** Use `agent_creator/generator.py` to generate an updated version of the agent code based on user-provided task descriptions.
  - **Automated Repository Management:** Optionally push the newly created agent to GitHub and update `agents.json`.
  - **Modular Design:** The agent’s core logic is encapsulated in the **model/agent.py** file (or **agent\_custom.py** if customized), so developers can easily update or extend the functionality.
  - **Automatic pyproject + lock-file with framework-specific deps.** ▲ **NEW**
  - **Modular assets:** edit a single file to support new frameworks. **NEW**
  - **One-command bootstrap:** `bash create_agent.sh`. **NEW**

Start creating and customizing your agents with the WatsonX Agents Hub, and empower your applications with dynamic, AI-powered agents\!


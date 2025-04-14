# {AGENT_NAME}

This is an agent created for the IBM CIC's Agents Orchestrator with WatsonX.

## Dependencies

### Windows
If you are using this agent under Windows, please install [WLS 2](https://learn.microsoft.com/en-us/windows/wsl/install):

#### 1. Enable WSL:
Open PowerShell as Administrator and run:
```bash
wsl --install
```

#### 2. Install Ubuntu 22.04:
1. Open the Microsoft Store, search for "Ubuntu 22.04," and click "Install."
2. Launch Ubuntu by typing `wsl` in the terminal.
3. Verify the Ubuntu version using the following command:
   ```bash
   lsb_release -a
   ```

## Podman

Since this project uses Podman, install it from [here](https://podman.io/docs/installation)

## Usage

To use the agent, execute the following steps:

1. Move into the agent path
```bash
cd {AGENT_PATH}
```

2. Adjust values in environment file
```bash
nano .env
```

3. Build the containers
```bash
podman-compose build
```

4. Start the containers
```bash
podman-compose up -d
```

5. Test connectivity
```bash
curl localhost:{HOST_PORT}/test
```

## Next steps

After creating the agent, you can start writing its logic and endpoints. 

## Documentation

- [Poetry](https://python-poetry.org/docs/)
- [Podman](https://docs.podman.io/en/latest/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/docs/tutorials/)
- [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

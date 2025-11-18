"""AI service for WatsonX integration.

This module provides AI-powered code generation capabilities using
IBM WatsonX Granite models.
"""

from typing import Any

from watsonx_agent_creator.core.config import get_settings
from watsonx_agent_creator.core.exceptions import AIServiceError, ConfigurationError
from watsonx_agent_creator.core.logging import get_logger
from watsonx_agent_creator.domain.models import AIModelConfig

logger = get_logger(__name__)


class AIService:
    """Service for AI-powered code generation using WatsonX.

    This service integrates with IBM WatsonX.ai to provide AI-powered
    agent code customization using Granite models.

    Attributes:
        settings: Application settings
        model_config: AI model configuration
        client: WatsonX model inference client
    """

    def __init__(self, model_config: AIModelConfig | None = None) -> None:
        """Initialize the AI service.

        Args:
            model_config: Optional model configuration (defaults to settings)

        Raises:
            ConfigurationError: If WatsonX credentials are missing

        Examples:
            >>> service = AIService()
            >>> code = await service.generate_agent_code("Create a chatbot agent")
        """
        self.settings = get_settings()

        if not self.settings.has_watsonx_config:
            raise ConfigurationError(
                "WatsonX configuration missing. Set WATSONX_APIKEY and PROJECT_ID environment variables.",
                {
                    "has_apikey": bool(self.settings.watsonx_apikey),
                    "has_project_id": bool(self.settings.watsonx_project_id),
                },
            )

        self.model_config = model_config or AIModelConfig()
        self.client: Any = None

        logger.info(f"AI service initialized with model: {self.model_config.model_id}")

    def _initialize_client(self) -> Any:
        """Initialize WatsonX model client.

        Returns:
            Initialized model client

        Raises:
            AIServiceError: If client initialization fails
        """
        try:
            # Import here to avoid dependency if AI features not used
            from ibm_watsonx_ai import APIClient, Credentials  # type: ignore[import-untyped]
            from ibm_watsonx_ai.foundation_models import ModelInference  # type: ignore[import-untyped]

            # Create credentials
            credentials = Credentials(
                url=self.settings.watsonx_url,
                api_key=self.settings.watsonx_apikey,
            )

            # Create API client
            api_client = APIClient(credentials)

            # Create model inference client
            model = ModelInference(
                model_id=self.model_config.model_id,
                api_client=api_client,
                project_id=self.settings.watsonx_project_id,
                params={
                    "max_new_tokens": self.model_config.max_new_tokens,
                    "temperature": self.model_config.temperature,
                    "top_p": self.model_config.top_p,
                    "top_k": self.model_config.top_k,
                    "repetition_penalty": self.model_config.repetition_penalty,
                },
            )

            logger.info("WatsonX client initialized successfully")
            return model

        except ImportError as e:
            logger.error("Failed to import WatsonX SDK", exc_info=True)
            raise AIServiceError(
                "WatsonX SDK not available. Install with: uv pip install ibm-watsonx-ai",
                {"error": str(e)},
            ) from e
        except Exception as e:
            logger.error("Failed to initialize WatsonX client", exc_info=True)
            raise AIServiceError(
                "Failed to initialize WatsonX client",
                {"error": str(e)},
            ) from e

    async def generate_agent_code(
        self,
        task_description: str,
        base_code: str | None = None,
        framework: str = "watsonx",
    ) -> str:
        """Generate or customize agent code using AI.

        Args:
            task_description: Natural language description of what the agent should do
            base_code: Optional base code to customize
            framework: Framework being used

        Returns:
            Generated or customized agent code

        Raises:
            AIServiceError: If code generation fails

        Examples:
            >>> service = AIService()
            >>> code = await service.generate_agent_code(
            ...     "Create a chatbot that answers questions about Python"
            ... )
        """
        if not self.client:
            self.client = self._initialize_client()

        # Build prompt
        prompt = self._build_prompt(task_description, base_code, framework)

        logger.info("Generating agent code with AI")
        logger.debug(f"Task: {task_description[:100]}...")

        try:
            # Generate code
            response = self.client.generate_text(prompt=prompt)

            if not response:
                raise AIServiceError("Empty response from AI model")

            # Extract code from response
            generated_code = self._extract_code(response)

            logger.info("Agent code generated successfully")
            logger.debug(f"Generated {len(generated_code)} characters of code")

            return generated_code

        except Exception as e:
            logger.error("AI code generation failed", exc_info=True)
            raise AIServiceError(
                "Failed to generate agent code",
                {"task": task_description[:100], "error": str(e)},
            ) from e

    def _build_prompt(
        self,
        task_description: str,
        base_code: str | None,
        framework: str,
    ) -> str:
        """Build prompt for AI code generation.

        Args:
            task_description: Task description
            base_code: Optional base code
            framework: Framework name

        Returns:
            Formatted prompt string
        """
        if base_code:
            prompt = f"""You are an expert Python developer specializing in AI agents.

Task: Modify the following agent code to accomplish this task: {task_description}

Framework: {framework}

Current Code:
```python
{base_code}
```

Instructions:
1. Modify the code to accomplish the specified task
2. Preserve the existing structure and imports
3. Add comprehensive docstrings and type hints
4. Follow PEP 8 style guidelines
5. Return ONLY the complete modified code, no explanations

Modified Code:
```python
"""
        else:
            prompt = f"""You are an expert Python developer specializing in AI agents.

Task: Create a new AI agent that accomplishes this task: {task_description}

Framework: {framework}

Instructions:
1. Create a complete, production-ready agent implementation
2. Include all necessary imports
3. Add comprehensive docstrings and type hints
4. Follow PEP 8 style guidelines
5. Include error handling
6. Return ONLY the complete code, no explanations

Agent Code:
```python
"""

        return prompt

    def _extract_code(self, response: str) -> str:
        """Extract Python code from AI response.

        Args:
            response: AI model response

        Returns:
            Extracted Python code
        """
        # Try to extract code from markdown code blocks
        if "```python" in response:
            start = response.find("```python") + len("```python")
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()

        elif "```" in response:
            start = response.find("```") + len("```")
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()

        # Return full response if no code blocks found
        return response.strip()

    async def validate_code(self, code: str) -> bool:
        """Validate generated code syntax.

        Args:
            code: Python code to validate

        Returns:
            True if code is valid, False otherwise
        """
        try:
            compile(code, "<string>", "exec")
            logger.debug("Code validation successful")
            return True
        except SyntaxError as e:
            logger.warning(f"Code validation failed: {e}")
            return False

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the configured model.

        Returns:
            Dictionary with model configuration details
        """
        return {
            "model_id": self.model_config.model_id,
            "max_new_tokens": self.model_config.max_new_tokens,
            "temperature": self.model_config.temperature,
            "top_p": self.model_config.top_p,
            "top_k": self.model_config.top_k,
            "repetition_penalty": self.model_config.repetition_penalty,
        }

import os

ANALYSIS_AGENT_ADDR = "analysis@fame.fabric"
SUMMARIZER_AGENT_ADDR = "summarizer@fame.fabric"
SENTIMENT_AGENT_ADDR = "sentiment@fame.fabric"


def get_openai_client():
    from openai import AsyncOpenAI

    openai_api_key = os.getenv("OPENAI_API_KEY")
    return AsyncOpenAI(api_key=openai_api_key)


def get_model_name():
    return os.getenv("MODEL_NAME") or "gpt-4.1-mini"

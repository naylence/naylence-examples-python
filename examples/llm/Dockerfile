FROM ghcr.io/naylence/agent-sdk-base:0.1.8

# Install additional packages required for LLM examples
RUN pip install --no-cache-dir \
    openai \
    python-dotenv \
    pillow \
    numpy \
    anthropic \
    tiktoken

WORKDIR /work

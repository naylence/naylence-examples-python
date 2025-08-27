import argparse
import asyncio
import base64
import os
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional

import openai
from naylence.fame.core import FameFabric
from naylence.fame.util import logging

from naylence.agent import Agent, BaseAgent

logging.enable_logging(log_level="warning")


logger = logging.getLogger(__name__)

# Load environment variables
default_output_dir = "generated_images"

IMAGE_MODEL = "dall-e-2"
PROMPT_ENHANCEMENT_MODEL = "gpt-4.1-mini"


class ImageGenerationAgent(BaseAgent):
    """
    An agent that generates images using OpenAI's DALL-E 2 model.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set it in .env file or pass it to the constructor."
            )
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

        self.image_generation_prompt = """
        You are a creative image generation assistant. Given a text prompt, 
        you will help create a detailed image generation prompt that will work well with DALL-E 2.
        Consider:
        1. Visual details and composition
        2. Style and artistic direction
        3. Lighting and atmosphere
        4. Color palette and mood
        
        Prompt size must NOT exceed 1000 chars.
        """

    async def run_task(self, payload: Any, id: Any) -> Any:
        user_prompt = payload["prompt"]
        image_size = payload.get("size", "512x512")
        fmt = payload.get("response_format", "b64_json")
        logger.info(f"Received task with prompt: {user_prompt}")

        enhanced_prompt = await self._enhance_prompt(user_prompt)
        return await self._generate_image(
            enhanced_prompt, size=image_size, response_format=fmt
        )

    async def _enhance_prompt(self, user_prompt: str) -> str:
        try:
            logger.info(f"Enhancing prompt: {user_prompt}")
            response = await self.client.chat.completions.create(
                model=PROMPT_ENHANCEMENT_MODEL,
                messages=[
                    {"role": "system", "content": self.image_generation_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            enhanced_prompt = response.choices[0].message.content
            assert enhanced_prompt
            logger.info(f"Enhanced prompt: {enhanced_prompt}")

            if len(enhanced_prompt) > 1000:
                logger.warning(
                    f"Enhanced prompt too long ({len(enhanced_prompt)} chars), truncating to 1000 chars"
                )
                enhanced_prompt = enhanced_prompt[:997] + "..."
            return enhanced_prompt

        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            return (
                (user_prompt[:997] + "...") if len(user_prompt) > 1000 else user_prompt
            )

    async def _generate_image(
        self,
        prompt: str,
        size: Literal["256x256", "512x512", "512x512"] = "512x512",
        response_format: Literal["url", "b64_json"] = "b64_json",
    ) -> Dict[str, Any]:
        try:
            logger.info(
                f"Generating image with size {size} and format {response_format}"
            )
            response = await self.client.images.generate(
                model=IMAGE_MODEL,
                prompt=prompt,
                n=1,
                response_format=response_format,
                size=size,  # type: ignore
            )
            assert response.data
            image_obj = response.data[0]
            if response_format == "url":
                # Use attribute access on Image object
                return {"url": image_obj.url, "prompt": prompt, "size": size}
            else:
                return {"b64_json": image_obj.b64_json, "prompt": prompt, "size": size}
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {"error": str(e), "status": "error"}


def save_image(result: Any, output_dir: Path) -> Path:
    prompt = result.get("prompt", "image")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = "".join(
        c for c in prompt[:30] if c.isalnum() or c in (" ", "-", "_")
    ).strip()

    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"{timestamp}_{safe_prompt}.png"

    img_bytes = base64.b64decode(result["b64_json"])
    with open(filepath, "wb") as f:
        f.write(img_bytes)
    return filepath


def is_running_in_docker() -> bool:
    """Check if we're running inside a Docker container."""
    return (
        Path("/.dockerenv").exists()
        or os.getenv("DISPLAY") == ""
        or os.getenv("DOCKER_CONTAINER") == "true"
    )


async def main(
    prompt: str, size: str, output_dir: Path, url_only: bool, no_browser: bool
):
    async with FameFabric.create() as fabric:
        agent_addr = await fabric.serve(ImageGenerationAgent())
        remote = Agent.remote_by_address(agent_addr)
        payload = {
            "prompt": prompt,
            "size": size,
            "response_format": "url" if url_only else "b64_json",
        }
        result: Any = await remote.run_task(payload=payload)

    # Check if we should skip browser opening
    skip_browser = no_browser or is_running_in_docker()

    if url_only and result.get("url"):
        url = result["url"]

        # Print prominent success message with URL
        print("\n🎨 Image generated successfully!")
        print(f"🔗 Image URL: {url}")
        print("⏰ Note: URL expires after 1 hour\n")

        logger.info(f"Image URL: {url}")

        if not skip_browser:
            logger.info("Opening URL in browser...")
            webbrowser.open(url)
        else:
            logger.info(
                "Browser opening disabled (running in Docker or --no-browser specified)"
            )
    elif result.get("b64_json"):
        filepath = save_image(result, output_dir)
        abs_path = filepath.resolve()

        # Print prominent success message with file location
        print("\n🎨 Image generated successfully!")
        print(f"📁 Saved to: {abs_path}")
        print(f"📂 Directory: {abs_path.parent}")
        print(f"📄 Filename: {abs_path.name}\n")

        logger.info(f"Image saved to: {abs_path}")

        if not skip_browser:
            logger.info("Opening image in browser...")
            webbrowser.open(abs_path.as_uri())
        else:
            logger.info(
                "Browser opening disabled (running in Docker or --no-browser specified)"
            )
    else:
        logger.error("No valid image data returned.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate an image using DALL-E 2 via Naylence ImageGenerationAgent"
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="Text prompt for image generation",
        default="A serene landscape with mountains and a flowing river at sunset",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=str,
        choices=["256x256", "512x512", "1024x1024"],
        help="Image size",
        default="512x512",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help="Directory to save generated images",
        default=default_output_dir,
    )
    parser.add_argument(
        "-u",
        "--url-only",
        action="store_true",
        help="Do not save locally; open the image URL returned by the API instead",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the generated image in a browser (useful for Docker/headless environments)",
    )
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    asyncio.run(
        main(
            prompt=args.prompt,
            size=args.size,
            output_dir=out_dir,
            url_only=args.url_only,
            no_browser=args.no_browser,
        )
    )

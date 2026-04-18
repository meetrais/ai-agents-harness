"""Basic SandboxAgent with Docker execution (Windows-compatible).

Requires:
  - pip install "openai-agents[docker]"
  - Docker Desktop running
  - OPENAI_API_KEY env var set
"""

import asyncio
import logging
from pathlib import Path

from docker import from_env as docker_from_env

from agents import ModelSettings, Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.entries import LocalDir
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions

from progress import Spinner

logging.basicConfig(level=logging.WARNING)

# Path to the external dataroom directory
DATAROOM = Path(__file__).resolve().parent.parent / "dataroom"


async def main() -> None:
    # Mount the dataroom directory into the container at "data/"
    manifest = Manifest(
        entries={"data": LocalDir(src=DATAROOM)},
    )

    agent = SandboxAgent(
        name="Dataroom Analyst",
        model="gpt-5.4",
        model_settings=ModelSettings(reasoning={"effort": "none"}),
        instructions="Answer using only files in data/. Cite source filenames.",
        default_manifest=manifest,
    )

    async with Spinner("Dataroom Analyst analyzing data"):
        result = await Runner.run(
            agent,
            "Compare FY2025 revenue, operating income, and operating cash flow with FY2024.",
            max_turns=10,
            run_config=RunConfig(
                sandbox=SandboxRunConfig(
                    client=DockerSandboxClient(docker_from_env()),
                    options=DockerSandboxClientOptions(image="python:3.14-slim"),
                ),
                workflow_name="Docker sandbox review",
            ),
        )

    print("\n" + "=" * 60)
    print("AGENT OUTPUT:")
    print("=" * 60)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
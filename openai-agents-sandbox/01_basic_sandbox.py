"""Basic SandboxAgent with Docker execution (Windows-compatible).

Requires:
  - pip install "openai-agents[docker]"
  - Docker Desktop running
  - OPENAI_API_KEY env var set
"""

import asyncio
import logging

from docker import from_env as docker_from_env

from agents import Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.entries import File
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions

logging.basicConfig(level=logging.WARNING)
logging.getLogger("openai.agents").setLevel(logging.DEBUG)


async def main() -> None:
    # Use File entries — these get staged directly into the container,
    # no volume mount needed (avoids Windows Docker path issues)
    manifest = Manifest(
        entries={
            "data/metrics.md": File(
                content=(
                    b"# Annual metrics\n\n"
                    b"| Year | Revenue | Operating income | Operating cash flow |\n"
                    b"| --- | ---: | ---: | ---: |\n"
                    b"| FY2025 | $124.3M | $18.6M | $24.1M |\n"
                    b"| FY2024 | $98.7M | $12.4M | $17.9M |\n"
                ),
            ),
        }
    )

    agent = SandboxAgent(
        name="Dataroom Analyst",
        model="gpt-5.4",
        instructions="Answer using only files in data/. Cite source filenames.",
        default_manifest=manifest,
    )

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
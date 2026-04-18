"""Full Capabilities -- Filesystem + Shell + Memory.

Shows how to explicitly compose capabilities. When a custom list is passed
it replaces the defaults (Filesystem, Shell, Compaction), so include
everything you need.

Memory uses progressive disclosure: memory_summary.md is injected at start,
MEMORY.md is searched when prior work looks relevant, and rollout summaries
are opened only when more detail is needed.

Requires: Docker Desktop running.
"""

import asyncio

from docker import from_env as docker_from_env

from agents import ModelSettings, Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Filesystem, Memory, Shell
from agents.sandbox.entries import File
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions

from progress import Spinner

manifest = Manifest(
    entries={
        "data/risks.md": File(
            content=(
                b"# Delivery risks\n\n"
                b"- Security questionnaire not complete.\n"
                b"- Procurement needs final legal language by April 1.\n"
            )
        ),
    }
)

agent = SandboxAgent(
    name="Memory-enabled reviewer",
    model="gpt-5.4",
    model_settings=ModelSettings(reasoning={"effort": "none"}),
    instructions=(
        "Inspect the workspace and retain useful lessons "
        "for follow-up runs."
    ),
    default_manifest=manifest,
    capabilities=[Memory(), Filesystem(), Shell()],
)


async def main() -> None:
    async with Spinner("Memory-enabled reviewer analyzing risks"):
        result = await Runner.run(
            agent,
            "Review the workspace files and summarize the key risks. "
            "Store any lessons learned for future runs.",
            max_turns=3,
            run_config=RunConfig(
                sandbox=SandboxRunConfig(
                    client=DockerSandboxClient(docker_from_env()),
                    options=DockerSandboxClientOptions(image="python:3.14-slim"),
                ),
            ),
        )

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

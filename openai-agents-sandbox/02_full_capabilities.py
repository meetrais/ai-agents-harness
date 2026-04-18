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
import tempfile
from pathlib import Path

from docker import from_env as docker_from_env

from agents import Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Filesystem, Memory, Shell
from agents.sandbox.entries import LocalDir
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions


async def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        dataroom = Path(tmp) / "dataroom"
        dataroom.mkdir()
        (dataroom / "risks.md").write_text(
            """# Delivery risks

- Security questionnaire not complete.
- Procurement needs final legal language by April 1.
""",
            encoding="utf-8",
        )

        agent = SandboxAgent(
            name="Memory-enabled reviewer",
            model="gpt-5.4",
            instructions=(
                "Inspect the workspace and retain useful lessons "
                "for follow-up runs."
            ),
            default_manifest=Manifest(entries={"data": LocalDir(src=dataroom)}),
            capabilities=[Memory(), Filesystem(), Shell()],
        )

        result = await Runner.run(
            agent,
            "Review the workspace files and summarize the key risks. "
            "Store any lessons learned for future runs.",
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

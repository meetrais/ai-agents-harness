"""Docker Sandbox with Custom Options.

Shows how to pass DockerSandboxClientOptions to customize the container
image used for execution.

Requires: Docker Desktop running.
"""

import asyncio

from docker import from_env as docker_from_env

from agents import Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Shell
from agents.sandbox.config import DEFAULT_PYTHON_SANDBOX_IMAGE
from agents.sandbox.entries import File
from agents.sandbox.sandboxes.docker import (
    DockerSandboxClient,
    DockerSandboxClientOptions,
)

manifest = Manifest(
    entries={
        "account_brief.md": File(
            content=(
                b"# Northwind Health\n\n"
                b"- Segment: Mid-market healthcare analytics.\n"
                b"- Renewal date: 2026-04-15.\n"
            )
        ),
        "implementation_risks.md": File(
            content=(
                b"# Delivery risks\n\n"
                b"- Security questionnaire not complete.\n"
                b"- Procurement needs final legal language by April 1.\n"
            )
        ),
    }
)

agent = SandboxAgent(
    name="Docker Sandbox Analyst",
    model="gpt-5.4",
    instructions=(
        "Review the workspace before answering. "
        "Keep the response concise and cite file names."
    ),
    default_manifest=manifest,
    capabilities=[Shell()],
)


async def main():
    result = await Runner.run(
        agent,
        "Summarize the blockers and recommend next actions.",
        run_config=RunConfig(
            sandbox=SandboxRunConfig(
                client=DockerSandboxClient(docker_from_env()),
                options=DockerSandboxClientOptions(
                    image=DEFAULT_PYTHON_SANDBOX_IMAGE,
                ),
            ),
            workflow_name="Docker sandbox review",
        ),
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

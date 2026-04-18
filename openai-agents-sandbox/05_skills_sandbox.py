"""Loading Skills into the Sandbox.

Shows how to mount a Git-based skill repository into the sandbox
so the agent can use pre-built procedures before doing its work.

Requires: Docker Desktop running.
"""

import asyncio

from docker import from_env as docker_from_env

from agents import Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Capabilities, Skills
from agents.sandbox.entries import File, GitRepo
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions

manifest = Manifest(
    entries={
        "client_data.md": File(
            content=(
                b"# Client: Acme Corp\n\n"
                b"- Revenue: $2.4M\n"
                b"- Filing status: C-Corp\n"
                b"- Fiscal year end: December 31\n"
            )
        ),
    }
)

agent = SandboxAgent(
    name="Tax prep assistant",
    model="gpt-5.4",
    instructions="Use the mounted skill before preparing the return.",
    default_manifest=manifest,
    capabilities=Capabilities.default() + [
        Skills(from_=GitRepo(repo="owner/tax-prep-skills", ref="main")),
    ],
)


async def main():
    result = await Runner.run(
        agent,
        "Review client_data.md and prepare a preliminary tax summary.",
        run_config=RunConfig(
            sandbox=SandboxRunConfig(
                client=DockerSandboxClient(docker_from_env()),
                options=DockerSandboxClientOptions(image="python:3.14-slim"),
            ),
            workflow_name="Skills sandbox example",
        ),
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

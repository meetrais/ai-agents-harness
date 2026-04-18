"""Loading Skills into the Sandbox.

Shows how to provide skill/procedure files so the agent can follow
pre-built steps before doing its work.

Requires: Docker Desktop running.
"""

import asyncio

from docker import from_env as docker_from_env

from agents import ModelSettings, Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Capabilities
from agents.sandbox.entries import File
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions

from progress import Spinner

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
        "skills/tax_prep_checklist.md": File(
            content=(
                b"# Tax Preparation Checklist\n\n"
                b"1. Verify client filing status and entity type.\n"
                b"2. Confirm fiscal year end date.\n"
                b"3. Review revenue figures and categorize income streams.\n"
                b"4. Identify applicable deductions (QBID, depreciation, etc.).\n"
                b"5. Estimate quarterly tax obligations.\n"
                b"6. Flag any items requiring CPA review.\n"
            )
        ),
    }
)

agent = SandboxAgent(
    name="Tax prep assistant",
    model="gpt-5.4",
    model_settings=ModelSettings(reasoning={"effort": "none"}),
    instructions=(
        "Before preparing any tax summary, read and follow the checklist "
        "in skills/tax_prep_checklist.md. Cite the checklist steps you completed."
    ),
    default_manifest=manifest,
)


async def main():
    async with Spinner("Tax prep assistant reviewing client data"):
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

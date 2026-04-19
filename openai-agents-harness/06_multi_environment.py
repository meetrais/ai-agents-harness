import asyncio
import logging
import os
from pathlib import Path

from agents import ModelSettings, Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Filesystem, Memory, Shell
from agents.sandbox.entries import LocalDir

from progress import Spinner

logging.basicConfig(level=logging.WARNING)

# Path to the external dataroom directory
DATAROOM = Path(__file__).resolve().parent.parent / "dataroom"


def get_run_config():
    """Dynamically get the run config based on the ENVIRONMENT variable."""
    env = os.getenv("ENVIRONMENT", "local")

    if env == "local":
        from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient
        return RunConfig(
            sandbox=SandboxRunConfig(client=UnixLocalSandboxClient())
        )

    elif env == "staging":
        from docker import from_env as docker_from_env
        from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions
        return RunConfig(
            sandbox=SandboxRunConfig(
                client=DockerSandboxClient(docker_from_env()),
                options=DockerSandboxClientOptions(image="python:3.14-slim"),
            )
        )

    elif env == "production":
        from agents.extensions.sandbox.modal import ModalSandboxClient
        return RunConfig(
            sandbox=SandboxRunConfig(client=ModalSandboxClient())
        )
    
    raise ValueError(f"Unknown environment: {env}")


async def main() -> None:
    # Mount the dataroom directory into the container at "data/"
    manifest = Manifest(
        entries={"data": LocalDir(src=DATAROOM)},
    )

    # In harness architecture, the agent definition stays exactly the same across
    # different environments
    agent = SandboxAgent(
        name="Dataroom Analyst",
        model="gpt-5.4",
        model_settings=ModelSettings(reasoning={"effort": "none"}),
        instructions="Answer using only files in data/. Cite source filenames.",
        default_manifest=manifest,
        capabilities=[Memory(), Filesystem(), Shell()],
    )

    env = os.getenv("ENVIRONMENT", "local")
    async with Spinner(f"Dataroom Analyst analyzing data in {env.upper()} environment"):
        result = await Runner.run(
            agent,
            "Compare FY2025 revenue, operating income, and operating cash flow with FY2024.",
            max_turns=10,
            run_config=get_run_config(),
        )

    print("\n" + "=" * 60)
    print(f"AGENT OUTPUT ({env.upper()}):")
    print("=" * 60)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

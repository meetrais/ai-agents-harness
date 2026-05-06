"""Shared harness setup for the sandbox examples."""

from __future__ import annotations

from pathlib import Path

from agents import ModelSettings, Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Filesystem, Shell
from agents.sandbox.entries import LocalDir
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions
from docker import from_env as docker_from_env

from harness_config import (
    DATAROOM_AGENT_INSTRUCTIONS,
    DATAROOM_TASK_INSTRUCTION,
    DEFAULT_DOCKER_IMAGE,
    DEFAULT_MODEL,
    DEFAULT_REASONING,
)


DATAROOM = Path(__file__).resolve().parent.parent / "dataroom"


def create_dataroom_manifest() -> Manifest:
    """Mount the shared dataroom directory into the sandbox at data/."""
    return Manifest(entries={"data": LocalDir(src=DATAROOM)})


def create_dataroom_agent(
    *,
    model: str = DEFAULT_MODEL,
    instructions: str = DATAROOM_AGENT_INSTRUCTIONS,
) -> SandboxAgent:
    """Build the standard dataroom analyst worker agent."""
    return SandboxAgent(
        name="Dataroom Analyst",
        model=model,
        model_settings=ModelSettings(reasoning=DEFAULT_REASONING),
        instructions=instructions,
        default_manifest=create_dataroom_manifest(),
        capabilities=[Filesystem(), Shell()],
    )


def create_docker_run_config(
    *,
    workflow_name: str = "Docker sandbox review",
    image: str = DEFAULT_DOCKER_IMAGE,
) -> RunConfig:
    """Build the Docker-backed run config used by the examples."""
    return RunConfig(
        sandbox=SandboxRunConfig(
            client=DockerSandboxClient(docker_from_env()),
            options=DockerSandboxClientOptions(image=image),
        ),
        workflow_name=workflow_name,
    )


async def run_dataroom_task(*, max_turns: int = 10):
    """Run the standard dataroom task and return the SDK result."""
    return await Runner.run(
        create_dataroom_agent(),
        DATAROOM_TASK_INSTRUCTION,
        max_turns=max_turns,
        run_config=create_docker_run_config(),
    )

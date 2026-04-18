"""Resume a Sandbox Session.

Demonstrates pausing work after a first run, freezing the session state,
then resuming from the same workspace with a follow-up instruction.

Requires: Docker Desktop running.
"""

import asyncio

from docker import from_env as docker_from_env

from agents import ModelSettings, Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Filesystem, Shell
from agents.sandbox.entries import File
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions

from progress import Spinner

manifest = Manifest(
    entries={
        "app.py": File(
            content=(
                b"# placeholder app\n"
                b"def main():\n"
                b"    print('hello world')\n\n"
                b"if __name__ == '__main__':\n"
                b"    main()\n"
            )
        ),
    }
)

agent = SandboxAgent(
    name="Iterative Builder",
    model="gpt-5.4",
    model_settings=ModelSettings(reasoning={"effort": "none"}),
    instructions="Work inside the sandbox workspace. Be concise.",
    default_manifest=manifest,
    capabilities=[Filesystem(), Shell()],
)


async def main():
    client = DockerSandboxClient(docker_from_env())
    options = DockerSandboxClientOptions(image="python:3.14-slim")

    # --- First run: build the initial version ---
    session = await client.create(manifest=manifest, options=options)
    async with session:
        async with Spinner("Iterative Builder — first run"):
            first_result = await Runner.run(
                agent,
                "Build the first version of the app.",
                max_turns=20,
                run_config=RunConfig(
                    sandbox=SandboxRunConfig(session=session),
                    workflow_name="Sandbox resume example",
                ),
            )

    print("--- First run output ---")
    print(first_result.final_output)

    # Freeze session state so we can resume later
    conversation = first_result.to_input_list()
    frozen_session_state = client.deserialize_session_state(
        client.serialize_session_state(session.state)
    )

    # Add a follow-up instruction
    conversation.append({
        "role": "user",
        "content": "Continue from the existing workspace and add tests.",
    })

    # --- Second run: resume in the same workspace ---
    resumed_session = await client.resume(frozen_session_state)
    try:
        async with resumed_session:
            async with Spinner("Iterative Builder — resumed run"):
                second_result = await Runner.run(
                    agent,
                    conversation,
                    max_turns=20,
                    run_config=RunConfig(
                        sandbox=SandboxRunConfig(session=resumed_session),
                    ),
                )
        print("--- Second run output ---")
        print(second_result.final_output)
    finally:
        await client.delete(resumed_session)


if __name__ == "__main__":
    asyncio.run(main())

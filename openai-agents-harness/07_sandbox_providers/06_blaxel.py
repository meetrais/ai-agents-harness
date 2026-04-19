import asyncio
import logging
from pathlib import Path

from agents import ModelSettings, Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Filesystem, Memory, Shell
from agents.sandbox.entries import LocalDir

from progress import Spinner
from agents.extensions.sandbox.blaxel import BlaxelSandboxClient

logging.basicConfig(level=logging.WARNING)

DATAROOM = Path(__file__).resolve().parent.parent.parent / "dataroom"

async def main() -> None:
    manifest = Manifest(entries={"data": LocalDir(src=DATAROOM)})

    agent = SandboxAgent(
        name="Dataroom Analyst (Blaxel)",
        model="gpt-5.4",
        model_settings=ModelSettings(reasoning={"effort": "none"}),
        instructions="Answer using only files in data/. Cite source filenames. Read and write any memory files directly in the current directory, do not attempt to escape to parent directories.",
        default_manifest=manifest,
        capabilities=[Memory(), Filesystem(), Shell()],
    )

    async with Spinner("Blaxel Dataroom Analyst analyzing data"):
        result = await Runner.run(
            agent,
            "Compare FY2025 revenue, operating income, and operating cash flow with FY2024.",
            max_turns=10,
            run_config=RunConfig(
                sandbox=SandboxRunConfig(client=BlaxelSandboxClient())
            ),
        )

    print("\n" + "=" * 60)
    print("AGENT OUTPUT (BLAXEL):")
    print("=" * 60)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

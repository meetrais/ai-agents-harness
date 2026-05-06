"""Basic SandboxAgent with Docker execution (Windows-compatible).

Requires:
  - pip install "openai-agents[docker]"
  - Docker Desktop running
  - OPENAI_API_KEY env var set
"""

import asyncio
import logging

from harness_common import run_dataroom_task
from harness_config import DATAROOM_TASK_INSTRUCTION
from progress import Spinner

logging.basicConfig(level=logging.WARNING)


async def main() -> None:
    async with Spinner("Dataroom Analyst analyzing data"):
        result = await run_dataroom_task(max_turns=10)

    print("\n" + "=" * 60)
    print("TASK:")
    print(DATAROOM_TASK_INSTRUCTION)
    print("=" * 60)
    print("AGENT OUTPUT:")
    print("=" * 60)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

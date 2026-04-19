# OpenAI Agents SDK - Sandbox Examples

Demonstrates the **SandboxAgent** feature of the OpenAI Agents SDK using
Docker containers for isolated execution.

Based on: https://openai.com/index/the-next-evolution-of-the-agents-sdk/

## Prerequisites

- Python 3.10+
- `OPENAI_API_KEY` environment variable
- Docker Desktop running

## Setup

```bash
uv pip install -r requirements.txt
```

> **Note**: For testing the sandbox provider scripts in `07_sandbox_providers/`, you will need to install the SDK for your preferred provider (e.g., `uv pip install modal e2b`).

## Examples

| Script / Folder | Description |
|---|---|
| `01_basic_sandbox.py` | Mounts a local data directory into the sandbox and queries it |
| `02_full_capabilities.py` | Filesystem, Shell, and Memory capabilities combined |
| `03_custom_sandbox_options.py` | Custom Docker image and options |
| `04_resume_session.py` | Pause and resume a sandbox session across turns |
| `05_skills_sandbox.py` | Mount a Git-based skill into the sandbox |
| `06_multi_environment.py` | Dynamically swaps Sandbox Client backends based on `ENVIRONMENT` variable (local, staging, production) |
| `07_sandbox_providers/` | Ready-to-use provider scripts tailored for Daytona, E2B, Modal, Cloudflare, Vercel, Blaxel, and Runloop |

## Running

You can use `uv run` to correctly execute the sandbox in your environment context:

```bash
uv run 01_basic_sandbox.py
```

To run a multi-environment script:
```bash
ENVIRONMENT=local uv run 06_multi_environment.py
```

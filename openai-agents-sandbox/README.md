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
pip install -r requirements.txt
```

## Examples

| Script | Description |
|---|---|
| `01_basic_sandbox.py` | Mounts a local data directory into the sandbox and queries it |
| `02_full_capabilities.py` | Filesystem, Shell, and Memory capabilities combined |
| `03_custom_sandbox_options.py` | Custom Docker image and options |
| `04_resume_session.py` | Pause and resume a sandbox session across turns |
| `05_skills_sandbox.py` | Mount a Git-based skill into the sandbox |

## Running

```bash
python 01_basic_sandbox.py
```

# AI Agents Harness

> **A robust, multi-environment sandbox harness for OpenAI Agents.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI SDK](https://img.shields.io/badge/OpenAI-SDK-orange.svg)](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository provides a unified architecture for developing, testing, and deploying AI agents with isolated code execution capabilities. The **Harness Architecture** decouples agent business logic from infrastructure, enabling seamless transitions from local development to production.

---

## Key Features

- **Multi-Environment Support**: Seamlessly swap execution backends (Unix Local, Docker, Modal, etc.) using simple environment variables.
- **Decoupled Architecture**: Write your agent definition once; run it anywhere without modifying the core logic.
- **Secure Sandboxing**: Isolated execution environments for untrusted code, leveraging the OpenAI Agents SDK's `SandboxAgent`.
- **Rich Provider Ecosystem**: Built-in support for top-tier sandbox providers including Daytona, E2B, Modal, Cloudflare, and more.
- **Data Mounting**: Easy mapping of local directories and "datarooms" into the agent's execution context.

---

## Architecture Overview

The core philosophy of this harness is to treat the **Sandbox Provider** as a swappable configuration rather than a hardcoded implementation detail.

```mermaid
graph TD
    A[Agent Definition] --> B{Environment Harness}
    B -- ENVIRONMENT=local --> C[Unix Local Sandbox]
    B -- ENVIRONMENT=staging --> D[Docker Container]
    B -- ENVIRONMENT=production --> E[Cloud Provider: Modal/E2B/etc.]
    
    F[Data Room] -.-> C
    F[Data Room] -.-> D
    F[Data Room] -.-> E
```

---

## Project Structure

```text
ai-agents-harness/
├── openai-agents-harness/  # Implementation & Examples
│   ├── 01_... to 05_...    # Feature-specific demonstrations
│   ├── 06_multi_env.py     # Core multi-environment harness
│   └── 07_providers/       # Standalone provider integrations
├── dataroom/               # Local data directories for mounting
└── LICENSE                 # MIT License
```

---

## Getting Started

### Prerequisites

- **Python**: 3.10 or higher.
- **API Keys**: `OPENAI_API_KEY` is required. Provider-specific keys (e.g., `MODAL_TOKEN_ID`, `E2B_API_KEY`) are needed for cloud execution.
- **Docker**: Required for local container-based sandboxing.

### Installation

We recommend using [uv](https://github.com/astral-sh/uv) for fast dependency management:

```bash
# Clone the repository
git clone https://github.com/meetrais/ai-agents-harness.git
cd ai-agents-harness/openai-agents-harness

# Install base dependencies
uv pip install -r requirements.txt

# (Optional) Install provider-specific extras
uv pip install "openai-agents[modal,e2b,daytona]"
```

---

## Usage Examples

Explore the library of patterns available in the `openai-agents-harness/` directory:

| Example | Description |
| :--- | :--- |
| **Basic Sandbox** | [01_basic_sandbox.py](./openai-agents-harness/01_basic_sandbox.py) |
| **Multi-Env Harness** | [06_multi_environment.py](./openai-agents-harness/06_multi_environment.py) |
| **Custom Images** | [03_custom_sandbox_options.py](./openai-agents-harness/03_custom_sandbox_options.py) |
| **Session Persistence**| [04_resume_session.py](./openai-agents-harness/04_resume_session.py) |

### Running the Harness

To run the agent in different environments:

```bash
# Default (Local execution)
uv run 06_multi_environment.py

# Docker-based (Staging)
ENVIRONMENT=staging uv run 06_multi_environment.py

# Cloud-based (Production - requires Modal setup)
ENVIRONMENT=production uv run 06_multi_environment.py
```

---

## Supported Providers

This harness supports a wide variety of sandboxing providers out of the box. Check the [Providers README](./openai-agents-harness/07_sandbox_providers/README.md) for setup details.

- **[Daytona](https://daytona.io)**: Standard dev environments.
- **[E2B](https://e2b.dev)**: Optimized specialized sandboxes for AI.
- **[Modal](https://modal.com)**: Serverless micro-VMs with GPU support.
- **[Runloop](https://runloop.ai)**: Devboxes with advanced state serialization.
- **[Blaxel](https://blaxel.ai)**: Perpetual sandboxes with ultra-fast cold starts.

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

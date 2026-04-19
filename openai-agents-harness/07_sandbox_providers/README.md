# Sandbox Providers

This folder contains standalone scripts demonstrating how to deploy the OpenAI Agent Sandbox onto various cloud computing providers. Each provider spins up a secure, sandboxed execution environment (often a microVM or container) for the agent to safely execute code.

## Providers Overview & Setup

### 1. Daytona (`01_daytona.py`)
[Daytona](https://daytona.io) offers self-hosted and cloud development environments. It specializes in spinning up standard dev environments quickly.
* **Installation:** `uv pip install "openai-agents[daytona]"`
* **Authentication:** Generally relies on a Daytona profile/CLI login. Run `daytona login` or configure `DAYTONA_API_KEY`.

### 2. E2B (`02_e2b.py`)
[E2B](https://e2b.dev) is specifically built for AI agents. It provides secure, heavily-isolated long-running sandboxes optimized for fast code execution.
* **Installation:** `uv pip install "openai-agents[e2b]"`
* **Authentication:** Get an API key from the E2B dashboard and set it using: 
  ```bash
  export E2B_API_KEY="your-key"
  ```

### 3. Modal (`03_modal.py`)
[Modal](https://modal.com) provides serverless microVMs tightly integrated with Python, allowing for dynamic scale-out to GPUs and instant cold boots.
* **Installation:** `uv pip install "openai-agents[modal]"`
* **Authentication:** Run the setup command in your terminal. It will open a browser to generate a token:
  ```bash
  uv run modal setup
  ```

### 4. Cloudflare (`04_cloudflare.py`)
[Cloudflare](https://cloudflare.com) offers edge-native execution.
* **Installation:** `uv pip install "openai-agents[cloudflare]"`
* **Authentication:** Requires `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. Authenticate via their CLI or set the environment variables.

### 5. Vercel (`05_vercel.py`)
[Vercel](https://vercel.com) provides edge compute and serverless functions built seamlessly into frontend pipelines.
* **Installation:** `uv pip install "openai-agents[vercel]"`
* **Authentication:** Set `VERCEL_API_TOKEN` or authenticate globally via Vercel CLI.

### 6. Blaxel (`06_blaxel.py`)
[Blaxel](https://blaxel.ai) focuses on "perpetual sandboxes" tailored for AI agents, offering sub-25ms cold starts. It handles idle states effectively to lower costs.
* **Installation:** `uv pip install "openai-agents[blaxel]"`
* **Authentication:** Set your Blaxel API key in your environment settings or login using the Blaxel CLI.
  ```bash
  export BLAXEL_API_KEY="your-key"
  ```

### 7. Runloop (`07_runloop.py`)
[Runloop](https://runloop.ai) provides "devboxes" which are cloud-hosted micro-VMs. It offers advanced serialization, allowing agents to pause and resume memory states seamlessly.
* **Installation:** `uv pip install "openai-agents[runloop]"`
* **Authentication:** Obtain a Runloop API key and set it before execution:
  ```bash
  export RUNLOOP_API_KEY="your-key"
  ```

---

## How to execute a provider

Once you have installed the respective package and authenticated your terminal (using the API keys or CLI logins detailed above), you can run any of the examples directly via `uv`:

```bash
# Example: running E2B
uv run 02_e2b.py
```

# Part 6: Technical Implementation Details

---

## Technical Deep Dive: Overview

**Purpose**: Explain key MARS implementation choices

**Topics**:
1. Git Worktrees - Parallel development
2. AskSage Integration - DoD AI access via LiteLLM
3. Sysbox Runtime - Secure containerization
4. Git Submodules - Dependency management

**Audience**: Technical stakeholders, infrastructure teams

---

# Worktrees: Parallel Development

---

## The Problem: Linear Development Bottleneck

**Traditional Git Workflow**:
```
main branch (work blocked while testing)
    ↓
Create feature branch
    ↓
Make changes (can't work on other features)
    ↓
Test, iterate
    ↓
Merge back to main
    ↓
Switch to next feature
```

**Limitations**:
- ❌ One task at a time per repository
- ❌ Frequent context switching
- ❌ Long-running tasks block other work
- ❌ Testing requires checkout/stash dance

---

## Git Worktrees: The Solution

**What is a worktree?**
> Multiple working directories for the same repository, each with its own branch

**Visual Concept**:
```
Main Repository (/workspace/mars-v2)
    ↓ branch: main

Worktree 1 (/workspace/mars-v2/mars-dev/worktrees/feature-a)
    ↓ branch: feature/a

Worktree 2 (/workspace/mars-v2/mars-dev/worktrees/feature-b)
    ↓ branch: feature/b

Worktree 3 (/workspace/mars-v2/mars-dev/worktrees/testing)
    ↓ branch: test/integration
```

**All share**: Same .git history, tags, remotes
**Each has**: Own working directory, own branch, own state

---

## Worktrees in MARS Development

![Git Worktrees Workflow](diagrams/png/git-worktrees-workflow.png){ width=85% }

**How MARS Uses Worktrees**:

**Parallel Sprint Development** (E8 Orchestration):
- **5-25 concurrent CCC sessions**, each in own worktree
- Example: Sprint 7 (Wave 2) = 8 worktrees simultaneously
- Each worktree = isolated environment for one task

**Typical MARS Worktree Structure**:
```
mars-v2/                           # Main repo (read-only during sprints)
├── mars-dev/worktrees/
│   ├── c2-zotero-fixes/          # Component 2 work
│   ├── c4-infrastructure/         # Component 4 enhancements
│   ├── s7-wave2-agent-scaffold/   # Sprint 7 task
│   ├── s7-wave2-testing/          # Parallel testing
│   └── mars-writing/              # Documentation sessions
```

---

## Worktrees: Benefits for MARS

**1. True Parallel Development**:
- Work on C2 (Zotero) while C4 (Infrastructure) builds
- Run tests in one worktree, write code in another
- Documentation in one worktree, implementation in another

**2. No Context Loss**:
- Each worktree preserves full IDE state
- Terminal history stays relevant
- No constant branch switching

**3. Isolated Testing**:
- Test changes without affecting main development
- Multiple test configurations simultaneously
- Integration testing in dedicated worktree

**4. Sprint Orchestration** (E8):
- 5-25 parallel CCC sessions (one per worktree)
- Zellij dashboard shows all sessions
- Merge queue for controlled integration

**Productivity Gain**: **40-60% faster** multi-task development

---

## Worktrees: Command Primer

**Create a worktree**:
```bash
# From main repository
git worktree add ../worktrees/feature-x -b feature/x

# Result:
# - New directory: ../worktrees/feature-x
# - New branch: feature/x (checked out in worktree)
# - Ready to work immediately
```

**List all worktrees**:
```bash
git worktree list

# Output:
# /workspace/mars-v2              abc1234 [main]
# /workspace/mars-v2/../feature-x def5678 [feature/x]
```

**Work in worktree** (completely isolated):
```bash
cd ../worktrees/feature-x
vim code.py               # Make changes
git add code.py
git commit -m "feat: Add feature X"
# Main repo unaffected, other worktrees unaffected
```

**Merge back to main**:
```bash
cd /workspace/mars-v2    # Back to main repo
git merge feature/x      # Integrate changes
```

---

## Worktrees: MARS E8 Integration

**E8 Parallel Orchestration** uses worktrees for **sprint management**:

**Sprint Planning** (`mars-dev/sprints/s7-wave2/sprint.yaml`):
```yaml
tasks:
  - id: T1-agent-scaffold
    worktree: s7-wave2-agent-scaffold
    branch: feat/s7-wave2-agent-scaffold

  - id: T2-testing
    worktree: s7-wave2-testing
    branch: feat/s7-wave2-testing
```

**Automated Worktree Creation**:
```bash
# Script: mars-dev/scripts/create-worktrees.sh
./mars-dev/scripts/create-worktrees.sh sprints/s7-wave2/sprint.yaml

# Creates 8 worktrees, 8 branches, 8 Zellij panes
# Each ready for parallel CCC session
```

**Result**: **8 tasks progressing simultaneously** instead of sequentially

---

## Worktrees: Real-World MARS Example

**Scenario**: Sprint 7 Wave 2 (8 parallel tasks)

**Setup** (1 command):
```bash
./mars-dev/scripts/launch-sprint.py sprints/s7-wave2/sprint.yaml
```

**What Happens**:
1. Creates 8 worktrees (one per task)
2. Creates 8 branches (one per task)
3. Launches Zellij dashboard (8 panes)
4. Starts 8 CCC sessions (one per pane)
5. Loads task context into each session

**Parallel Execution**:
- Pane 1: Agent scaffolding
- Pane 2: Integration testing
- Pane 3: Documentation updates
- Pane 4: ADR authoring
- Pane 5-8: Other tasks

**Merge Strategy**: Controlled queue (one worktree at a time)

**Productivity**: 8 tasks in **parallel** vs. **sequential** = **5-7× faster sprints**

---

# AskSage Integration

---

## The Challenge: DoD AI Access

**Problem**: Commercial AI services not allowed on classified networks

**Requirements**:
- ✅ Air-gap capable (no internet)
- ✅ DoD accredited (ATO/security review)
- ✅ Data never leaves network
- ✅ Vendor lock-in avoidance

**Traditional Solution**: Build everything from scratch
**MARS Solution**: AskSage + LiteLLM abstraction

---

## What is AskSage?

**AskSage**: Navy-hosted AI service (GPT-4, Claude, Llama)

**Architecture**:
```
Navy CAPRA Endpoint (https://capra.flankspeed.dso.mil)
    ↓ (DoD PKI authentication)
AskSage API Gateway
    ↓ (routes to available models)
Commercial AI Providers (Azure OpenAI, AWS Bedrock)
    ↓ (via FedRAMP connections)
LLM Models (GPT-4, Claude 3.5, Llama 3)
```

**Key Features**:
- 🔐 **DoD PKI authentication** (CAC/ECA required)
- 🛡️ **FedRAMP authorized** connections
- 📊 **Usage tracking** and audit logs
- 🚫 **No training** on your data (contractual)
- 💰 **Government rates** (volume discounts)

---

## AskSage vs. Commercial Anthropic

| Feature | **AskSage** | **Commercial Anthropic** |
|---------|-------------|-------------------------|
| **Access** | DoD PKI (CAC/ECA) | API key (anyone) |
| **Network** | FedRAMP connection | Public internet |
| **Data Policy** | No training (contract) | No training (policy) |
| **Cost** | Gov't rates (~50% less) | Standard API rates |
| **Models** | GPT-4, Claude, Llama | Claude only |
| **Classified** | ✅ Allowed (with ATO) | ❌ Prohibited |
| **Air-Gap** | ⚠️ Partial (local fallback) | ❌ Not possible |
| **Audit** | ✅ Full DoD logging | ⚠️ Limited |

**MARS Approach**: Use AskSage for classified, Anthropic for unclassified (LiteLLM handles both)

---

## The LiteLLM Shim: Why It Matters

**Problem**: Each AI provider has different API

**OpenAI API**:
```python
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Anthropic API**:
```python
import anthropic
response = anthropic.Anthropic().messages.create(
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**AskSage API**:
```python
import requests
response = requests.post(
    "https://capra.flankspeed.dso.mil/v1/chat/completions",
    headers={"Authorization": f"Bearer {pki_token}"},
    json={"model": "gpt-4", "messages": [...]}
)
```

**All different!** Hard-coded vendor = lock-in

---

## LiteLLM: Unified AI Gateway

![LiteLLM Architecture](diagrams/png/litellm-architecture.png){ width=85% }

**LiteLLM**: Translates all providers → OpenAI-compatible API

**MARS Architecture**:
```
MARS Agents
    ↓ (OpenAI API format - always)
LiteLLM Proxy (localhost:4000)
    ↓ (routes based on config)
┌──────────────┬─────────────────┬──────────────┐
AskSage        Anthropic         Ollama
(via CAPRA)    (commercial)      (local GPU)
```

**Configuration** (`litellm-config.yaml`):
```yaml
model_list:
  - model_name: claude-sonnet
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_base: https://capra.flankspeed.dso.mil/v1
      api_key: ${ASKSAGE_API_KEY}

  - model_name: claude-sonnet
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: ${ANTHROPIC_API_KEY}
```

**MARS Agents**: Just call `localhost:4000/v1/chat/completions` → LiteLLM handles routing

---

## LiteLLM Benefits for MARS

**1. Vendor Independence**:
- Switch providers without code changes
- Use AskSage on classified, Anthropic on unclass
- Fallback to local Ollama if network down

**2. Unified Interface**:
- All agents use same API (OpenAI format)
- No vendor-specific code
- Simplified agent development

**3. Cost Optimization**:
- Route expensive calls to cheaper models
- Load balancing across providers
- Usage tracking and quotas

**4. Security & Compliance**:
- Single point of authentication
- Centralized audit logging
- API key rotation without code changes

**5. Air-Gap Readiness**:
- Swap AskSage → Ollama (config change only)
- No agent code modifications
- Seamless transition to offline operation

---

## LiteLLM Configuration Example

**MARS uses 3 providers simultaneously**:

```yaml
# litellm-config.yaml
model_list:
  # AskSage (DoD classified work)
  - model_name: gpt-4-asksage
    litellm_params:
      model: azure/gpt-4
      api_base: https://capra.flankspeed.dso.mil/v1
      api_key: os.environ/ASKSAGE_API_KEY

  # Anthropic (unclassified work)
  - model_name: claude-sonnet
    litellm_params:
      model: claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

  # Ollama (air-gap fallback)
  - model_name: local-llama
    litellm_params:
      model: ollama/llama3.1:70b
      api_base: http://localhost:11434
```

**Agent Code** (same for all):
```python
import openai
client = openai.OpenAI(base_url="http://localhost:4000/v1")

response = client.chat.completions.create(
    model="claude-sonnet",  # LiteLLM routes appropriately
    messages=[{"role": "user", "content": "Analyze this data"}]
)
```

**No vendor-specific code!**

---

## AskSage Authentication Flow

**Challenge**: AskSage requires DoD PKI (CAC/ECA)

**MARS Solution**:

**1. Manual Token Acquisition** (one-time setup):
```bash
# User authenticates with CAC/ECA via browser
# Receives JWT token (valid 30 days)
export ASKSAGE_API_KEY="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Saved in mars-env.config (sourced at session start)
```

**2. LiteLLM Token Refresh** (automatic):
```yaml
# litellm-config.yaml
general_settings:
  asksage_token_refresh:
    enabled: true
    refresh_endpoint: https://capra.flankspeed.dso.mil/auth/refresh
    refresh_interval: 86400  # 24 hours
```

**3. Fallback to Anthropic** (if token expires):
```python
# LiteLLM automatically tries alternate providers
# Config: fallbacks = ["claude-sonnet", "local-llama"]
```

**Result**: Minimal user intervention, seamless failover

---

# Sysbox: Secure Containers

---

## The Container Security Challenge

**Standard Docker** (privileged containers):
```
Container (runs as root inside)
    ↓ (has full system access)
Host Kernel
    ↓ (vulnerable to container escape)
Host Filesystem, Network, Devices
```

**Problem**: Root inside container = root on host (with escape exploits)

**Traditional Solutions**:
- **Rootless Docker**: Docker daemon runs as user (complex setup)
- **User Namespaces**: Map root → user (limited compatibility)
- **SELinux/AppArmor**: Mandatory access control (complex policies)

**MARS Solution**: **Sysbox** runtime

---

## What is Sysbox?

**Sysbox**: Container runtime that provides **system-level isolation**

**Key Feature**: Containers that **feel like VMs** but are still containers

**Magic Trick**:
- Container **thinks** it has full system access (systemd, Docker-in-Docker)
- Host **knows** container is isolated (UID/GID mapping, namespaces)
- Security **improved** (no privileged mode needed)

**Created by**: Nestybox (acquired by Docker, 2022)
**Used by**: GitLab CI (Docker-in-Docker), Tailscale (system containers)

---

## Docker Runtimes: Standard vs. Sysbox

**Standard Docker (runc runtime)**:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock myimage
```
- ⚠️ Container has **full Docker control** (can break out)
- ⚠️ Mounted `/var/run/docker.sock` = root on host

**Rootless Docker** (rootless daemon):
```
dockerd-rootless.sh
docker run myimage
```
- ✅ Docker daemon runs as user (no root)
- ❌ **Complex setup** (slirp4netns, uidmap, XDG_RUNTIME_DIR)
- ❌ **Limited features** (no privileged ports, no systemd)

**Sysbox Runtime** (MARS approach):
```
docker run --runtime=sysbox-runc myimage
```
- ✅ **Simple**: Standard Docker workflow
- ✅ **Secure**: UID/GID remapping automatic
- ✅ **Compatible**: Full Docker-in-Docker support
- ✅ **Systemd**: Works inside containers

---

## Sysbox Architecture

![Sysbox Architecture](diagrams/png/sysbox-architecture.png){ width=85% }

**How Sysbox Works**:

**Layer 1: Host Docker Daemon** (runs as root, manages containers)
```
dockerd (system daemon, TCP socket at localhost:9088)
```

**Layer 2: Sysbox Runtime** (intercepts container creation)
```
sysbox-runc (OCI runtime)
    ↓ (creates user namespace)
sysbox-fs (FUSE filesystem)
    ↓ (emulates /proc, /sys)
sysbox-mgr (resource management)
```

**Layer 3: Container** (isolated environment)
```
Container sees: UID 0 (root), full /proc, /sys, can run Docker
Host sees: UID 100000+ (unprivileged user), namespaced
```

**Key Insight**: Container **believes** it's privileged, but host **enforces** unprivileged operation

---

## DOCKER_HOST: Understanding Docker Sockets

**The Docker Socket Landscape**:

**1. System Docker Socket** (privileged):
```
/var/run/docker.sock (owned by root:docker)
```
- Default Docker daemon socket
- Requires `docker` group membership or root
- **MARS uses this** (via Sysbox isolation)

**2. Rootless Docker Socket** (user):
```
/run/user/1000/docker.sock (owned by user)
```
- Rootless daemon socket
- User-specific (XDG_RUNTIME_DIR)
- **MARS doesn't use** (too complex for multi-user)

**3. Remote Docker Socket** (TCP):
```
tcp://localhost:2375 (insecure)
tcp://localhost:2376 (TLS)
```
- Network-accessible Docker API
- Used for remote management
- **MARS uses TCP in dev** (localhost:9088 for mars-dev)

---

## MARS Docker Architecture

**MARS uses 2 Docker configurations**:

::::: {.columns}
:::: {.column width="48%"}

**Production** (Sysbox):
```
DOCKER_HOST=unix:///var/run/docker.sock
DOCKER_RUNTIME=sysbox-runc
```

**Benefits**:
- System Docker daemon
- Sysbox security isolation
- Standard workflow

**Use Case**:
- Research deployments
- Multi-user environments
- Classified networks

::::
:::: {.column width="48%"}

**Development** (mars-dev):
```
DOCKER_HOST=tcp://localhost:9088
DOCKER_RUNTIME=sysbox-runc
```

**Benefits**:
- Isolated from system Docker
- Won't interfere with host
- Safe for experimentation

**Use Case**:
- Building MARS itself
- Testing infrastructure
- Parallel dev environments

::::
:::::

**Key Point**: Same Sysbox runtime, different daemon endpoints

---

## Docker Image Caching: Sysbox Behavior

**Challenge**: Sysbox uses **per-container** image stores

**Standard Docker** (shared cache):
```
/var/lib/docker/
├── image/          # All containers share images
├── overlay2/       # Shared layers
└── containers/     # Container-specific data
```
**Sysbox** (isolated cache):
```
/var/lib/sysbox/
├── container-1/
│   └── var/lib/docker/  # Container 1's images
├── container-2/
│   └── var/lib/docker/  # Container 2's images (duplicate!)
└── container-3/
    └── var/lib/docker/  # Container 3's images (duplicate!)
```

**Implication**: Each Sysbox container has **own Docker image cache**

---

## Image Caching: MARS Optimization

**Problem**: 3 containers × 2 GB images = 6 GB storage waste

**MARS Solution**: Strategic image caching

**Approach 1: Pre-pull in Host**:
```bash
# On host (before creating Sysbox containers)
docker pull python:3.11-slim
docker pull node:20-alpine
docker pull postgres:15

# Sysbox containers inherit from /var/lib/docker/
# (via sysbox-fs mount magic)
```

**Approach 2: Shared Volume** (experimental):
```yaml
# docker-compose.yml
services:
  mars-dev:
    runtime: sysbox-runc
    volumes:
      - docker-cache:/var/lib/docker:ro  # Read-only shared cache
```

**Approach 3: Build Once, Run Many**:
```bash
# Build MARS images on host
docker build -t mars/litellm:latest -f litellm/Dockerfile .

# Sysbox containers can docker pull from host registry
# (if registry is accessible)
```

**Current MARS Status**: Uses Approach 1 (pre-pull) + periodic cleanup

---

## Sysbox vs. Rootless Docker: Comparison

| Feature | **Sysbox** (MARS) | **Rootless Docker** |
|---------|-------------------|---------------------|
| **Setup Complexity** | ✅ Simple (install runtime) | ❌ Complex (daemon setup) |
| **Docker-in-Docker** | ✅ Full support | ⚠️ Limited |
| **Systemd Support** | ✅ Yes | ❌ No |
| **Privileged Ports** | ✅ Yes (remapped) | ❌ No (>1024 only) |
| **UID Mapping** | ✅ Automatic | ⚠️ Manual config |
| **Image Caching** | ⚠️ Per-container | ✅ Shared |
| **Security** | ✅ Strong isolation | ✅ Strong isolation |
| **Multi-User** | ✅ Works well | ⚠️ Per-user daemon |

**Why MARS chose Sysbox**: Simpler setup, full Docker features, better multi-user

---

## Sysbox in MARS: Practical Example

**Scenario**: Running MARS development environment (E6)

**Without Sysbox** (privileged container):
```bash
docker run --privileged \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mars/dev:latest

# ⚠️ Container can:
# - Access host Docker daemon (full control)
# - Escape to host via vulnerabilities
# - Read/write host filesystem
```

**With Sysbox** (MARS approach):
```bash
docker run --runtime=sysbox-runc \
  mars/dev:latest

# ✅ Container can:
# - Run Docker inside (isolated daemon)
# - Use systemd (process manager)
# - Feel like full system
#
# ❌ Container cannot:
# - Access host Docker daemon
# - Break out to host
# - See other containers' data
```

**Security Gain**: **Defense in depth** without functionality loss

---

# Git Submodules

---

## The Dependency Management Challenge

**MARS has 2 types of dependencies**:

**1. Research Project Dependencies** (outward):
- How do research projects **use** MARS?
- Where does MARS code live in research repos?
- How to update MARS version?

**2. MARS Internal Dependencies** (inward):
- How does MARS **use** external tools (LiteLLM, GitLab MCP, Zotero)?
- How to version-control external dependencies?
- How to ensure reproducible builds?

**Solution**: Git submodules (both directions)

---

## What are Git Submodules?

**Git Submodule**: A git repository embedded inside another git repository

**Visual Concept**:
```
Main Repository (research-project/)
├── .git/                 # Main repo's git metadata
├── src/
│   ├── algorithms/       # Your research code
│   └── framework/        # MARS (git submodule)
│       ├── .git/         # MARS's git metadata (pointer)
│       └── core/         # MARS source code
└── .gitmodules           # Submodule configuration
```

**Key Properties**:
- **Specific commit**: Submodule tracks exact MARS version (e.g., commit abc123)
- **Independent history**: MARS and research-project have separate git histories
- **Reproducible**: `git clone --recursive` gets exact versions

---

## Git Submodules: How Research Projects Use MARS

![Git Submodules - Research Project](diagrams/png/git-submodules-research.png){ width=85% }

**Research Project Structure**:
```
battery-research/                    # Your research repository
├── .git/
├── .gitmodules                      # Defines MARS submodule
├── src/
│   ├── framework/                   # MARS (git submodule)
│   │   ├── core/
│   │   ├── modules/
│   │   └── bin/mars                 # MARS CLI
│   └── battery_sim/                 # Your research code
├── data/                            # Your research data
├── results/                         # Your experiment results
└── README.md
```

**.gitmodules file**:
```ini
[submodule "src/framework"]
    path = src/framework
    url = https://github.com/nasa/mars-v2.git
    branch = v1.0
```

**Setup** (one-time):
```bash
git submodule add https://github.com/nasa/mars-v2.git src/framework
git commit -m "Add MARS framework as submodule"
```

---

## Submodules: Research Project Workflow

**Initial Clone** (new team member):
```bash
# Clone research project
git clone https://gitlab.example.com/research/battery-sim.git
cd battery-sim

# Initialize submodules (gets MARS)
git submodule update --init --recursive

# Result: src/framework/ now contains MARS
```

**Update MARS Version**:
```bash
# Navigate to MARS submodule
cd src/framework

# Pull latest MARS changes
git pull origin main

# Return to research project
cd ../..

# Commit updated MARS version
git add src/framework
git commit -m "Update MARS to v1.1"
```

**Benefit**: Research project tracks **exact MARS version** (reproducible results)

---

## Git Submodules: How MARS Uses External Dependencies

![Git Submodules - MARS Dependencies](diagrams/png/git-submodules-mars.png){ width=85% }

**MARS Repository Structure**:
```
mars-v2/                             # MARS repository
├── .git/
├── .gitmodules                      # Defines 5 external dependencies
├── core/
├── modules/
├── external/                        # External dependencies (submodules)
│   ├── litellm/                     # Git submodule → LiteLLM fork
│   ├── gitlab-mcp/                  # Git submodule → GitLab MCP fork
│   ├── zotero-selfhost/             # Git submodule → Zotero Docker
│   ├── claude-extractor/            # Git submodule → Session exporter
│   └── generic-infra/               # Git submodule → Infrastructure patterns
└── bin/
```

**Why Submodules for External Dependencies?**
- ✅ **Version locking**: MARS tracks exact commit of each dependency
- ✅ **Reproducible builds**: `git clone --recursive` gets everything
- ✅ **Offline development**: All dependencies in one clone
- ✅ **Fork management**: MARS uses forks with custom patches

---

## MARS External Dependencies

**5 External Repositories** (all managed as submodules):

| Dependency | Type | Purpose | Fork? |
|------------|------|---------|-------|
| **LiteLLM** | Python/Docker | AI gateway (AskSage/CAPRA) | ✅ Yes (AskSage provider) |
| **GitLab MCP** | Node.js MCP | 79 GitLab tools | ✅ Yes (fixes/features) |
| **Zotero Server** | Docker Compose | Self-hosted Zotero | ❌ No (upstream) |
| **Zotero MCP** | Python MCP | Literature mgmt tools | ✅ Yes (10 tools) |
| **Claude Extractor** | Python CLI | CCC session export | ❌ No (upstream) |
| **Generic Infra** | Patterns | Reusable infra templates | ✅ Yes (extracted from MARS) |

**Setup**:
```bash
# One command gets all dependencies
git clone --recursive https://github.com/nasa/mars-v2.git
```

---

## Submodules: MARS Update Workflow

**Update External Dependency**:

**Scenario**: LiteLLM releases new version with bug fixes

**Workflow**:
```bash
# Navigate to submodule
cd external/litellm

# Check current commit
git log --oneline -1
# Output: abc123 Add AskSage provider support

# Pull upstream changes
git fetch origin
git merge origin/main

# Test changes
cd ../..
pytest tests/test_litellm_integration.py

# Commit updated submodule
git add external/litellm
git commit -m "Update LiteLLM to v1.2.3 (bug fixes)"
```

**Benefit**: Controlled dependency updates, full testing before integration

---

## Submodules vs. Package Managers

**Why not use pip/npm/docker pull?**

| Approach | **Git Submodules** | **Package Managers** |
|----------|-------------------|---------------------|
| **Offline** | ✅ Works (bundled) | ❌ Needs internet |
| **Reproducibility** | ✅ Exact commit | ⚠️ Version ranges |
| **Custom Patches** | ✅ Easy (fork) | ❌ Hard (patch files) |
| **Air-Gap** | ✅ Full support | ❌ Requires registry |
| **Version Lock** | ✅ Explicit commit | ⚠️ Lock files (can drift) |
| **Security Review** | ✅ Full source visible | ⚠️ Binary/compiled |

**MARS Choice**: Submodules for **critical dependencies**, package managers for **libraries**

**Example**:
- `external/litellm/` → **Submodule** (custom AskSage provider)
- `pip install requests` → **Package manager** (standard library)

---

## Submodules: Common Workflows

**1. Initial Setup** (new MARS deployment):
```bash
git clone --recursive https://github.com/nasa/mars-v2.git
cd mars-v2
./mars-dev/scripts/setup-external-deps.sh
```

**2. Update All Submodules**:
```bash
git submodule update --remote --merge
```

**3. Check Submodule Status**:
```bash
git submodule status
# Output shows commit hash and branch for each submodule
```

**4. Work on Submodule** (develop patch):
```bash
cd external/litellm
git checkout -b fix/asksage-streaming
# Make changes, test, commit
git push origin fix/asksage-streaming
# Return to MARS, update submodule reference
cd ../..
git add external/litellm
git commit -m "Update LiteLLM with AskSage streaming fix"
```

---

## Submodules: Best Practices (MARS Approach)

**1. Pin to Specific Commits** (not branches):
```bash
# Good: Reproducible
cd external/litellm
git checkout abc123  # Specific commit
cd ../..
git add external/litellm

# Avoid: Can change unexpectedly
git submodule update --remote  # Pulls latest, may break
```

**2. Test Before Updating**:
```bash
# Update submodule
cd external/litellm && git pull

# Run tests
cd ../.. && pytest tests/test_litellm_*.py

# Only commit if tests pass
git add external/litellm && git commit -m "..."
```

**3. Document Dependencies**:
```yaml
# external-dependencies.yaml
dependencies:
  litellm:
    type: git-submodule
    path: external/litellm
    commit: abc123
    purpose: AskSage/CAPRA AI gateway
    status: Production
```

---

## Submodules: MARS Dependency Graph

```
Research Project (battery-sim)
    ↓ (git submodule)
MARS v2 (mars-v2)
    ↓ (5 git submodules)
    ├── LiteLLM (AI gateway)
    ├── GitLab MCP (project mgmt)
    ├── Zotero MCP (literature)
    ├── Zotero Server (self-hosted)
    └── Generic Infra (patterns)
```

**Reproducibility Chain**:
1. Research project pins MARS commit (e.g., v1.0.2)
2. MARS pins dependency commits (LiteLLM abc123, GitLab xyz789)
3. `git clone --recursive` = **exact versions, always**

**Air-Gap Capability**:
- Single clone = all dependencies (no network needed)
- Tarball distribution = fully offline installation
- Security review = all source code visible

---

## Submodules: Troubleshooting

**Problem 1**: Submodule not initialized
```bash
# Symptom: external/litellm/ is empty
# Fix:
git submodule update --init --recursive
```

**Problem 2**: Submodule detached HEAD
```bash
# Symptom: (HEAD detached at abc123)
# Fix (if you want to track a branch):
cd external/litellm
git checkout main
git pull
cd ../..
git add external/litellm
```

**Problem 3**: Merge conflicts in submodule
```bash
# Symptom: Conflict in submodule pointer
# Fix:
cd external/litellm
git status  # See what's conflicting
# Resolve, then:
cd ../..
git add external/litellm
```

---

# Summary: Technical Implementation

---

## Technical Choices: Recap

**1. Git Worktrees**: **40-60% faster** parallel development
- 5-25 concurrent CCC sessions
- No context switching
- E8 sprint orchestration

**2. AskSage + LiteLLM**: **Vendor independence**
- DoD classified AI access
- Fallback to Anthropic/Ollama
- Zero code changes to swap providers

**3. Sysbox Runtime**: **Secure containerization**
- Docker-in-Docker without privileged mode
- UID/GID isolation automatic
- Full systemd support

**4. Git Submodules**: **Reproducible builds**
- Exact dependency versions
- Air-gap capable
- Offline development

**Result**: Research-grade platform with DoD-level security

---

## MARS Architecture: Three-Layer System

**Separation of Concerns**

::::: {.columns}
:::: {.column width="30%"}

### mars-rt
**Runtime CLI**

**Purpose**: Run research projects

**Users**: Research teams

**Commands**:
- `mars up` - Deploy services
- `mars agents list`
- `mars services info`

**Location**: Production/research environments

::::
:::: {.column width="30%"}

### mars-dev
**Development CLI**

**Purpose**: Build MARS itself

**Users**: MARS developers

**Commands**:
- `mars-dev up` - Start E6 container
- `mars-dev build`
- `mars-dev doctor`

**Location**: E6 dev container

::::
:::: {.column width="30%"}

### mars-user-plugin
**Personal Customization**

**Purpose**: Customize dev environment

**Users**: Individual developers

**Capabilities**:
- Dotfiles (.vimrc, .bashrc)
- Custom scripts
- IDE configs
- Lifecycle hooks

**Location**: `external/mars-user-plugin/`

::::
:::::

---

## mars-user-plugin: Developer Experience Layer

**Problem**: Every developer has different preferences

**Solution**: Plugin system for personal customization

**Key Features**:

1. **Auto-Mount System**: Drop files → auto-mounted in E6 container
   ```
   external/mars-user-plugin/
   └── mounted-files/
       └── root/
           ├── .vimrc    (660 → rw mount)
           └── .bashrc   (640 → ro mount)
   ```

2. **Lifecycle Hooks**: Hook into mars-dev events
   - `pre-up.sh` - Before container starts
   - `container-startup.sh` - During startup
   - `post-build.sh` - After build completes

3. **Git-Tracked**: Personal configs tracked in separate repo
   - Share across MARS deployments
   - Version control your dev environment
   - Zero impact on mars-v2 repository

---

## Three-Layer Relationship

```
┌─────────────────────────────────────────────────────────┐
│  mars-user-plugin (Personal Layer)                      │
│  ├─ Developer dotfiles (.vimrc, .bashrc, .tmux.conf)   │
│  ├─ Custom scripts & tools                              │
│  └─ IDE configurations                                  │
├─────────────────────────────────────────────────────────┤
│  mars-dev (Development Layer)                           │
│  ├─ E6 Docker-in-Docker container                       │
│  ├─ Build infrastructure (mars-dev build)               │
│  ├─ Testing & validation                                │
│  └─ Claude Code CLI workspace                           │
├─────────────────────────────────────────────────────────┤
│  mars-rt (Runtime Layer)                                │
│  ├─ Research project deployment                         │
│  ├─ Agent orchestration                                 │
│  ├─ Service management                                  │
│  └─ Production operations                               │
└─────────────────────────────────────────────────────────┘
```

**Key Principle**: Clean separation
- **mars-rt**: What research teams use
- **mars-dev**: How we build MARS
- **mars-user-plugin**: How each developer personalizes their workflow

---

## mars-user-plugin: Quick Start

**5-Minute Setup**

```bash
# 1. Clone plugin template
cp -r external/mars-user-plugin-template ~/dev/mars-user
cd ~/dev/mars-user

# 2. Add your dotfiles
cp ~/.vimrc mounted-files/root/.vimrc
chmod 660 mounted-files/root/.vimrc  # rw mount

# 3. Register with mars-dev
cd ~/dev/mars-v2
mars-dev register-plugin ~/dev/mars-user

# 4. Rebuild E6 container
mars-dev down
mars-dev build --no-cache
mars-dev up -d

# 5. Your dotfiles are now in E6!
mars-dev exec bash
vim  # Uses your .vimrc configuration
```

**Benefits**:
- ✅ Personal preferences without polluting mars-v2
- ✅ Share configs across MARS deployments
- ✅ Version control your dev environment
- ✅ Zero learning curve (just drop files)

---

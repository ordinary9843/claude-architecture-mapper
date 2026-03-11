# Claude Architecture Mapper

[![Claude Code Auditor](https://img.shields.io/badge/Claude_Code_Auditor-Grade_A-success?style=flat-square&logo=anthropic&logoColor=white)](https://github.com/ordinary9843/claude-code-auditor)

Tells you what's actually installed in your Claude Code environment — and draws it. Scans every plugin, skill, agent, and command across `~/.claude/` and your current project, detects trigger collisions and semantic overlaps, and writes a structured `ARCHITECTURE.md` with a live Mermaid dependency graph.

Most Claude Code setups grow organically until nobody knows what's installed or what conflicts with what. This plugin makes your full environment visible in a single command.

## Installation

You can install this plugin either directly within Claude Code or via your standard terminal.

### 1. Inside Claude Code (Recommended)

```shell
/plugin marketplace add https://github.com/ordinary9843/claude-architecture-mapper.git
/plugin install architecture-mapper@claude-architecture-mapper
```

### 2. Via Standard Terminal

```shell
claude plugin marketplace add https://github.com/ordinary9843/claude-architecture-mapper.git
claude plugin install architecture-mapper@claude-architecture-mapper
```

*Note: Restart Claude Code after installation to ensure the plugin loads correctly.*

## How It Works

Run from any directory — no arguments needed:

```text
/architecture-mapper:map   →  scan environment and write ARCHITECTURE.md
```

The skill scans both scopes simultaneously:

- **Global scope** (`~/.claude/`): all installed plugins, cached skills, agents, and commands
- **Project scope** (current directory): project-local agents, skills, commands, rules, memory, and CLAUDE.md

It reads only frontmatter and metadata — never executes or acts on the content of scanned files.

### What Gets Scanned

| Artifact | Glob Patterns |
|----------|--------------|
| Skills | `~/.claude/skills/**/SKILL.md`, `~/.claude/plugins/cache/**/skills/**/SKILL.md`, `skills/**/SKILL.md` |
| Agents | `~/.claude/agents/*.md`, `~/.claude/plugins/cache/**/agents/*.md`, `agents/*.md`, `.claude/agents/*.md` |
| Commands | `~/.claude/commands/*.md`, `~/.claude/plugins/cache/**/.claude/commands/*.md`, `.claude/commands/*.md` |
| Rules | `.claude/rules/*.md` |
| Memory | `MEMORY.md` |
| Config | `CLAUDE.md` |

### Output — `ARCHITECTURE.md`

The skill creates or updates `ARCHITECTURE.md` in the current directory with five sections:

1. **Ecosystem Inventory** — every component with type, source plugin, trigger, model, and size
2. **Collision Report** — overlapping components ranked by severity (🔴 Critical / 🟡 Warning / 🔵 Info)
3. **Ecosystem Health** — component count, collision count, bloat alerts
4. **Recommendations** — top 3 actionable improvements
5. **Visual Map** — Mermaid graph between `<!-- START_METAMAP -->` markers (safe to re-run; only that section is replaced)

## Usage Examples

### 1. Map Your Full Environment

```shell
/architecture-mapper:map
```

**Example output (`ARCHITECTURE.md` excerpt):**

```text
## Ecosystem Inventory

| Name          | Type    | Source Plugin              | Trigger  | Model | Size | Governance   |
|---------------|---------|----------------------------|----------|-------|------|--------------|
| map           | Skill   | claude-architecture-mapper | —        | —     | 6 KB | 🔒 no-invoke |
| review        | Skill   | claude-code-auditor        | —        | —     | 4 KB | 🔒 no-invoke |
| commit        | Command | global                     | /commit  | —     | 2 KB | —            |

## Collision Report

None detected.

## Ecosystem Health

| Metric              | Value | Status |
|---------------------|-------|--------|
| Total Components    | 3     | —      |
| Installed Plugins   | 2     | —      |
| Collision Count     | 0     | 🟢     |
| Bloat Alerts (>8KB) | 0     | 🟢     |
```

### 2. Detect Trigger Conflicts

When two installed components claim the same slash command, the Collision Report flags it:

```text
## Collision Report

| Component A                    | Component B             | Reason              | Severity    |
|--------------------------------|-------------------------|---------------------|-------------|
| review (claude-code-auditor)   | review (superpowers)    | Same trigger /review | 🔴 Critical |
```

**Recommendation generated:** Rename one trigger to eliminate the conflict.

## Understanding the Graph

The Mermaid graph is auto-scaled based on node count:

| Total nodes | Direction | Context nodes | Grouping    |
|-------------|-----------|---------------|-------------|
| ≤ 15        | `graph TD` | Included      | By type     |
| 16–25       | `graph LR` | Omitted       | By type     |
| > 25        | `graph LR` | Omitted       | By plugin   |

Node types use distinct colors: skills (green), agents (blue), commands (orange), context (purple), memory (red).

## Plugin Architecture

```text
claude-architecture-mapper/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest (name: architecture-mapper)
│   └── marketplace.json         # Marketplace definition
├── skills/
│   └── map/
│       ├── SKILL.md             # Core map skill
│       ├── references/
│       │   ├── mermaid-rules.md # Mermaid syntax constraints
│       │   └── doctor-rules.md  # Diagnostic thresholds and health rules
│       └── examples/
│           ├── 01-small-environment.md   # Happy path: 2 skills + 1 command
│           ├── 02-collision-detected.md  # Trigger collision scenario
│           └── 03-no-artifacts.md        # Edge case: empty environment
├── CLAUDE.md                    # Plugin context loaded at session start
├── LICENSE                      # MIT License
└── README.md
```

## Requirements & Troubleshooting

### Prerequisites

- [Claude Code CLI](https://code.claude.com) must be installed.

### Common Issues

**1. The plugin is not loading**

Run the built-in validate command to check for errors:

```shell
claude plugin validate .
claude plugin list
```

**2. The skill is not available**

If you don't see `/architecture-mapper:map` when typing `/help`:
- Make sure you have restarted Claude Code after installation.
- Confirm the plugin installed successfully: `claude plugin list`

**3. `~/.claude/` not found**

The skill handles this gracefully — it skips the global scope scan and notes "Global scope unavailable" in the Ecosystem Health table. Only the project scope is scanned.

## Contributing

We welcome community improvements!

1. Clone this repository to your local machine.
2. Add the marketplace locally: `claude plugin marketplace add .`
3. Install the local plugin: `claude plugin install architecture-mapper@claude-architecture-mapper`
4. Run the skill to establish a baseline: `/architecture-mapper:map`
5. Submit a PR with a description of your changes.

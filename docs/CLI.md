# CLI Reference

## Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `-v`, `--version` | Enable verbose mode | `false` |

---

## Commands

### `extract` (alias: `e`)

Extract organization data from GitHub API and save it to a YAML file.

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `-o`, `--orgs` | No | List of organization names to extract data from | — |
| `-f`, `--file` | No | Output YAML file path | `./github_management.yaml` |

```bash
github-management extract -o my-org
github-management extract -o org1 org2 -f output.yaml
```

---

### `diff` (alias: `d`)

Show differences between a local YAML file and the current GitHub state.

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `-o`, `--orgs` | Yes | List of organization names to diff against | — |
| `-f`, `--file` | No | Input YAML file path to compare | `./github_management.yaml` |

```bash
github-management diff -o my-org
github-management diff -o org1 org2 -f custom.yaml
```

---

### `validate` (alias: `v`)

Validate YAML file syntax and data consistency.

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `-f`, `--file` | No | YAML file path to validate | `./github_management.yaml` |

```bash
github-management validate
github-management validate -f custom.yaml
```

---

### `push` (alias: `p`)

Push data modifications from a YAML file. Requires a **scope** sub-command (`org` or `user`), then a **target** sub-command.

#### Common Options (shared by all push sub-commands)

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `-f`, `--file` | No | Input YAML file path | `./github_management.yaml` |
| `--dry-run` | No | Simulate changes without applying them | `false` |

---

#### `push org`

Push **organization-level** data (teams, members, topics, etc.).

##### `push org topics`

Push repository **topics** modifications for organizations.

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `--repo-filter` | No | Filter repositories by name/pattern (supports wildcards) | `None` (all repos) |
| `-o`, `--orgs` | No | List of organization names to push topics to | `None` (all orgs in YAML) |

```bash
github-management push org topics
github-management push org topics --repo-filter "api-*"
github-management push -f custom.yaml --dry-run org topics -o my-org
```

---

##### `push org teams`

Push **teams** modifications (members, inheritance, roles, repo access).

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `--team-filter` | No | Filter teams by name/pattern (supports wildcards) | `None` (all teams) |
| `-o`, `--orgs` | No | List of organization names to push teams to | `None` (all orgs in YAML) |

```bash
github-management push org teams
github-management push org teams --team-filter "backend-*"
github-management push --dry-run org teams -o my-org --team-filter "core-team"
```

---

##### `push org cleanup`

Cleanup organization members. Requires **exactly one** of the two mutually exclusive options below.

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `--auto-delete-inactive` | One of the two | Auto delete users that no longer exist on GitHub | — |
| `--remove-member` | One of the two | Remove specific members from the organization (everywhere) | — |

> **Note:** `--auto-delete-inactive` and `--remove-member` are **mutually exclusive** — you must use one or the other, not both.

```bash
github-management push org cleanup --auto-delete-inactive
github-management push org cleanup --remove-member user1 user2
github-management push --dry-run org cleanup --auto-delete-inactive
```

---

#### `push user`

Push **user-level** data (repositories, topics, etc.).

##### `push user topics`

Push repository **topics** modifications for the user account.

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `--repo-filter` | No | Filter repositories by name/pattern (supports wildcards) | `None` (all repos) |

```bash
github-management push user topics
github-management push user topics --repo-filter "my-project-*"
github-management push --dry-run user topics --repo-filter "my-repo"
```

---

##### `push user cleanup`

Cleanup user repository members. Requires **exactly one** of the two mutually exclusive options below.

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `--auto-delete-inactive` | One of the two | Auto delete users that no longer exist on GitHub | — |
| `--remove-member` | One of the two | Remove specific members from the repositories (everywhere) | — |

> **Note:** `--auto-delete-inactive` and `--remove-member` are **mutually exclusive** — you must use one or the other, not both.

```bash
github-management push user cleanup --auto-delete-inactive
github-management push user cleanup --remove-member user1 user2
github-management push --dry-run user cleanup --auto-delete-inactive
```

---

### `create` (alias: `c`)

Create GitHub elements from a YAML configuration file. Requires a **sub-command** to specify what to create.

#### Common Options (shared by all create sub-commands)

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `--dry-run` | No | Simulate changes without applying them | `false` |

---

#### `create repo` (alias: `r`)

Create a repository in the user account using a template repository.

| Option | Required | Description | Default |
|--------|----------|-------------|---------|
| `-f`, `--file` | No | Input YAML configuration file path | `./create_repository_config.yaml` |

```bash
github-management create repo
github-management create repo -f my-repo-config.yaml
github-management create --dry-run repo -f my-repo-config.yaml
```

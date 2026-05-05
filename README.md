# envdiff

> CLI tool to diff `.env` files across environments and flag missing or mismatched variables.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/youruser/envdiff.git
cd envdiff
pip install .
```

---

## Usage

Compare two `.env` files and see what's missing or different:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DEBUG
  - REDIS_URL

Mismatched values:
  DATABASE_URL
    development: postgres://localhost/myapp_dev
    production:  postgres://prod-host/myapp_prod
```

### Options

| Flag | Description |
|------|-------------|
| `--only-missing` | Show only variables missing from the second file |
| `--only-mismatched` | Show only variables with differing values |
| `--quiet` | Exit with non-zero code if differences found (useful in CI) |

```bash
# CI usage — fails the pipeline if envs are out of sync
envdiff .env.example .env --quiet
```

---

## License

This project is licensed under the [MIT License](LICENSE).
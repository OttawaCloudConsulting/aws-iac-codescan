# Checkov Kubernetes Scanning

## Overview

- [Checkov Kubernetes Scanning](#checkov-kubernetes-scanning)
  - [Overview](#overview)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Rendered Manifests with Kustomize](#rendered-manifests-with-kustomize)
  - [Output Artifacts](#output-artifacts)
  - [Logging](#logging-1)
  - [Project Structure](#project-structure)
  - [Development Notes](#development-notes)


This tool provides static analysis for Kubernetes configuration files using [Checkov](https://github.com/bridgecrewio/checkov). It is designed to support security and compliance scanning within modern GitOps, Kustomize, and Crossplane-based infrastructure-as-code environments.

The tool can be executed as a standalone CLI script and is optimized for mono-repository setups. It supports both raw Kubernetes manifests and fully rendered manifests generated from Kustomize overlays. Scan results are output in both machine-readable JSON and human-readable Markdown formats, with detailed policy violation summaries.

Key use cases include:

- Validating Kubernetes YAML for security and policy compliance before deployment.
- Rendering and scanning manifests from `kustomization.yaml`-based projects.
- Generating audit-ready Markdown reports for infrastructure reviews.
- Integrating scanning into CI/CD pipelines using structured output.

The tool is built to be easily extendable, portable, and compatible with a variety of development and production environments.

## Features

### Checkov Integration

- Leverages Checkov to scan Kubernetes manifests for misconfigurations, policy violations, and security risks.
- Supports both raw manifest files and fully rendered output from Kustomize.

### Kustomize Rendering

- Detects and renders Kustomize-based configurations using `kustomize build`.
- Supports both base and overlay directories for flexible deployments.
- Allows scanning of rendered output only, avoiding false positives from non-resource files like `kustomization.yaml`.

### Markdown Summary Reports

- Automatically generates human-readable summaries of scan results.
- Includes failed check details with file paths, resources, severity levels, and remediation links.
- Saves output to timestamped Markdown files for audit and collaboration.

### JSON Output

- Stores structured Checkov scan results in standard JSON format.
- Enables integration with CI/CD pipelines, dashboards, or reporting tools.

### Command-Line Interface

- Provides a clear and flexible CLI interface with support for:
  - `--target` directory
  - `--render` and `--render-only`
  - `--dry-run` mode
  - `--debug` logging

### Logging & Diagnostics

- Built-in logging with environment or CLI override (`LOG_LEVEL`, `--debug`).
- Outputs structured logs for easier debugging and automation.

### Environment Bootstrapping

- Provides shell scripts (`env_setup.sh`) for setting up dependencies across APT, YUM, and Homebrew-based systems.
- Ensures consistent environment setup regardless of platform.

### Modular & Extensible

- Designed as a modular Python application.
- Easy to extend with additional scan formats, integrations, or post-processing logic.

## Requirements

### Supported Operating Systems

- Linux (Debian, Ubuntu, RHEL/CentOS)
- macOS (Intel or Apple Silicon)

### Python

- Python 3.10 or higher (3.10–3.13 are supported)

### Required Tools & Dependencies

The following tools must be installed on the system or will be installed by the provided environment setup scripts:

- [Checkov](https://github.com/bridgecrewio/checkov)
- [Kustomize](https://github.com/kubernetes-sigs/kustomize)
- [Git](https://git-scm.com/)
- [curl](https://curl.se/)
- [wget](https://www.gnu.org/software/wget/)
- [Python venv module](https://docs.python.org/3/library/venv.html)

### Optional Runtime Dependencies

These will be required if rendering manifests or bootstrapping via the CLI:

- `env_setup.sh` and corresponding OS-specific scripts (`install_env_apt.sh`, `install_env_yum.sh`, `install_env_brew.sh`)
- Internet access (for initial dependency installation)

### Permissions

- User must have permission to install system packages if using setup scripts
- Script is safe to run as a non-root user (assumes local environment setup)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/kubernetes-code-analysis-tool.git
cd kubernetes-code-analysis-tool
```

### 2. Run the Environment Setup Script

```bash
chmod +x env_setup.sh
./env_setup.sh
```

The script will detect your operating system and package manager, then install all required dependencies.

### 3. (Optional) Activate Python Virtual Environment

If `VENV=true` is set inside `env_setup.sh`, a Python virtual environment will be created and activated.

### 4. Install Python Dependencies (If Any)

Currently, this tool does not require external Python packages beyond the standard library. If future features require them, install using:

```bash
pip install -r requirements.txt
```

---

## Usage

### Basic Syntax

```bash
python scan.py --target <path-to-directory>
```

### Common Examples

#### Scan a directory of plain Kubernetes manifests

```bash
python scan.py --target ./my-k8s-configs
```

#### Render and scan a Kustomize-based directory

```bash
python scan.py --render --target ./overlays/dev
```

#### Render only (no scan)

```bash
python scan.py --render-only --target ./overlays/dev
```

#### Dry run to see which YAML files will be scanned

```bash
python scan.py --dry-run --target ./my-k8s-configs
```

#### Enable verbose logging

```bash
python scan.py --debug --target ./my-k8s-configs
```

### Output

- JSON results: `checkov_output/results_json.json`
- Markdown summary: `checkov_output/CHECKOV_SUMMARY_<timestamp>.md`
- (If rendered): `rendered_output/manifest.yaml`

### Logging

- Default level: `WARNING`
- Set via CLI: `--debug`
- Set via env var: `LOG_LEVEL=INFO`

---

## Rendered Manifests with Kustomize

### Purpose

Many Kubernetes projects use Kustomize to manage overlays and configurations. Kustomize files (`kustomization.yaml`) are not valid Kubernetes manifests and should not be scanned directly. Instead, the tool renders them into a single manifest file before scanning.

### How It Works

- If `--render` is provided, the tool runs:

  ```bash
  kustomize build <target-directory>
  ```

- The output is saved as `rendered_output/manifest.yaml`
- Checkov then scans this file instead of the original directory

### Example

```bash
python scan.py --render --target ./application-sets/argocd
```

This will:

- Detect and build overlays using Kustomize
- Output a single manifest file to `rendered_output/`
- Scan that rendered file with Checkov

### When to Use

- Always use `--render` when your target includes a `kustomization.yaml`
- For overlays, you may also target paths like `./overlays/dev`

### Best Practices

- Avoid scanning raw directories containing Kustomize configurations without `--render`
- Use `--render-only` for testing generated output before full scans
- Keep Kustomize version consistent across environments

---

## Output Artifacts

### Output Directory Structure

All artifacts generated by the tool are written to the local working directory in timestamped or static subfolders.

```
./
├── checkov_output/
│   ├── results_json.json
│   └── CHECKOV_SUMMARY_<timestamp>.md
├── rendered_output/
│   └── manifest.yaml
```

### JSON Output

- File: `checkov_output/results_json.json`
- Format: Standard Checkov JSON output
- Use: Machine-readable results for dashboards, CI/CD, or auditing

### Markdown Summary

- File: `checkov_output/CHECKOV_SUMMARY_<timestamp>.md`
- Format: Structured and human-readable
- Includes:
  - Scan timestamp
  - Total passed, failed, skipped, and parsing errors
  - Checkov version
  - Detailed list of failed policies

### Rendered Manifest (Kustomize Only)

- File: `rendered_output/manifest.yaml`
- Format: Fully rendered Kubernetes YAML from `kustomize build`
- Use: Debugging, validation, and Checkov scan input

### Cleanup Notes

- Output directories are not automatically removed between runs.
- You may want to periodically clean up `checkov_output/` and `rendered_output/` manually or via automation if needed.

---

## Logging

### Logging Behavior

Logging is enabled by default and outputs messages to standard output. The log level determines how much information is displayed.

### Default Level

- `WARNING`: Only warnings, errors, and critical issues are shown.

### Controlling Log Level

You can change the log level using:

#### 1. Command-Line Option

```bash
--debug
```

This enables verbose output for troubleshooting (sets level to `DEBUG`).

#### 2. Environment Variable

```bash
export LOG_LEVEL=INFO
```

Accepted levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Log Level Precedence

If both `--debug` and `LOG_LEVEL` are set:

- The `--debug` flag takes precedence and overrides the environment value.

### Logging Format

```
[LEVEL] message text
```

Example:

```
[INFO] Checkov scan completed with no policy violations.
[WARNING] Checkov completed with violations (exit code 1).
```

### Recommendations

- Use `--debug` during development or troubleshooting.
- Set `LOG_LEVEL` in CI/CD environments for consistent verbosity.
- Avoid `DEBUG` level in production unless actively debugging.

---

## Project Structure

The project is organized to support modular development and environment-specific installations.

### Root Directory

```
./
├── scan.py                      # Main CLI entry point
├── env_setup.sh                # Entry-point for environment detection and bootstrap
├── install_env_apt.sh          # APT-based installation script
├── install_env_yum.sh          # YUM-based installation script
├── install_env_brew.sh         # Homebrew installation script (macOS)
├── checkov_output/             # Generated scan outputs (JSON and Markdown)
├── rendered_output/            # Rendered manifests from kustomize
├── requirements.txt            # Placeholder for future Python dependencies
└── README.md                   # Project documentation
```

### Additional Notes

- All install scripts define reusable functions for per-tool installation
- The Python code adheres to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Future enhancements may introduce subdirectories for tests, plugins, or custom policies

---

## Development Notes

### Coding Standards

- All Python code follows the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Logging is preferred over `print()` statements for all output
- Functions should be type-annotated where appropriate

### Testing

- Manual testing can be done by running `scan.py` with various flag combinations
- Example targets should be created in a test directory (e.g., `test/manifests`) for integration scenarios
- Future work may introduce `pytest` or GitHub Actions

### Shell Scripts

- Use shared function names across `install_env_*.sh` for compatibility with `env_setup.sh`
- Scripts should only install missing dependencies (no bulk installs)
- `env_setup.sh` should auto-detect OS and call the appropriate installer

### Feature Flags

- `--render` and `--render-only` determine whether manifests are preprocessed
- `--dry-run` displays matched files without executing scans
- Logging verbosity controlled by `--debug` and `LOG_LEVEL`

### Known Limitations

- Does not yet support recursive rendering of multiple Kustomize overlays
- Assumes `kustomize` and `checkov` are installed and in `$PATH`
- Assumes working directory permissions for creating output folders

### Future Improvements

- Add test suite for core logic
- Validate YAML schema pre-scan
- Add support for Checkov custom policies and baseline suppression
- Output performance benchmarking (scan duration, file count)

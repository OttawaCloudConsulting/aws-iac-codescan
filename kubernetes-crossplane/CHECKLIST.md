# Development Checklist – Checkov Analysis Tool

## 1. Environment Setup

- [x] Create shell script(s) to install prerequisites:
  - [x] `install_env_apt.sh` – for APT-based systems
  - [x] `install_env_yum.sh` – for YUM-based systems
  - [x] `install_env_brew.sh` – for macOS Homebrew
- [x] Each script should:
  - [x] Check for Python 3.9+ and install if missing
  - [x] Install `pip`, `virtualenv`, and `checkov`
  - [x] Install optional tools: `kustomize`, `kubectl`, `helm`
- [ ] Provide instruction to activate Python virtual environment

## 2. Project Directory Initialization

- [ ] Create base directory structure:

  ```
  .
  ├── scan.py (or scan.sh)
  ├── utils/
  ├── policies/
  ├── config/
  └── checkov_output/
  ```

- [x] Create `.gitignore`, `README.md`, and `LICENSE`
- [ ] Set up logging to stdout/stderr and optionally to file

## 3. Input Scanning Logic

- [ ] Implement CLI with:
  - [ ] Argument for input directory
  - [ ] Flags for dry-run, debug, render-only
- [ ] Validate directory exists and contains YAML manifests
- [ ] Add recursive discovery of manifests

## 4. Manifest Preprocessing (Optional)

- [ ] Detect and render with `kustomize build`
- [ ] Store rendered manifests in temp or defined directory
- [ ] (Optional) Add hooks for Helm, Crossplane or YTT rendering

## 5. Checkov Execution

- [ ] Run Checkov CLI against input/rendered directory
- [ ] Capture CLI output (human-readable)
- [ ] Capture JSON output (machine-readable)
- [ ] Support `--external-checks-dir` for future custom policy path

## 6. Output Management

- [ ] Generate timestamped output filenames
- [ ] Save TXT report to `checkov_output/report_<timestamp>.txt`
- [ ] Save JSON report to `checkov_output/report_<timestamp>.json`
- [ ] Optional: Save stderr or logs to file

## 7. Tool Modes

- [ ] `scan`: Full execution
- [ ] `render-only`: Preprocess manifests only
- [ ] `dry-run`: Print paths that would be scanned
- [ ] `debug`: Enable verbose logging

## 8. Testing & Validation

- [ ] Create test manifests under `/test`
- [ ] Ensure known issues are detected by Checkov
- [ ] Test rendering with Kustomize
- [ ] Validate CLI + JSON outputs

## 9. Documentation

- [ ] Add usage examples to `README.md`
- [ ] Include description of all modes and flags
- [ ] Describe installation script usage
- [ ] Add notes about adding custom policies

## 10. Future-Proofing

- [ ] Stub logic to support loading custom policies from `policies/`
- [ ] Embed Git commit and branch info in reports
- [ ] Add environment variable overrides for key paths

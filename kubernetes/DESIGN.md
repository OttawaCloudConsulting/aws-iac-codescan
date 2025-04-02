# Code Analysis Tool Design – Checkov-based

## Phase 1: Strategic Goals

### Primary Objective

Create a reusable, script-based tool (Python or Bash) to **scan Kubernetes code** (including Crossplane XRDs/Claims and regular manifests) in a **mono-repo**, outputting both **human-readable and machine-readable results**, with **future support for custom policies**.

---

## Phase 2: Core Design Principles

### 1. Directory Scanning Logic

- Target: `mono-repo/some/directory/`
- Recursively find and scan Kubernetes YAML manifests.
- Allow flag-based scoping to include/exclude:
  - Native manifests
  - Compositions/claims (for Crossplane)
  - Kustomize-built outputs

### 2. Manifest Preprocessing (Optional, but Modular)

- Detect and render:
  - `kustomize build` if `kustomization.yaml` is present.
  - Optional: `kubectl kustomize`, `ytt`, or `helm template`
- Output rendered YAMLs to a temporary folder to be scanned by Checkov.
- Enable logic to skip this phase if raw manifests are acceptable.

### 3. Scanning Engine

- Checkov CLI usage:

  ```bash
  checkov -d <path> --framework kubernetes
  ```

- For prebuilt output:

  ```bash
  --external-checks-dir <path>
  ```

- Output formats:
  - CLI (text) for human readability
  - JSON for automation pipelines, dashboards, or diffing

### 4. Output Management

- Save output with timestamped naming (e.g., `checkov_report_20240402.json`)
- Output paths configurable
- Save logs and failures separately (for CI/CD use)

### 5. Tool Modes

- `scan`: Run a full scan
- `render-only`: Just render Crossplane or Kustomize output
- `dry-run`: Check what would be scanned, without actual execution
- `debug`: Print more verbose logs

---

## Phase 3: Tool Architecture

```text
.
├── scan.py (or scan.sh)       # Main entrypoint
├── utils/
│   ├── renderer.py            # Kustomize, Crossplane, Helm support (optional)
│   └── output_writer.py       # Manage CLI + JSON output formats
├── policies/                  # (optional) custom policies
│   └── k8s/
├── config/
│   └── default.conf           # Optional: global config or path defaults
└── checkov_output/
    ├── checkov_report_20240402.json
    └── checkov_report_20240402.txt
```

## ✅ Required Tools & Packages

| Tool / Package       | Purpose                                  | Requirement         |
|----------------------|-------------------------------------------|---------------------|
| `python3 (>= 3.10)`  | Primary runtime for tool and Checkov      | **Required**        |
| `pip3`               | Python package installer                  | **Required**        |
| `virtualenv` or `venv` | Create isolated Python environment     | **Required**        |
| `checkov` (via pip)  | Static analysis tool                      | **Required**        |

---

## 🔄 Optional (Recommended for Preprocessing)

| Tool        | Purpose                                               | Notes |
|-------------|--------------------------------------------------------|-------|
| `kustomize` | Render Kubernetes overlays and bases                   | Useful if scanning overlays instead of raw manifests |
| `kubectl`   | Validate manifests or simulate rendering (less common) | Optional for advanced debugging or validation |
| `helm`      | Render Helm charts into Kubernetes manifests           | Needed only if Helm is added to your workflow |
| `jq`        | Parse or transform JSON reports                        | Helpful for CI scripts or JSON formatting |
| `git`       | Fetch metadata (commit hash, branch) for embedding     | Useful for traceability or audit tagging |


---

## Phase 4: Future Extensibility

| Feature                     | When to Add                            | Why                                             |
|----------------------------|----------------------------------------|--------------------------------------------------|
| **Custom Policies**        | When you need enforcement beyond built-in checks | Checkov supports Python or YAML-based checks    |
| **CI/CD Mode**             | Integrate with GitHub Actions, GitLab CI, Argo    | Block merge on failed policy                    |
| **Metadata Embed**         | Include Git branch, commit hash in report         | Useful for audit trail or dashboarding          |
| **Dashboard Export**       | Parse JSON → Ingest to Grafana/ELK               | For report visualization                        |
| **Crossplane Schema Awareness** | Validate claim to composition linkage    | Deeper Crossplane validation                    |

---

## Phase 5: Manual vs. Automated Triggers

- **Manual:** CLI script invoked by engineer
- **Scheduled:** Cron job or pipeline step scans and archives
- **Git Triggered:** CI pipeline triggered on code push or PR

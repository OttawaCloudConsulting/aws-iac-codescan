"""CLI interface for scanning Kubernetes configuration directories using Checkov.

This script handles parsing command-line arguments, validates input paths,
recursively finds YAML files, supports dry-run and render-only modes,
and performs Checkov-based static analysis.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import json
from datetime import datetime
from typing import Any, List

def configure_logging(debug: bool = False) -> None:
    """Configures the logging level based on environment or debug flag.

    Args:
        debug (bool): If True, override everything with DEBUG level.
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    if debug:
        log_level = "DEBUG"

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="[%(levelname)s] %(message)s"
    )

def parse_args() -> argparse.Namespace:
    """Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Scan Kubernetes configuration directories using Checkov."
    )

    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Path to the directory containing Kubernetes manifests."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the files that would be scanned without running Checkov."
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output."
    )

    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Only perform preprocessing/rendering of manifests without scanning."
    )

    parser.add_argument(
        "--render",
        action="store_true",
        help="Render manifests before scanning."
    )

    return parser.parse_args()

def validate_target_directory(target_path: str) -> None:
    """Validates that the target directory exists and is a directory.

    Args:
        target_path (str): Path to validate.

    Raises:
        SystemExit: If the path is invalid.
    """
    if not os.path.isdir(target_path):
        logging.error("Target directory '%s' does not exist or is not a directory.", target_path)
        sys.exit(1)

def find_yaml_files(base_path: str) -> List[str]:
    """Recursively finds all .yaml and .yml files in the given directory.

    Args:
        base_path (str): The root directory to start scanning.

    Returns:
        List[str]: List of full paths to YAML files found.
    """
    yaml_files = []
    for root, _, files in os.walk(base_path):
        for filename in files:
            if filename.endswith(('.yaml', '.yml')):
                full_path = os.path.join(root, filename)
                yaml_files.append(full_path)
    return yaml_files

def render_kustomize(target_path: str, debug: bool = False) -> str:
    """Renders a kustomize base or overlay to a temporary directory.

    Args:
        target_path (str): Path containing the kustomization.yaml
        debug (bool): Enable debug logging

    Returns:
        str: Path to rendered output file
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = os.path.join("rendered_output", f"render-{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "manifest.yaml")

    if not shutil.which("kustomize"):
        logging.error("'kustomize' not found in PATH. Please install it before using rendering features.")
        sys.exit(1)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            subprocess.run(
                ["kustomize", "build", target_path],
                check=True,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )
    except subprocess.CalledProcessError as error:
        logging.error("Kustomize rendering failed: %s", error.stderr)
        sys.exit(1)

    logging.debug("Rendered output saved to: %s", output_file)
    return output_file

def generate_summary_markdown(json_path: str, output_dir: str) -> None:
    """Generates a Markdown summary of Checkov scan results.

    Args:
        json_path (str): Path to Checkov results JSON file
        output_dir (str): Directory to write the summary Markdown file
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logging.error("Failed to read JSON report: %s", e)
        return

    failed_checks = data.get("results", {}).get("failed_checks", [])
    summary = data.get("summary", {})
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    summary_file = os.path.join(output_dir, f"CHECKOV_SUMMARY_{filename_timestamp}.md")

    with open(summary_file, "w", encoding="utf-8") as md:
        md.write("# Checkov Scan Summary\n\n")
        md.write("## Scan Metadata\n")
        md.write(f"- **Timestamp:** {timestamp}\n")
        md.write(f"- **Passed Checks:** {summary.get('passed', 0)}\n")
        md.write(f"- **Failed Checks:** {summary.get('failed', 0)}\n")
        md.write(f"- **Skipped Checks:** {summary.get('skipped', 0)}\n")
        md.write(f"- **Parsing Errors:** {summary.get('parsing_errors', 0)}\n")
        md.write(f"- **Resources Scanned:** {summary.get('resource_count', 0)}\n")
        md.write(f"- **Checkov Version:** {summary.get('checkov_version', 'N/A')}\n\n")

        if failed_checks:
            md.write("## Failed Checks Detail\n\n")
            for check in failed_checks:
                md.write(f"### {check.get('check_id', 'UNKNOWN')} - {check.get('check_name', 'Unnamed Check')}\n")
                md.write(f"- **File:** `{check.get('file_path', 'unknown')}`\n")
                md.write(f"- **Resource:** `{check.get('resource', 'unknown')}`\n")
                severity = check.get('severity') or "N/A"
                md.write(f"- **Severity:** {severity}\n")
                guideline = check.get('guideline')
                if guideline:
                    md.write(f"- **Guideline:** [{guideline}]({guideline})\n")
                md.write("\n")

    logging.info("Summary Markdown generated: %s", summary_file)

def run_checkov_scan(scan_path: str, debug: bool = False) -> None:
    """Runs Checkov on the given directory or file, outputting JSON only.

    Args:
        scan_path (str): Path to scan (file or directory)
        debug (bool): Enable debug logging
    """
    output_dir = "checkov_output"
    os.makedirs(output_dir, exist_ok=True)
    json_file = os.path.join(output_dir, "results_json.json")

    scan_flag = "--file" if os.path.isfile(scan_path) else "--directory"

    cmd = [
        "checkov",
        "--framework", "kubernetes",
        "--quiet",
        "--compact",
        "--soft-fail",
        scan_flag, scan_path,
        "--output", "json",
        "--output-file-path", output_dir,
    ]

    result = subprocess.run(
        cmd,
        stderr=subprocess.STDOUT,
        text=True
    )

    if result.returncode == 0:
        logging.info("Checkov scan completed with no policy violations.")
    else:
        logging.warning("Checkov completed with violations (exit code %s).", result.returncode)

    logging.info("JSON Report: %s", json_file)
    generate_summary_markdown(json_file, output_dir)

def main() -> None:
    """Main entry point for the CLI tool."""
    args = parse_args()
    configure_logging(debug=args.debug)
    validate_target_directory(args.target)

    logging.debug("Arguments parsed: %s", vars(args))

    if args.render_only:
        output_path = render_kustomize(args.target, debug=args.debug)
        logging.info("Render-only mode complete. Output saved to: %s", output_path)
        sys.exit(0)

    if args.render:
        rendered_manifest = render_kustomize(args.target, debug=args.debug)
        run_checkov_scan(rendered_manifest, debug=args.debug)
        sys.exit(0)

    yaml_files = find_yaml_files(args.target)

    if args.dry_run:
        logging.info("[DRY RUN] YAML files discovered:")
        for path in yaml_files:
            logging.info("  %s", path)
        logging.info("[DRY RUN] Total: %d file(s)", len(yaml_files))
        sys.exit(0)

    run_checkov_scan(args.target, debug=args.debug)

if __name__ == "__main__":
    main()


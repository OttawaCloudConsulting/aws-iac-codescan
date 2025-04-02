"""CLI interface for scanning Kubernetes configuration directories using Checkov.

This script handles parsing command-line arguments, validates input paths,
recursively finds YAML files, supports dry-run and render-only modes,
and performs Checkov-based static analysis.
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Any, List

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
        print(f"ERROR: Target directory '{target_path}' does not exist or is not a directory.")
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
        print("ERROR: 'kustomize' not found in PATH. Please install it before using rendering features.")
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
        print("ERROR: Kustomize rendering failed:")
        print(error.stderr)
        sys.exit(1)

    if debug:
        print(f"[DEBUG] Rendered output saved to: {output_file}")

    return output_file

def run_checkov_scan(scan_path: str, debug: bool = False) -> None:
    """Runs Checkov on the given directory or file.

    Args:
        scan_path (str): Path to scan (file or directory)
        debug (bool): Enable debug logging
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = "checkov_output"
    os.makedirs(output_dir, exist_ok=True)
    txt_file = os.path.join(output_dir, f"checkov_report_{timestamp}.txt")
    json_file = os.path.join(output_dir, f"checkov_report_{timestamp}.json")

    scan_flag = "--file" if os.path.isfile(scan_path) else "--directory"

    cmd = [
        "checkov",
        "--framework", "kubernetes",
        scan_flag, scan_path,
        "--output", "json",
        "--output-file-path", json_file,
    ]

    try:
        with open(txt_file, "w", encoding="utf-8") as txt_out:
            subprocess.run(
                cmd,
                check=True,
                stdout=txt_out,
                stderr=subprocess.STDOUT,
                text=True
            )
        print(f"✅ Checkov scan completed.\nTXT Report: {txt_file}\nJSON Report: {json_file}")
    except subprocess.CalledProcessError as error:
        print("ERROR: Checkov scan failed.")
        print(error)
        sys.exit(1)

def main() -> None:
    """Main entry point for the CLI tool."""
    args = parse_args()
    validate_target_directory(args.target)

    if args.debug:
        print("[DEBUG] Arguments parsed:")
        for key, value in vars(args).items():
            print(f"  {key}: {value}")

    if args.render_only:
        output_path = render_kustomize(args.target, debug=args.debug)
        print(f"✅ Render-only mode complete. Output saved to: {output_path}")
        sys.exit(0)

    if args.render:
        rendered_manifest = render_kustomize(args.target, debug=args.debug)
        run_checkov_scan(rendered_manifest, debug=args.debug)
        sys.exit(0)

    yaml_files = find_yaml_files(args.target)

    if args.dry_run:
        print("[DRY RUN] YAML files discovered:")
        for path in yaml_files:
            print(f"  {path}")
        print(f"[DRY RUN] Total: {len(yaml_files)} file(s)")
        sys.exit(0)

    run_checkov_scan(args.target, debug=args.debug)

if __name__ == "__main__":
    main()


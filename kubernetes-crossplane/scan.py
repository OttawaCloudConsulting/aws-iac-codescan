"""CLI interface for scanning Kubernetes configuration directories using Checkov.

This script handles parsing command-line arguments and validates input paths.
"""

import argparse
import os
import sys
from typing import Any

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

def main() -> None:
    """Main entry point for the CLI tool."""
    args = parse_args()
    validate_target_directory(args.target)

    if args.debug:
        print("[DEBUG] Arguments parsed:")
        for key, value in vars(args).items():
            print(f"  {key}: {value}")

    print("CLI argument parsing and validation complete.")

if __name__ == "__main__":
    main()
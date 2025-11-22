#!/usr/bin/env python3
"""
OSRM Preprocessing Script with MD5 Validation and Conditional Downloading

This script:
1. Checks remote MD5 hash against local file
2. Downloads latest OSM data if needed
3. Runs OSRM preprocessing pipeline (extract, partition, customize)
"""

import os
import sys
import hashlib
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional
from datetime import timedelta
from time import time


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_step(step: str) -> None:
    """Print a step message."""
    print(f"→ {step}")


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    return (
        str(timedelta(seconds=int(seconds))).lstrip("0:").lstrip("0")
        if int(seconds) >= 3600
        else str(timedelta(seconds=int(seconds)))
    )


def get_remote_md5(url: str) -> Optional[str]:
    """Fetch remote MD5 hash from URL."""
    try:
        print_step(f"Fetching remote MD5 from {url}")
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode().strip()
            # Extract hash from "hash filename" format
            md5_hash = content.split()[0]
            print(f"  Remote MD5: {md5_hash}")
            return md5_hash
    except Exception as e:
        print(f"✗ Error fetching remote MD5: {e}", file=sys.stderr)
        return None


def get_local_md5(filepath: str) -> Optional[str]:
    """Calculate MD5 hash of local file."""
    try:
        md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"✗ Error calculating local MD5: {e}", file=sys.stderr)
        return None


def download_with_progress(url: str, dest: str) -> bool:
    """Download file with progress bar."""
    try:
        print_step(f"Downloading from {url}")

        def progress_hook(block_num, block_size, total_size):
            """Simple progress indicator."""
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(
                    f"  [{percent:3d}%] {mb_downloaded:.1f}MB / {mb_total:.1f}MB",
                    end="\r",
                )

        urllib.request.urlretrieve(url, dest, progress_hook)
        print(f"  [100%] Download complete!             ")
        return True
    except Exception as e:
        print(f"\n✗ Error downloading file: {e}", file=sys.stderr)
        return False


def run_docker_command(
    command: list, data_dir: str, command_name: str = ""
) -> tuple[bool, float]:
    """Run a Docker command with error handling and time tracking.

    Returns:
        tuple[bool, float]: (success, duration_in_seconds)
    """
    try:
        env = os.environ.copy()
        env["OSRM_DATA"] = data_dir

        print_step(f"Running: {' '.join(command)}")
        start_time = time()
        result = subprocess.run(command, env=env, check=False, capture_output=False)
        duration = time() - start_time

        if result.returncode != 0:
            print(
                f"✗ Command failed with return code {result.returncode}",
                file=sys.stderr,
            )
            return False, duration

        if command_name:
            print(f"✓ {command_name} completed in {format_duration(duration)}")
        return True, duration
    except Exception as e:
        print(f"✗ Error running command: {e}", file=sys.stderr)
        return False, 0.0


def main() -> int:
    # """Main execution flow."""
    # print_section("OSRM Data Preprocessing")

    # # Configuration
    osrm_data = os.environ.get("OSRM_DATA")
    if not osrm_data:
        print("✗ OSRM_DATA environment variable not set", file=sys.stderr)
        return 1

    osrm_data = Path(osrm_data)
    osrm_data.mkdir(parents=True, exist_ok=True)

    remote_md5_url = (
        "https://download.geofabrik.de/south-america/brazil-latest.osm.pbf.md5"
    )
    pbf_url = "https://download.geofabrik.de/south-america/brazil-latest.osm.pbf"
    pbf_file = osrm_data / "brazil-latest.osm.pbf"
    md5_file = osrm_data / "brazil-latest.osm.pbf.md5"

    # Step 1: Fetch remote MD5
    print_section("Step 1: Checking for updates")
    remote_md5 = get_remote_md5(remote_md5_url)
    if not remote_md5:
        print("✗ Failed to fetch remote MD5. Aborting.")
        return 1

    # Step 2: Check local file
    print_step("Checking local file")
    local_md5 = get_local_md5(str(pbf_file)) if pbf_file.exists() else None

    if local_md5:
        print(f"  Local MD5:  {local_md5}")
    else:
        print(f"  Local file not found")

    # Step 3: Compare and decide
    print_section("Step 2: Validation")
    if local_md5 and local_md5.lower() == remote_md5.lower():
        print("✓ Files are up-to-date! No download needed.")
        print(f"  Using existing: {pbf_file}")
        return 0
    else:
        print("✗ Files differ or local file missing. Downloading latest version...")

        print_section("Step 3: Downloading data")
        if not download_with_progress(pbf_url, str(pbf_file)):
            return 1

        # Verify downloaded file
        print_section("Step 4: Verifying download")
        print_step("Calculating MD5 of downloaded file")
        new_md5 = get_local_md5(str(pbf_file))

        if not new_md5:
            print("✗ Failed to calculate MD5 of downloaded file", file=sys.stderr)
            return 1

        if new_md5.lower() == remote_md5.lower():
            print(f"✓ Downloaded file verified successfully")
            # Save MD5 for future reference
            with open(md5_file, "w") as f:
                f.write(f"{remote_md5} {pbf_file.name}\n")
        else:
            print(f"✗ MD5 mismatch after download!", file=sys.stderr)
            print(f"  Expected: {remote_md5}", file=sys.stderr)
            print(f"  Got:      {new_md5}", file=sys.stderr)
            return 1

    # Step 5: Run OSRM preprocessing
    print_section("Step 5: OSRM Preprocessing")

    commands = [
        (
            [
                "docker",
                "run",
                "--rm",
                "-t",
                "-v",
                f"{osrm_data}:/data",
                "ghcr.io/project-osrm/osrm-backend:latest",
                "osrm-extract",
                "-p",
                "/data/profiles/car_avoid.lua",
                "/data/brazil-latest.osm.pbf",
            ],
            "osrm-extract",
        ),
        (
            [
                "docker",
                "run",
                "--rm",
                "-t",
                "-v",
                f"{osrm_data}:/data",
                "ghcr.io/project-osrm/osrm-backend:latest",
                "osrm-partition",
                "/data/brazil-latest.osrm",
            ],
            "osrm-partition",
        ),
        (
            [
                "docker",
                "run",
                "--rm",
                "-t",
                "-v",
                f"{osrm_data}:/data",
                "ghcr.io/project-osrm/osrm-backend:latest",
                "osrm-customize",
                "/data/brazil-latest.osrm",
            ],
            "osrm-customize",
        ),
    ]

    total_time = 0.0
    for i, (cmd, cmd_name) in enumerate(commands, 1):
        print(f"\nCommand {i}/{len(commands)}:")
        cmd_time = 0.0
        success, duration = run_docker_command(cmd, str(osrm_data), cmd_name)
        if not success:
            print(f"\n✗ Preprocessing failed at command {i}", file=sys.stderr)
            return 1
        total_time += duration
        cmd_time += duration
        print(f"  Command {i} ({cmd_name}) completed in {format_duration(duration)}")

    print_section(
        f"✓ Preprocessing complete! Total time: {format_duration(total_time)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

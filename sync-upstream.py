#!/usr/bin/env python3
"""
AI Agent Skills Central Hub - Upstream Sync Engine
Author: feishu/skillshub
Description: Synchronize and track official skill updates without overwriting custom skills.
"""

import os
import sys
import json
import shutil
import subprocess
import argparse

HUB_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(HUB_DIR, "skills-manifest.json")
CACHE_DIR = os.path.join(HUB_DIR, ".cache")

def load_manifest():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Error: Manifest file not found at {MANIFEST_FILE}")
        sys.exit(1)
    with open(MANIFEST_FILE, "r") as f:
        return json.load(f)

def check_upstreams(manifest):
    print("==================================================")
    print("  Checking Upstream Repositories for Updates")
    print("==================================================")
    upstreams = manifest.get("upstreams", {})
    results = []

    for name, info in upstreams.items():
        repo = info["repo"]
        branch = info.get("branch", "main")
        print(f"Checking {name:18} ({repo})...", end="", flush=True)
        try:
            cmd = f"git ls-remote {repo} refs/heads/{branch}"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
            if res.returncode == 0 and res.stdout.strip():
                remote_head = res.stdout.strip().split()[0]
                results.append((name, branch, remote_head[:7], "Available"))
                print(f" [OK] Latest: {remote_head[:7]}")
            else:
                results.append((name, branch, "N/A", "Timeout/Auth"))
                print(f" [Failed: {res.stderr.strip()[:40]}]")
        except subprocess.TimeoutExpired:
            results.append((name, branch, "Timeout", "Network timeout"))
            print(" [Timeout]")
        except Exception as e:
            results.append((name, branch, "Error", str(e)))
            print(f" [Error: {e}]")

    print("\nSummary:")
    print(f"{'Source':18} {'Branch':8} {'Remote Commit':14} {'Status'}")
    print("-" * 55)
    for name, branch, head, status in results:
        print(f"{name:18} {branch:8} {head:14} {status}")
    print("-" * 55)

def sync_upstream_repo(name, info, manifest):
    repo = info["repo"]
    branch = info.get("branch", "main")
    sub_dir = info.get("skills_dir", "")
    os.makedirs(CACHE_DIR, exist_ok=True)
    target_cache = os.path.join(CACHE_DIR, name)

    print(f"\n---> Syncing upstream: {name} ({repo})")
    if not os.path.exists(os.path.join(target_cache, ".git")):
        print(f"Cloning {name} (depth 1)...")
        cmd = f"git clone --depth 1 -b {branch} {repo} {target_cache}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error cloning {repo}: {res.stderr}")
            return False
    else:
        print(f"Pulling latest changes for {name}...")
        res = subprocess.run("git fetch --depth 1 && git reset --hard origin/" + branch, shell=True, cwd=target_cache, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error fetching {name}: {res.stderr}")
            return False

    # Locate skills in cache
    search_root = os.path.join(target_cache, sub_dir) if sub_dir else target_cache
    if not os.path.exists(search_root):
        search_root = target_cache

    protected = set(manifest.get("custom_protected", []))
    updated_count = 0

    # Scan for skills in the cloned repo
    for root, dirs, files in os.walk(search_root):
        if "SKILL.md" in files:
            skill_name = os.path.basename(root)
            # Check if this skill belongs to this upstream in manifest or starts with prefix
            mapped_source = manifest.get("skills", {}).get(skill_name, {}).get("source")
            if skill_name in protected:
                print(f"  [Protected] Skipping custom skill: {skill_name}")
                continue

            if mapped_source == name or skill_name in manifest.get("skills", {}):
                dest_path = os.path.join(HUB_DIR, skill_name)
                os.makedirs(dest_path, exist_ok=True)
                for f in files:
                    shutil.copy2(os.path.join(root, f), os.path.join(dest_path, f))
                for d in dirs:
                    src_d = os.path.join(root, d)
                    dst_d = os.path.join(dest_path, d)
                    shutil.copytree(src_d, dst_d, dirs_exist_ok=True)
                updated_count += 1

    print(f"Successfully synced {updated_count} skills from {name}!")
    return True

def main():
    parser = argparse.ArgumentParser(description="AI Agent Skills Central Hub Upstream Sync")
    parser.add_argument("--check", action="store_true", help="Check upstream repositories for updates without modifying files")
    parser.add_argument("--all", action="store_true", help="Sync all registered upstreams")
    parser.add_argument("source", nargs="?", help="Specific upstream to sync (e.g. gstack, samber-golang, superpowers)")

    args = parser.parse_args()
    manifest = load_manifest()

    if args.check:
        check_upstreams(manifest)
        return

    if args.all:
        for name, info in manifest.get("upstreams", {}).items():
            sync_upstream_repo(name, info, manifest)
        print("\nAll upstreams synchronized!")
        print("Run 'git status' and 'git diff' in ~/.skillshub to review changes.")
        return

    if args.source:
        upstreams = manifest.get("upstreams", {})
        if args.source not in upstreams:
            print(f"Error: Unknown source '{args.source}'. Registered sources: {list(upstreams.keys())}")
            sys.exit(1)
        sync_upstream_repo(args.source, upstreams[args.source], manifest)
        print("\nSync completed! Run 'git status' and 'git diff' to review changes.")
        return

    parser.print_help()

if __name__ == "__main__":
    main()

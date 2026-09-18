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

# Helper to get SSH url for GitHub if needed
def get_git_urls(url):
    urls = [url]
    if url.startswith("https://github.com/"):
        ssh_url = url.replace("https://github.com/", "git@github.com:")
        urls.append(ssh_url)
    return urls

def load_manifest():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Error: Manifest file not found at {MANIFEST_FILE}")
        sys.exit(1)
    with open(MANIFEST_FILE, "r") as f:
        return json.load(f)

def run_git_with_fallback(cmd_template, url, cwd=None):
    urls = get_git_urls(url)
    last_err = ""
    for u in urls:
        cmd = cmd_template.format(url=u)
        try:
            res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=20)
            if res.returncode == 0:
                return True, res.stdout.strip(), u
            last_err = res.stderr.strip()
        except subprocess.TimeoutExpired:
            last_err = "Timeout"
        except Exception as e:
            last_err = str(e)
    return False, last_err, urls[0]

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
        cmd_template = f"git ls-remote {{url}} refs/heads/{branch}"
        success, out, used_url = run_git_with_fallback(cmd_template, repo)
        if success and out:
            remote_head = out.split()[0]
            results.append((name, branch, remote_head[:7], "Available"))
            print(f" [OK] Latest: {remote_head[:7]}")
        else:
            results.append((name, branch, "N/A", out[:20]))
            print(f" [Failed: {out[:30]}]")

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
    
    # 1. Clone or pull
    if not os.path.exists(os.path.join(target_cache, ".git")):
        print(f"Cloning {name} (depth 1)...")
        cmd_template = f"git clone --depth 1 -b {branch} {{url}} {target_cache}"
        success, out, used_url = run_git_with_fallback(cmd_template, repo)
        if not success:
            print(f"Error cloning {repo}: {out}")
            return False
    else:
        print(f"Pulling latest changes for {name}...")
        res = subprocess.run(f"git fetch --depth 1 origin {branch} && git reset --hard origin/{branch}", 
                             shell=True, cwd=target_cache, capture_output=True, text=True)
        if res.returncode != 0:
            # Try re-cloning
            print(f"Re-cloning {name} due to fetch error...")
            shutil.rmtree(target_cache, ignore_errors=True)
            cmd_template = f"git clone --depth 1 -b {branch} {{url}} {target_cache}"
            success, out, used_url = run_git_with_fallback(cmd_template, repo)
            if not success:
                print(f"Error re-cloning {name}: {out}")
                return False

    # 2. Locate skills in cache
    search_root = os.path.join(target_cache, sub_dir) if sub_dir else target_cache
    if not os.path.exists(search_root):
        search_root = target_cache

    protected = set(manifest.get("custom_protected", []))
    updated_count = 0

    # Prune list of ignored directories
    ignore_dirs = {'.git', '.github', '.cache', 'node_modules', 'test', 'tests', 'fixtures', 
                   '.hermes', '.kiro', '.factory', '.agents', '.claude', '.gemini', '.cursor', 
                   '.codex', 'bin', 'docs', 'extension', 'lib', 'supabase', 'browser-skills'}

    for root, dirs, files in os.walk(search_root):
        # In-place modify dirs to avoid descending into git or test directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        
        # NEVER treat the repository root itself as a skill!
        if os.path.abspath(root) == os.path.abspath(target_cache):
            continue

        if "SKILL.md" in files:
            skill_name = os.path.basename(root)
            if skill_name in protected:
                print(f"  [Protected] Skipping custom skill: {skill_name}")
                continue

            # Only update if skill is tracked in manifest under this source or in manifest
            mapped_source = manifest.get("skills", {}).get(skill_name, {}).get("source")
            if mapped_source == name or skill_name in manifest.get("skills", {}):
                dest_path = os.path.join(HUB_DIR, skill_name)
                os.makedirs(dest_path, exist_ok=True)
                
                # Copy skill files
                for f in files:
                    if f.startswith(".git"):
                        continue
                    shutil.copy2(os.path.join(root, f), os.path.join(dest_path, f))
                
                # Copy skill subdirs (like agents/, scripts/, references/, sections/)
                for d in dirs:
                    if d in ignore_dirs or d.startswith("."):
                        continue
                    src_d = os.path.join(root, d)
                    dst_d = os.path.join(dest_path, d)
                    shutil.copytree(src_d, dst_d, dirs_exist_ok=True, 
                                    ignore=shutil.ignore_patterns('.git*', '__pycache__', '*.pack', '*.idx'))
                
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

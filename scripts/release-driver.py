#!/usr/bin/env python3
"""Prepare, publish, and verify an Astria plugin release."""

import argparse
import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "astriaai/skills"
WORKFLOW = "plugin.yml"
BRANCH = "main"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
ALLOWED_RELEASE_FILES = {
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
}
ALLOWED_RELEASE_PREFIXES = ("plugins/astria/",)


class ReleaseError(RuntimeError):
    pass


def run(arguments, *, capture=False):
    print(f"+ {shlex.join(str(argument) for argument in arguments)}", flush=True)
    completed = subprocess.run(
        [str(argument) for argument in arguments],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )
    return completed.stdout.strip() if capture else ""


def git(*arguments, capture=False):
    return run(("git", *arguments), capture=capture)


def require_command(name):
    if shutil.which(name) is None:
        raise ReleaseError(f"required command is not installed: {name}")


def changed_files():
    tracked = git("diff", "--name-only", "--", capture=True).splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard", capture=True).splitlines()
    return sorted(set(tracked + untracked))


def is_release_file(path):
    return path in ALLOWED_RELEASE_FILES or path.startswith(ALLOWED_RELEASE_PREFIXES)


def require_release_scope(paths):
    unexpected = [path for path in paths if not is_release_file(path)]
    if unexpected:
        raise ReleaseError(f"release preparation changed unexpected files: {', '.join(unexpected)}")


def require_clean_checkout():
    status = git("status", "--porcelain", "--untracked-files=all", capture=True)
    if status:
        raise ReleaseError("commit or remove existing worktree changes before publishing:\n" + status)
    branch = git("branch", "--show-current", capture=True)
    if branch != BRANCH:
        raise ReleaseError(f"release from {BRANCH}, not {branch or 'detached HEAD'}")


def require_main_matches_origin():
    if git("rev-parse", "HEAD", capture=True) != git("rev-parse", f"origin/{BRANCH}", capture=True):
        raise ReleaseError(f"local {BRANCH} must exactly match origin/{BRANCH}")


def require_newer_version(version):
    current = json.loads((ROOT / "plugins" / "astria" / "plugin.json").read_text(encoding="utf-8"))["version"]
    current_core = tuple(int(part) for part in current.split("-", 1)[0].split("+", 1)[0].split("."))
    requested_core = tuple(int(part) for part in version.split("-", 1)[0].split("+", 1)[0].split("."))
    if requested_core <= current_core:
        raise ReleaseError(f"release version must be newer than {current}: {version}")


def require_unreleased(version):
    tag = f"v{version}"
    local_tag = subprocess.run(
        ["git", "rev-parse", "--quiet", "--verify", f"refs/tags/{tag}"],
        cwd=ROOT,
        capture_output=True,
    )
    if local_tag.returncode == 0:
        raise ReleaseError(f"tag already exists: {tag}")


def find_tag_run(runs, tag):
    return next((run_data for run_data in runs if run_data["headBranch"] == tag), None)


def wait_for_tag_run(commit, tag, timeout_seconds=120):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        runs = json.loads(
            run(
                (
                    "gh",
                    "run",
                    "list",
                    "--repo",
                    REPOSITORY,
                    "--workflow",
                    WORKFLOW,
                    "--commit",
                    commit,
                    "--event",
                    "push",
                    "--limit",
                    "20",
                    "--json",
                    "databaseId,headBranch,status,conclusion,url",
                ),
                capture=True,
            )
        )
        tagged_run = find_tag_run(runs, tag)
        if tagged_run:
            return tagged_run
        time.sleep(3)
    raise ReleaseError(f"timed out waiting for the {tag} GitHub Actions run")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checksum_digest(path):
    fields = path.read_text(encoding="utf-8").strip().split()
    if len(fields) < 2 or not re.fullmatch(r"[0-9a-f]{64}", fields[0]):
        raise ReleaseError(f"invalid checksum file: {path}")
    return fields[0]


def verify_release(version):
    tag = f"v{version}"
    archive_name = f"astria-{version}.zip"
    checksum_name = f"{archive_name}.sha256"
    release = json.loads(
        run(("gh", "release", "view", tag, "--repo", REPOSITORY, "--json", "assets,url"), capture=True)
    )
    asset_names = {asset["name"] for asset in release["assets"]}
    missing = {archive_name, checksum_name} - asset_names
    if missing:
        raise ReleaseError(f"GitHub release is missing assets: {', '.join(sorted(missing))}")

    with tempfile.TemporaryDirectory(prefix="astria-release-verify-") as directory:
        run(
            (
                "gh",
                "release",
                "download",
                tag,
                "--repo",
                REPOSITORY,
                "--pattern",
                archive_name,
                "--pattern",
                checksum_name,
                "--dir",
                directory,
            )
        )
        remote_archive = Path(directory) / archive_name
        remote_checksum = Path(directory) / checksum_name
        expected = checksum_digest(remote_checksum)
        if sha256(remote_archive) != expected:
            raise ReleaseError("published archive does not match its checksum")
        local_archive = ROOT / "dist" / archive_name
        if sha256(local_archive) != expected:
            raise ReleaseError("published archive differs from the locally validated archive")

    print(f"Verified {release['url']} ({expected})")


def prepare_release(version):
    run((ROOT / "scripts" / "release-plugin.sh", version))
    paths = changed_files()
    require_release_scope(paths)
    if not paths:
        raise ReleaseError("release preparation produced no changes")
    git("diff", "--check")
    untracked = git("ls-files", "--others", "--exclude-standard", capture=True).splitlines()
    if untracked:
        git("add", "--", *untracked)
    git("commit", "-m", f"Release Astria plugin v{version}", "--", *paths)
    tag = f"v{version}"
    git("tag", "-a", tag, "-m", f"Astria plugin {tag}")
    return git("rev-parse", "HEAD", capture=True), tag


def publish_release(version, skip_local_install):
    require_command("gh")
    require_command("git")
    if not skip_local_install:
        require_command("codex")

    require_clean_checkout()
    git("fetch", "origin", BRANCH, "--tags")
    require_main_matches_origin()
    require_newer_version(version)
    require_unreleased(version)
    run(("gh", "auth", "status", "--hostname", "github.com"))

    commit, tag = prepare_release(version)
    git("push", "--atomic", "origin", f"HEAD:{BRANCH}", f"refs/tags/{tag}")
    tagged_run = wait_for_tag_run(commit, tag)
    run(("gh", "run", "watch", str(tagged_run["databaseId"]), "--repo", REPOSITORY, "--exit-status"))
    verify_release(version)

    if skip_local_install:
        print("Skipped local Codex reinstall.")
    else:
        run(("codex", "plugin", "add", "astria@astria"))
        print("Local Codex plugin refreshed. Start a new task to load the released version.")

    print("OpenAI public-directory submission and publication remain manual:")
    print("https://platform.openai.com/plugins")


def dry_run(version, skip_local_install):
    require_command("git")
    require_clean_checkout()
    require_main_matches_origin()
    require_newer_version(version)
    require_unreleased(version)
    run((ROOT / "scripts" / "validate-plugin.py",))
    print(f"Dry run passed for v{version}.")
    print("Publish would prepare metadata, commit explicit release files, create and atomically push the tag,")
    print("wait for GitHub Actions, verify release assets and checksum, and refresh the local Codex plugin.")
    if skip_local_install:
        print("Local Codex reinstall would be skipped.")


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="semantic version without the v prefix")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="run non-mutating preflight checks")
    mode.add_argument("--publish", action="store_true", help="commit, tag, push, and verify the release")
    parser.add_argument(
        "--skip-local-install",
        action="store_true",
        help="do not reinstall astria@astria after the GitHub release succeeds",
    )
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    if not SEMVER.fullmatch(arguments.version):
        raise ReleaseError("version must be valid semver without a v prefix")
    if arguments.dry_run:
        dry_run(arguments.version, arguments.skip_local_install)
    else:
        publish_release(arguments.version, arguments.skip_local_install)


if __name__ == "__main__":
    try:
        main()
    except (ReleaseError, subprocess.CalledProcessError) as error:
        print(f"release-driver: {error}", file=sys.stderr)
        raise SystemExit(1)

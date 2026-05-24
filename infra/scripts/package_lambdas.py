from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def zip_dir(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()

    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_dir():
                continue
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            archive.write(path, path.relative_to(source))


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def package_api(repo_root: Path, build_root: Path, artifacts_dir: Path) -> Path:
    api_build = build_root / "api"
    clean_dir(api_build)

    run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        "--target",
        str(api_build),
        str(repo_root / "backend"),
        "mangum>=0.17.0",
    ])

    shutil.copy2(repo_root / "infra" / "lambda" / "api_handler.py", api_build / "api_handler.py")
    shutil.copy2(
        repo_root / "infra" / "lambda" / "runtime_services.py",
        api_build / "runtime_services.py",
    )

    destination = artifacts_dir / "api_lambda.zip"
    zip_dir(api_build, destination)
    return destination


def package_worker(repo_root: Path, build_root: Path, artifacts_dir: Path) -> Path:
    worker_build = build_root / "worker"
    clean_dir(worker_build)

    shutil.copy2(
        repo_root / "infra" / "lambda" / "worker_placeholder.py",
        worker_build / "worker_placeholder.py",
    )

    destination = artifacts_dir / "worker_lambda.zip"
    zip_dir(worker_build, destination)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Package mrisk Lambda artifacts.")
    parser.add_argument(
        "--artifacts-dir",
        default=None,
        help="Output artifact directory. Defaults to infra/terraform/dev/artifacts.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    build_root = repo_root / "infra" / ".build" / "lambda"
    artifacts_dir = (
        Path(args.artifacts_dir).resolve()
        if args.artifacts_dir
        else repo_root / "infra" / "terraform" / "dev" / "artifacts"
    )
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    api_zip = package_api(repo_root, build_root, artifacts_dir)
    worker_zip = package_worker(repo_root, build_root, artifacts_dir)

    print(f"Packaged API Lambda: {api_zip}")
    print(f"Packaged worker Lambda: {worker_zip}")


if __name__ == "__main__":
    main()

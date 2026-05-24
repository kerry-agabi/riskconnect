from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy built frontend assets to S3 and CloudFront.")
    parser.add_argument("--bucket", required=True, help="Frontend S3 bucket name.")
    parser.add_argument("--distribution-id", required=True, help="CloudFront distribution ID.")
    parser.add_argument("--dist-dir", default="frontend/dist", help="Frontend build directory.")
    args = parser.parse_args()

    dist_dir = Path(args.dist_dir).resolve()
    if not dist_dir.exists():
        raise SystemExit(f"Frontend dist directory not found: {dist_dir}")

    run([
        "aws",
        "s3",
        "sync",
        str(dist_dir),
        f"s3://{args.bucket}",
        "--delete",
        "--cache-control",
        "public,max-age=31536000,immutable",
    ])

    index_file = dist_dir / "index.html"
    if index_file.exists():
        run([
            "aws",
            "s3",
            "cp",
            str(index_file),
            f"s3://{args.bucket}/index.html",
            "--cache-control",
            "no-cache",
            "--content-type",
            "text/html",
        ])

    run([
        "aws",
        "cloudfront",
        "create-invalidation",
        "--distribution-id",
        args.distribution_id,
        "--paths",
        "/*",
    ])


if __name__ == "__main__":
    main()


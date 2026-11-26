"""Dual-track Python environment isolation check (compatible with Python 3.6.8 & Python 3.12+).

Compare both tracks:
1. Work track (global) : python scripts/verify_isolation.py
2. Lab track (isolated): uv run python scripts/verify_isolation.py
"""

import sys


def main():
    # Ensure UTF-8 output when piped in PowerShell on Windows Python 3.6+
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    exe = sys.executable
    ver = sys.version.split()[0]
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    print("=" * 70)
    print(f"Python Executable : {exe}")
    print(f"Python Version    : {ver}")
    print(f"Virtual Env       : {'YES (.venv isolated)' if in_venv else 'NO (System Global)'}")

    if sys.version_info[:2] == (3, 6) and not in_venv:
        print("Status            : [WORK TRACK OK] Global Python 3.6.8 is untouched!")
    elif sys.version_info >= (3, 12) and in_venv:
        import curl_cffi
        import httpx
        import pydantic

        print(
            f"Modern Stack      : httpx={httpx.__version__}, "
            f"curl_cffi={curl_cffi.__version__}, pydantic={pydantic.__version__}"
        )
        print("Status            : [LAB TRACK OK] Isolated Python 3.12 environment ready!")
    else:
        print("Status            : [INFO] Custom environment detected.")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""Run Playwright MCP on the CloakBrowser stealth Chromium.

Resolves the installed binary at every start, so a binary update needs no
config change. Usage: cloak-mcp [--headed] [extra playwright-mcp flags...]
"""

import json
import os
import shutil
import sys
from pathlib import Path

# cloak-update owns downloads; never fetch a binary during an MCP handshake.
os.environ.setdefault("CLOAKBROWSER_AUTO_UPDATE", "false")

from cloakbrowser import config as cloak_config  # noqa: E402
from cloakbrowser.download import ensure_binary  # noqa: E402

STATE_DIR = Path(os.environ.get("IPS_CLOAKBROWSER_HOME", Path.home() / ".local/share/ips-cloakbrowser"))
IDLE_TIMEOUT_MS = "600000"  # free a session's headless browser after 10 idle minutes


def main() -> None:
    argv = sys.argv[1:]
    headed = "--headed" in argv
    passthrough = [a for a in argv if a != "--headed"]

    # Drop the wrapper's fixed seed: with none, the binary draws a fresh
    # fingerprint per launch and the config file is identical for every session.
    stealth = [a for a in cloak_config.get_default_stealth_args() if not a.startswith("--fingerprint=")]
    if headed:
        stealth.append("--ignore-gpu-blocklist")
    launch = {
        "executablePath": ensure_binary(),
        "headless": not headed,
        "args": stealth,
        "ignoreDefaultArgs": getattr(cloak_config, "IGNORE_DEFAULT_ARGS", ["--enable-automation"]),
    }
    # Headless has no window, so a fixed desktop viewport stays coherent; headed tracks the real window.
    viewport = None if headed else getattr(cloak_config, "DEFAULT_VIEWPORT", {"width": 1920, "height": 947})
    config = {
        "browser": {
            "browserName": "chromium",
            "isolated": True,
            "launchOptions": launch,
            "contextOptions": {"viewport": viewport},
        },
        # Auto-named snapshots and screenshots stay out of the agent's repo.
        "outputDir": str(STATE_DIR / "output"),
        "outputMaxSize": 200 * 1024 * 1024,
    }

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = STATE_DIR / ("mcp-config-headed.json" if headed else "mcp-config.json")
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(config, indent=2) + "\n")
    os.replace(tmp, path)

    mcp = shutil.which("playwright-mcp")
    if not mcp:
        sys.exit("cloak-mcp: playwright-mcp not found on PATH; run the ips-cloakbrowser install script")
    os.execv(mcp, [mcp, "--config", str(path), "--idle-timeout", IDLE_TIMEOUT_MS, "--file-paths", "absolute", *passthrough])


if __name__ == "__main__":
    main()

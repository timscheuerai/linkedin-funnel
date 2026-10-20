#!/usr/bin/env python3
"""Shared helpers for linkedin-engage: the author's config and the OXYGEN CLI wrapper.

The config holds names and IDs, never credentials. Copy
`skills/linkedin-engage/config.example.json` to `.oxygen/linkedin-engage.json`
at the kit root (git-ignored) and fill it, or point LINKEDIN_ENGAGE_CONFIG at
another file. Every read goes through OXYGEN's managed LinkedIn scraper
(`scraper.*`, cookieless, no connected account), so the author's own LinkedIn
account and its limits are never touched. Nothing here posts, likes, follows,
connects or messages.
"""
import json, os, random, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # the kit root: scripts -> skill -> skills -> root
SKILL = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / ".oxygen" / "linkedin-engage.json"

SPENT = {"credits": 0.0}
_CONFIG = {}


def config():
    """The author's config, loaded once. Exits with a clear message when it is missing or unfilled."""
    if _CONFIG:
        return _CONFIG
    path = Path(os.environ.get("LINKEDIN_ENGAGE_CONFIG") or DEFAULT_CONFIG)
    if not path.exists():
        sys.exit(f"No config at {path}. Copy {SKILL / 'config.example.json'} there and fill it (see SKILL.md, setup).")
    c = json.loads(path.read_text())
    if not c.get("watchlist_table") or str(c["watchlist_table"]).startswith("YOUR") \
            or "YOUR-HANDLE" in str(c.get("my_profile_url") or "YOUR-HANDLE"):
        sys.exit(f"Fill watchlist_table and my_profile_url in {path} first.")
    c.setdefault("runs_dir", "context/research/engage/linkedin")
    c.setdefault("lanes", {})
    c.setdefault("niche_searches", [])
    c.setdefault("niche_min_reactions", 15)
    c.setdefault("thousands_separator", ",")
    c.setdefault("automated_comment_patterns", [])
    c.setdefault("extra_banned_words", [])
    _CONFIG.update(c)
    return _CONFIG


def runs_dir():
    return ROOT / config()["runs_dir"]


def slug_of(url):
    m = re.search(r"linkedin\.com/in/([^/?#]+)", url or "")
    return m.group(1).lower() if m else None


def me_slug():
    return slug_of(config().get("my_profile_url"))


def cli(args, max_chars=None):
    """1 OXYGEN CLI call, pinned to the configured profile and org. Returns the envelope's data."""
    c = config()
    cmd = ["oxygen"]
    if c.get("oxygen_profile"):
        cmd += ["--profile", c["oxygen_profile"]]
    if c.get("oxygen_org"):
        cmd += ["--org", c["oxygen_org"]]
    cmd += [*args, "--json"]
    if max_chars:
        cmd += ["--max-chars", str(max_chars)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    try:
        # There can be output after the JSON envelope.
        data, _ = json.JSONDecoder().raw_decode(out.stdout.strip())
    except json.JSONDecodeError:
        raise RuntimeError(f"oxygen CLI returned no JSON: {out.stderr[:400] or out.stdout[:400]}")
    if not data.get("ok"):
        raise RuntimeError(f"oxygen CLI error: {json.dumps(data.get('error'))[:600]}")
    return data["data"]


def tool(tool_id, inp, cap, budget=None):
    """Run 1 scraper call live with a credit cap. Returns the provider response ({raw, results})."""
    if budget is not None and cap > 0 and SPENT["credits"] + cap > budget:
        raise RuntimeError(f"budget: {tool_id} would pass the run budget of {budget} credits")
    for attempt in range(5):
        try:
            data = cli(["tools", "run", tool_id, "--input-json", json.dumps(inp), "--mode", "live", "--approved",
                        "--max-credits", str(cap)])
            break
        except RuntimeError as e:
            # The managed scraper answers "capacity is busy" (rate_limit_exceeded) when too many
            # calls run at once: back off and retry. A paid read can also end
            # "provider_outcome_unknown"; 1 retry usually goes through.
            busy = "rate_limit_exceeded" in str(e)
            unknown = "provider_outcome_unknown" in str(e) and attempt < 1
            if not (busy or unknown) or attempt == 4:
                raise
            time.sleep(4 * 2 ** attempt + random.random() * 2)
    SPENT["credits"] += float((data.get("credits") or {}).get("credits_used") or 0)
    return data["result"]["response"]

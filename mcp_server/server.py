import ast
import math
import operator
import os
import re
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")


# ── Simple arithmetic ────────────────────────────────────────────────────────


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


# ── Safe math expression evaluator ──────────────────────────────────────────

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

_SAFE_FUNCS = {
    name: getattr(math, name)
    for name in (
        "sqrt",
        "log",
        "log2",
        "log10",
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "floor",
        "ceil",
        "factorial",
        "exp",
    )
}
_SAFE_NAMES = {**_SAFE_FUNCS, "pi": math.pi, "e": math.e, "inf": math.inf}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _SAFE_NAMES:
        return _SAFE_NAMES[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _SAFE_FUNCS
    ):
        return _SAFE_FUNCS[node.func.id](*[_eval_node(a) for a in node.args])
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


@mcp.tool
def evaluate_math(expression: str) -> dict:
    """
    Safely evaluate a mathematical expression string and return the result.
    Supports +, -, *, /, **, %, and functions: sqrt, log, sin, cos, tan, floor, ceil, factorial, exp.
    Constants: pi, e.
    Example: "sqrt(2) * pi" or "factorial(5) + log(100, 10)"
    """
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _eval_node(tree.body)
        return {"expression": expression, "result": result}
    except Exception as ex:
        return {"expression": expression, "error": str(ex)}


# ── HTTP fetch ───────────────────────────────────────────────────────────────


@mcp.tool
def fetch_url(url: str, timeout_seconds: int = 10) -> dict:
    """
    Fetch the content of a URL via HTTP GET.
    Returns status code, response headers (content-type), and the body text (truncated to 4000 chars).
    Use this to retrieve web pages, APIs, or raw text files.
    """
    try:
        resp = requests.get(
            url, timeout=timeout_seconds, headers={"User-Agent": "MCPAgent/1.0"}
        )
        body = resp.text[:4000]
        return {
            "url": url,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("content-type", ""),
            "body": body,
            "truncated": len(resp.text) > 4000,
        }
    except requests.RequestException as ex:
        return {"url": url, "error": str(ex)}


# ── File I/O (sandboxed to cwd) ──────────────────────────────────────────────


def _safe_path(relative_path: str) -> Path:
    """Resolve path and ensure it stays within cwd."""
    base = Path.cwd().resolve()
    target = (base / relative_path).resolve()
    if not str(target).startswith(str(base)):
        raise PermissionError("Access outside working directory is not allowed.")
    return target


@mcp.tool
def read_file(path: str) -> dict:
    """
    Read the contents of a file at the given relative path (relative to cwd).
    Returns the file contents as a string (truncated to 8000 chars).
    """
    try:
        p = _safe_path(path)
        content = p.read_text(encoding="utf-8")
        truncated = len(content) > 8000
        return {"path": str(p), "content": content[:8000], "truncated": truncated}
    except Exception as ex:
        return {"path": path, "error": str(ex)}


@mcp.tool
def write_file(path: str, content: str) -> dict:
    """
    Write content to a file at the given relative path (relative to cwd).
    Creates parent directories if they do not exist. Overwrites existing files.
    """
    try:
        p = _safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {
            "path": str(p),
            "bytes_written": len(content.encode("utf-8")),
            "success": True,
        }
    except Exception as ex:
        return {"path": path, "error": str(ex)}


# ── Text analysis ────────────────────────────────────────────────────────────


@mcp.tool
def analyze_text(text: str) -> dict:
    """
    Analyze a block of text and return statistics:
    character count, word count, sentence count, paragraph count,
    top-10 most frequent words, and average word length.
    """
    words = re.findall(r"\b\w+\b", text.lower())
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    freq: dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]

    avg_word_len = round(sum(len(w) for w in words) / len(words), 2) if words else 0

    return {
        "char_count": len(text),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "avg_word_length": avg_word_len,
        "top_words": [{"word": w, "count": c} for w, c in top_words],
    }


# ── Regex search & replace ───────────────────────────────────────────────────


@mcp.tool
def regex_search(text: str, pattern: str, max_matches: int = 20) -> dict:
    """
    Search for all occurrences of a regex pattern in text.
    Returns a list of matches with their start/end positions and captured groups.
    """
    try:
        compiled = re.compile(pattern)
        matches = []
        for i, m in enumerate(compiled.finditer(text)):
            if i >= max_matches:
                break
            matches.append(
                {
                    "match": m.group(0),
                    "start": m.start(),
                    "end": m.end(),
                    "groups": list(m.groups()),
                }
            )
        return {"pattern": pattern, "total_found": len(matches), "matches": matches}
    except re.error as ex:
        return {"pattern": pattern, "error": str(ex)}


@mcp.tool
def regex_replace(text: str, pattern: str, replacement: str) -> dict:
    """
    Replace all occurrences of a regex pattern in text with a replacement string.
    Supports backreferences in the replacement (e.g. \\1).
    Returns the modified text and count of substitutions made.
    """
    try:
        new_text, count = re.subn(pattern, replacement, text)
        return {"result": new_text, "substitutions": count}
    except re.error as ex:
        return {"error": str(ex)}


# ── Date / time utilities ────────────────────────────────────────────────────


@mcp.tool
def datetime_info(timezone_name: str = "UTC") -> dict:
    """
    Return the current date and time in the requested timezone.
    Supported values: 'UTC' or an offset like '+05:30'.
    Also returns ISO-8601 timestamp, Unix epoch, and day-of-week.
    """
    try:
        if timezone_name.upper() == "UTC":
            tz = timezone.utc
        else:
            sign = 1 if "+" in timezone_name else -1
            parts = timezone_name.replace("+", "").replace("-", "").split(":")
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            from datetime import timedelta

            tz = timezone(timedelta(hours=sign * hours, minutes=sign * minutes))

        now = datetime.now(tz)
        return {
            "timezone": timezone_name,
            "iso": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "unix_epoch": int(now.timestamp()),
        }
    except Exception as ex:
        return {"error": str(ex)}


# ── JSON utilities ───────────────────────────────────────────────────────────


@mcp.tool
def json_extract(json_string: str, key_path: str) -> dict:
    """
    Parse a JSON string and extract a value at a dot-separated key path.
    Example: key_path="user.address.city" on {"user": {"address": {"city": "NY"}}}.
    Array indices are supported: "items.0.name".
    """
    try:
        data = json.loads(json_string)
        parts = key_path.split(".")
        current = data
        for part in parts:
            if isinstance(current, list):
                current = current[int(part)]
            else:
                current = current[part]
        return {"key_path": key_path, "value": current}
    except (KeyError, IndexError) as ex:
        return {"key_path": key_path, "error": f"Key not found: {ex}"}
    except Exception as ex:
        return {"key_path": key_path, "error": str(ex)}


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)

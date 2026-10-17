"""Check repository GoTrue source templates only; no runtime, network or OTP input."""

import json
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("identity-confirmation.html", "identity-recovery.html")
TOKEN = "{{ .Token }}"
TAGS = {
    "html",
    "head",
    "meta",
    "title",
    "body",
    "div",
    "table",
    "tr",
    "td",
    "p",
    "h1",
    "code",
}
VOID = {"meta"}
ATTRIBUTES = {
    "lang",
    "dir",
    "style",
    "role",
    "width",
    "cellpadding",
    "cellspacing",
    "border",
    "charset",
    "name",
    "content",
}


class TemplateParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = set()
        self.counts = {tag: 0 for tag in TAGS}
        self.visible_tokens = 0
        self.title_text = ""
        self.body_language = False

    def handle_starttag(self, tag, attrs):
        if tag not in TAGS:
            self.errors.add("unsafe_element")
        self.counts[tag] = self.counts.get(tag, 0) + 1
        values = dict(attrs)
        if len(values) != len(attrs):
            self.errors.add("duplicate_attribute")
        for name, value in attrs:
            decoded = unescape(value or "").lower()
            if name not in ATTRIBUTES or any(
                item in decoded
                for item in ("url(", "expression", "@import", "javascript:", "{{", "}}")
            ):
                self.errors.add("unsafe_attribute")
            if name == "style" and any(
                item in decoded for item in ("http:", "https:", "//")
            ):
                self.errors.add("external_resource")
        if tag == "html" and (
            values.get("lang") != "es-MX" or values.get("dir") != "ltr"
        ):
            self.errors.add("document_language")
        if self.stack == ["html", "body"] and tag == "div":
            self.body_language = (
                values.get("lang") == "es-MX" and values.get("dir") == "ltr"
            )
        if tag == "table" and values.get("role") != "presentation":
            self.errors.add("table_accessibility")
        if tag == "meta" and set(values) not in ({"charset"}, {"name", "content"}):
            self.errors.add("unsafe_metadata")
        if tag == "meta" and "name" in values and values["name"] != "viewport":
            self.errors.add("unsafe_metadata")
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID or not self.stack or self.stack[-1] != tag:
            self.errors.add("unbalanced_html")
        else:
            self.stack.pop()

    def handle_data(self, data):
        if "title" in self.stack:
            self.title_text += data
        if TOKEN in data:
            if "body" in self.stack and self.stack[-1:] == ["code"]:
                self.visible_tokens += data.count(TOKEN)
            else:
                self.errors.add("token_location")
        if re.search(r"\b[0-9]{6}\b", data):
            self.errors.add("rendered_code")
        if re.search(
            r"(?:https?:|mailto:|www\.)|[\w.+-]+@[\w.-]+", data, re.IGNORECASE
        ):
            self.errors.add("address_or_url")

    def handle_comment(self, data):
        self.errors.add("unexpected_comment")

    def handle_decl(self, decl):
        if decl.lower() != "doctype html":
            self.errors.add("document_structure")

    def handle_pi(self, data):
        self.errors.add("unsafe_element")


def validate(source):
    """Return fixed issue codes only; never echo source or parser diagnostics."""
    parser = TemplateParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception:  # noqa: BLE001 - Parser/source data never cross the diagnostic boundary.
        return ("invalid_html",)
    errors = parser.errors
    if parser.stack:
        errors.add("unbalanced_html")
    if not source.lstrip().lower().startswith("<!doctype html>") or any(
        parser.counts[tag] != 1 for tag in ("html", "head", "body", "title", "h1")
    ):
        errors.add("document_structure")
    if not parser.body_language:
        errors.add("body_language")
    if not parser.title_text.strip():
        errors.add("missing_title")
    variables = re.findall(r"{{.*?}}", source, flags=re.DOTALL)
    if variables != [TOKEN] or source.count("{{") != 1 or source.count("}}") != 1:
        errors.add("template_variables")
    if parser.visible_tokens != 1:
        errors.add("token_location")
    return tuple(sorted(errors))


def report():
    results = {}
    for name in FILES:
        try:
            path = ROOT / "docs/email" / name
            if path.is_symlink():
                raise ValueError
            issues = validate(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - Fixed diagnostic boundary.
            issues = ("source_unavailable",)
        results[name] = {"status": "failed" if issues else "passed", "issues": issues}
    passed = all(item["status"] == "passed" for item in results.values())
    return {
        "status": "passed" if passed else "failed",
        "templates": results,
        "scope": "repository_source_only",
        "diagnostics": "suppressed",
    }, int(not passed)


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "issues": ["unexpected_arguments"],
                    "diagnostics": "suppressed",
                }
            )
        )
        raise SystemExit(1)
    result, code = report()
    print(json.dumps(result))
    raise SystemExit(code)

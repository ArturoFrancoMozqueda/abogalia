"""Source-template negative controls with public synthetic mutations only."""

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / "check_identity_mail_templates.py"
spec = importlib.util.spec_from_file_location("mail_templates", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class TemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (
            checker.ROOT / "docs/email/identity-confirmation.html"
        ).read_text()

    def test_current_sources(self):
        report, code = checker.report()
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "passed")

    def test_rejects_unsafe_elements(self):
        for content in (
            "<script>PUBLIC</script>",
            '<img src="https://example.invalid/pixel">',
            '<a href="https://example.invalid">PUBLIC</a>',
            "<form></form>",
        ):
            with self.subTest():
                self.assertTrue(
                    checker.validate(
                        self.source.replace("</body>", content + "</body>")
                    )
                )

    def test_rejects_attributes_and_css(self):
        for attribute in (
            'onclick="PUBLIC"',
            'style="background:url(https://example.invalid)"',
            'style="background:&#117;rl(https://example.invalid)"',
        ):
            with self.subTest():
                source = self.source.replace(
                    "<code style=", "<code " + attribute + " style="
                )
                self.assertTrue(checker.validate(source))

    def test_rejects_other_variables_and_duplicates(self):
        for token in (
            "{{ .Email }}",
            "{{ .ConfirmationURL }}",
            "{{ .Token }} {{ .Token }}",
            "{{ .Token }",
            "012345",
        ):
            with self.subTest():
                self.assertTrue(
                    checker.validate(self.source.replace(checker.TOKEN, token))
                )

    def test_token_cannot_move_to_title_attribute_or_comment(self):
        source = self.source.replace(checker.TOKEN, "")
        for mutated in (
            source.replace("</title>", checker.TOKEN + "</title>"),
            source.replace("<code style=", '<code role="{{ .Token }}" style='),
            source.replace("</body>", "<!-- {{ .Token }} --></body>"),
        ):
            with self.subTest():
                self.assertTrue(checker.validate(mutated))

    def test_accessibility_and_balance(self):
        for old, new in (
            ('lang="es-MX"', 'lang="en"'),
            ('dir="ltr"', 'dir="rtl"'),
            ('role="presentation"', ""),
            ("<h1 ", "<h2 "),
            ("</table>", ""),
        ):
            with self.subTest():
                self.assertTrue(checker.validate(self.source.replace(old, new)))

    def test_no_source_data_in_results(self):
        issues = checker.validate(
            self.source.replace("</body>", "PUBLIC_ADDRESS@example.invalid</body>")
        )
        self.assertNotIn("PUBLIC_ADDRESS", str(issues))
        self.assertIn("address_or_url", issues)
        with patch.object(
            Path, "read_text", side_effect=RuntimeError("PUBLIC_DIAGNOSTIC")
        ):
            report, code = checker.report()
        self.assertEqual(code, 1)
        self.assertNotIn("PUBLIC_DIAGNOSTIC", str(report))


if __name__ == "__main__":
    unittest.main()

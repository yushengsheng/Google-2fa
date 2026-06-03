import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import main


def base32_secret(raw: bytes) -> str:
    return base64.b32encode(raw).decode("ascii").rstrip("=")


class TotpTests(unittest.TestCase):
    def test_rfc6238_vectors(self) -> None:
        cases = [
            (
                "SHA1",
                b"12345678901234567890",
                [
                    (59, "94287082"),
                    (1111111109, "07081804"),
                    (1111111111, "14050471"),
                    (1234567890, "89005924"),
                    (2000000000, "69279037"),
                    (20000000000, "65353130"),
                ],
            ),
            (
                "SHA256",
                b"12345678901234567890123456789012",
                [
                    (59, "46119246"),
                    (1111111109, "68084774"),
                    (1111111111, "67062674"),
                    (1234567890, "91819424"),
                    (2000000000, "90698825"),
                    (20000000000, "77737706"),
                ],
            ),
            (
                "SHA512",
                b"1234567890123456789012345678901234567890123456789012345678901234",
                [
                    (59, "90693936"),
                    (1111111109, "25091201"),
                    (1111111111, "99943326"),
                    (1234567890, "93441116"),
                    (2000000000, "38618901"),
                    (20000000000, "47863826"),
                ],
            ),
        ]

        for algorithm, raw_secret, expected_values in cases:
            entry = main.build_entry(
                label="test",
                secret=base32_secret(raw_secret),
                digits=8,
                period=30,
                algorithm=algorithm,
            )
            for timestamp, expected_code in expected_values:
                with self.subTest(algorithm=algorithm, timestamp=timestamp):
                    code, _remaining = main.generate_totp(entry, timestamp)
                    self.assertEqual(code, expected_code)

    def test_code_formatting(self) -> None:
        self.assertEqual(main.format_code("123456"), "123 456")
        self.assertEqual(main.format_code("12345678"), "1234 5678")
        self.assertEqual(main.format_code("12345"), "12345")


class VersionTests(unittest.TestCase):
    def test_version_is_available_for_ui_label(self) -> None:
        self.assertRegex(main.APP_VERSION, r"^v\d+\.\d+\.\d+$")
        self.assertEqual(main.WINDOW_TITLE, main.APP_NAME)
        self.assertEqual(f"版本 {main.APP_VERSION}", "版本 v1.0.4")


class ImportParsingTests(unittest.TestCase):
    def test_parse_plain_csv_pipe_tab_and_otpauth(self) -> None:
        raw_text = "\n".join(
            [
                "JBSWY3DPEHPK3PXP",
                "Google,otpauth://totp/Google:me@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Google",
                "Work|JBSWY3DPEHPK3PXP|8|60|SHA256",
                "Tab\tJBSWY3DPEHPK3PXP\t6\t30\tSHA1",
            ]
        )

        entries, errors = main.parse_bulk_text(raw_text)

        self.assertEqual(errors, [])
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0].label, "密钥 01")
        self.assertEqual(entries[1].label, "Google")
        self.assertEqual(entries[2].label, "Work")
        self.assertEqual(entries[2].digits, 8)
        self.assertEqual(entries[2].period, 60)
        self.assertEqual(entries[2].algorithm, "SHA256")
        self.assertEqual(entries[3].label, "Tab")

    def test_parse_reports_invalid_lines_without_dropping_valid_lines(self) -> None:
        entries, errors = main.parse_bulk_text("bad-secret\nJBSWY3DPEHPK3PXP")

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].secret, "JBSWY3DPEHPK3PXP")
        self.assertEqual(len(errors), 1)
        self.assertIn("第 1 行", errors[0])


class StoragePathTests(unittest.TestCase):
    def test_source_run_uses_project_directory(self) -> None:
        self.assertEqual(main.get_app_dir(), Path(main.__file__).resolve().parent)

    def test_frozen_run_uses_executable_directory(self) -> None:
        executable = Path(tempfile.gettempdir()) / "release" / "谷歌验证器.exe"
        with mock.patch.object(sys, "frozen", True, create=True):
            with mock.patch.object(sys, "executable", str(executable)):
                self.assertEqual(main.get_app_dir(), executable.resolve().parent)

    def test_save_input_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "nested" / "secrets.txt"
            with mock.patch.object(main, "INPUT_FILE", input_file):
                main.save_input_text("JBSWY3DPEHPK3PXP")
                self.assertEqual(input_file.read_text(encoding="utf-8"), "JBSWY3DPEHPK3PXP")

    def test_migrates_legacy_accounts_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_file = root / "secrets.txt"
            legacy_file = root / "accounts.json"
            legacy_file.write_text(
                json.dumps(
                    [
                        {
                            "issuer": "Issuer",
                            "account": "user@example.com",
                            "secret": "JBSWY3DPEHPK3PXP",
                            "digits": 6,
                            "period": 30,
                            "algorithm": "SHA1",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            with mock.patch.object(main, "INPUT_FILE", input_file):
                with mock.patch.object(main, "LEGACY_DATA_FILE", legacy_file):
                    migrated = main.migrate_legacy_input()

            self.assertEqual(
                migrated,
                "Issuer user@example.com,JBSWY3DPEHPK3PXP,6,30,SHA1",
            )
            self.assertEqual(input_file.read_text(encoding="utf-8"), migrated)


if __name__ == "__main__":
    unittest.main()

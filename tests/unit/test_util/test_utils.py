import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import util


class UtilTests(unittest.TestCase):
    def test_replace(self):
        original = os.path.join("tests", "unit", "fixtures", "script.txt")
        with tempfile.TemporaryDirectory() as temp_dir:
            p_data1 = os.path.join(temp_dir, "script.txt")
            p_data2 = os.path.join(temp_dir, "script.txt")
            shutil.copyfile(original, p_data1)
            shutil.copyfile(original, p_data2)

            tags = [
                ("#SHREK#", "Rick Astley"),
                ("her", "lorem ipsum"),
                ("私the私", "それです"),
                ("#dragon#", "dinosaur"),
            ]

            try:
                f_data = open(p_data1, encoding="utf-8")
                util.replace_instances(p_data1, tags)
                f_result1 = open(p_data2, encoding="utf-8")
                self.assertEqual(f_data.read(), f_result1.read())

                p_changed = os.path.join(
                    "tests", "unit", "fixtures", "script_changed.txt"
                )
                f_changed = open(p_changed, encoding="utf-8")

                result2_path = os.path.join(temp_dir, "test.txt")
                util.replace_instances(p_data1, tags, result2_path)
                f_result2 = open(result2_path, encoding="utf-8")
                self.assertEqual(f_changed.read(), f_result2.read())
            finally:
                f_data.close()
                f_changed.close()
                f_result1.close()
                f_result2.close()

    @patch("sys.argv", ["-test", "-t", "--lorem", "--IPSUM"])
    def test_arg_exists(self):
        self.assertFalse(util.arg_exists("test"))
        self.assertFalse(util.arg_exists("--LOREM", "--ipsum"))
        self.assertTrue(util.arg_exists("-test"))
        self.assertTrue(util.arg_exists("test", "-t"))
        self.assertTrue(util.arg_exists("--LOREM", "--IPSUM"))
        self.assertTrue(util.arg_exists("-lorem", "-IPSUM", "--test", "-t"))


if __name__ == "__main__":
    unittest.main()

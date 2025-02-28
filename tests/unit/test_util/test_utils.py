import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import util


class UtilTests(unittest.TestCase):
    def test_replace(self):
        p_original = os.path.abspath(
            os.path.join("tests", "unit", "fixtures", "script.txt")
        )

        p_replaced = os.path.abspath(
            os.path.join("tests", "unit", "fixtures", "script_changed.txt")
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            print("Temporary directory at " + temp_dir)

            p_data1 = os.path.join(temp_dir, "script1.txt")
            p_data2 = os.path.join(temp_dir, "script2.txt")
            p_data3 = os.path.join(temp_dir, "script3.txt")
            shutil.copyfile(p_original, p_data1)
            shutil.copyfile(p_original, p_data3)

            tags = [
                ("#SHREK#", "Rick Astley"),
                ("her", "lorem ipsum"),
                ("私the私", "それです"),
                ("#dragon#", "dinosaur"),
            ]

            f_original = open(p_original, encoding="utf-8")
            f_replaced = open(p_replaced, encoding="utf-8")
            original_text = f_original.read()
            replaced_text = f_replaced.read()
            f_original.close()
            f_replaced.close()

            # Test replacing with same file name
            util.replace_instances(p_data1, tags)
            f_data1 = open(p_data1, encoding="utf-8")
            self.assertEqual(f_data1.read(), replaced_text)

            # Test replacing with new file name
            util.replace_instances(p_data1, tags, p_data2)
            f_data2 = open(p_data2, encoding="utf-8")
            self.assertEqual(f_data2.read(), replaced_text)

            # Test no tags to replace
            util.replace_instances(p_data3, [])
            f_data3 = open(p_data3, encoding="utf-8")
            self.assertEqual(f_data3.read(), original_text)

            f_data1.close()
            f_data2.close()
            f_data3.close()

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

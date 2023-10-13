import os
import sys
import unittest

from duckargs import generate_python_code


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

class TestDuckargs(unittest.TestCase):
    def setUp(self):
        # Set default env. var values
        os.environ["DUCKARGS_PRINT"] = "1"
        os.environ["DUCKARGS_COMMENT"] = "1"

    def _run_test(self, test_dir_name):
        test_dir_path = os.path.join(TEST_DATA_DIR, test_dir_name)
        expected_python_path = os.path.join(test_dir_path, "expected_python.txt")
        args_path = os.path.join(test_dir_path, "args.txt")

        with open(args_path, 'r') as fh:
            args = fh.read().strip().split()

        with open(expected_python_path, 'r') as fh:
            expected_python = fh.read().strip()

        generated_python = generate_python_code(args).strip()
        self.assertEqual(generated_python, expected_python)

    def test_readme_example(self):
        self._run_test("readme_example")

    def test_flags_only(self):
        self._run_test("flags_only")

    def test_positional_only(self):
        self._run_test("positional_only")

    def test_options_only(self):
        self._run_test("options_only")

    def test_normalize_names(self):
        self._run_test("normalize_names")

    def test_many_opts(self):
        self._run_test("many_opts")

    def test_choices(self):
        self._run_test("choices")

    def test_hex(self):
        self._run_test("hex")

    def test_positional_values(self):
        self._run_test("positional_values")

    def test_negative_int(self):
        self._run_test("negative_int")

    def test_negative_hex(self):
        self._run_test("negative_hex")

    def test_env_print(self):
        os.environ["DUCKARGS_PRINT"] = "0"
        self._run_test("env_print")

    def test_env_comment(self):
        os.environ["DUCKARGS_COMMENT"] = "0"
        self._run_test("env_comment")

    def test_env_all(self):
        os.environ["DUCKARGS_COMMENT"] = "0"
        os.environ["DUCKARGS_PRINT"] = "0"
        self._run_test("env_all")

    def test_duplicate_names(self):
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '-a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '-b', '-a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a-a', '-a_a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a-a', '-a+a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '--aye', '-b', '--aye'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', 'pos1', 'pos1'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '--aye', '6', '-b', '--bbb', '--aye'])

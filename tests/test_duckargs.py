import os
import sys
import unittest

from duckargs import generate_python_code, generate_c_code


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

class TestDuckargs(unittest.TestCase):
    def setUp(self):
        # Set default env. var values
        os.environ["DUCKARGS_PRINT"] = "1"
        os.environ["DUCKARGS_COMMENT"] = "1"

    def _run_python_test(self, test_dir_name):
        test_dir_path = os.path.join(TEST_DATA_DIR, test_dir_name)
        expected_python_path = os.path.join(test_dir_path, "expected_python.txt")
        args_path = os.path.join(test_dir_path, "args.txt")

        with open(args_path, 'r') as fh:
            args = fh.read().strip().split()

        with open(expected_python_path, 'r') as fh:
            expected_python = fh.read().strip()

        generated_python = generate_python_code(args).strip()
        self.assertEqual(generated_python, expected_python)

    def _run_c_test(self, test_dir_name):
        test_dir_path = os.path.join(TEST_DATA_DIR, test_dir_name)
        expected_c_path = os.path.join(test_dir_path, "expected_c.txt")
        args_path = os.path.join(test_dir_path, "args.txt")

        with open(args_path, 'r') as fh:
            args = fh.read().strip().split()

        with open(expected_c_path, 'r') as fh:
            expected_c = fh.read().strip()

        generated_c = generate_c_code(args).strip()
        self.assertEqual(generated_c, expected_c)

    def test_readme_example_c(self):
        self._run_c_test("readme_example")

    def test_readme_example_python(self):
        self._run_python_test("readme_example")

    def test_flags_only_c(self):
        self._run_c_test("flags_only")

    def test_flags_only_python(self):
        self._run_python_test("flags_only")

    def test_positional_only_c(self):
        self._run_c_test("positional_only")

    def test_positional_only_python(self):
        self._run_python_test("positional_only")

    def test_options_only_c(self):
        self._run_c_test("options_only")

    def test_options_only_python(self):
        self._run_python_test("options_only")

    def test_normalize_names_c(self):
        self._run_c_test("normalize_names")

    def test_normalize_names_python(self):
        self._run_python_test("normalize_names")

    def test_many_opts_c(self):
        self._run_c_test("many_opts")

    def test_many_opts_python(self):
        self._run_python_test("many_opts")

    def test_choices_c(self):
        self._run_c_test("choices")

    def test_choices_python(self):
        self._run_python_test("choices")

    def test_hex_c(self):
        self._run_c_test("hex")

    def test_hex_python(self):
        self._run_python_test("hex")

    def test_positional_values_c(self):
        self._run_c_test("positional_values")

    def test_positional_values_python(self):
        self._run_python_test("positional_values")

    def test_negative_int_c(self):
        self._run_c_test("negative_int")

    def test_negative_int_python(self):
        self._run_python_test("negative_int")

    def test_negative_hex_c(self):
        self._run_c_test("negative_hex")

    def test_negative_hex_python(self):
        self._run_python_test("negative_hex")

    def test_reserved_words_python_python(self):
        self._run_python_test("reserved_words_python")

    def test_reserved_words_python_c(self):
        self._run_c_test("reserved_words_python")

    def test_reserved_words_c_python(self):
        self._run_python_test("reserved_words_c")

    def test_reserved_words_c_c(self):
        self._run_c_test("reserved_words_c")

    def test_env_print_c(self):
        os.environ["DUCKARGS_PRINT"] = "0"
        self._run_c_test("env_print")

    def test_env_print_python(self):
        os.environ["DUCKARGS_PRINT"] = "0"
        self._run_python_test("env_print")

    def test_env_comment_c(self):
        os.environ["DUCKARGS_COMMENT"] = "0"
        self._run_c_test("env_comment")

    def test_env_comment_python(self):
        os.environ["DUCKARGS_COMMENT"] = "0"
        self._run_python_test("env_comment")

    def test_env_all_c(self):
        os.environ["DUCKARGS_COMMENT"] = "0"
        os.environ["DUCKARGS_PRINT"] = "0"
        self._run_c_test("env_all")

    def test_env_all_python(self):
        os.environ["DUCKARGS_COMMENT"] = "0"
        os.environ["DUCKARGS_PRINT"] = "0"
        self._run_python_test("env_all")

    def test_invalid_env_print(self):
        os.environ["DUCKARGS_PRINT"] = "ksfensik"
        self.assertRaises(RuntimeError, generate_python_code, ['duckargs', '-a'])

    def test_invalid_env_comment(self):
        os.environ["DUCKARGS_COMMENT"] = "ksfensik"
        self.assertRaises(RuntimeError, generate_python_code, ['duckargs', '-a'])

    def test_duplicate_names(self):
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '-a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '-b', '-a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a-a', '-a_a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a-a', '-a+a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '--aye', '-b', '-a', '--aye'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', 'pos1', 'pos1'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '--aye', '6', '-b', '--aye'])

    def test_longopt_without_shortopt(self):
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '--a'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '--apple', '3', '--ya'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', 'a', 'b', 'c', '--apple'])

    def test_shortopt_too_long(self):
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-rr'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', '-a', '--apple', '3', '-ya'])
        self.assertRaises(ValueError, generate_python_code, ['duckargs', 'a', 'b', 'c', '-apple'])

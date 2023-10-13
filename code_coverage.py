import unittest
import sys

from coverage import Coverage


MIN_COVERAGE_PERCENT = 95


def main():
    cov = Coverage(omit="tests/*")
    cov.start()

    suite = unittest.TestLoader().discover("tests")
    t = unittest.TextTestRunner(verbosity = 2)
    t.run(suite)

    cov.stop()
    pc = cov.report()

    exit_code = 0
    msg = ""

    if pc < float(MIN_COVERAGE_PERCENT):
        msg = f"ERROR!! Test coverage is {pc:.4f}% (must be at least {MIN_COVERAGE_PERCENT}%)."
        exit_code = 1
    else:
        msg = f"All good. Test coverage is sufficient (must be at least {MIN_COVERAGE_PERCENT}%)."

    print(f"\n{msg}\n")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

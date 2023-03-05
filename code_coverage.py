import unittest
from coverage import Coverage


MIN_COVERAGE_PERCENT = 95.0


def main():
    cov = Coverage()
    cov.start()

    suite = unittest.TestLoader().discover("tests")
    t = unittest.TextTestRunner(verbosity = 2)
    t.run(suite)

    cov.stop()
    pc = cov.report()

    if pc < MIN_COVERAGE_PERCENT:
        raise ValueError(f"Coverage percent was below {MIN_COVERAGE_PERCENT:.4f} ({pc:.4f})")

    print(f"Success, coverage was above {MIN_COVERAGE_PERCENT:.2f}%")

if __name__ == "__main__":
    main()

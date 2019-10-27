import pytest


def main():

    argv = ['--cov-report=term', '--cov-report=html:./coverage_report', '--cov=./src', '--cov-fail-under=80']

    out = 1
    try:
        out = pytest.main(argv)
    except SystemExit:
        pass
    except Exception:
        out = 3

    return out


if __name__ == '__main__':
    error_code = main()
    if error_code != 0:
        import sys
        sys.exit(error_code)

import pytest
import sys

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "--cov=app", "--cov-report=html", "tests/"]))
import os
from submission.test_user import test_

def test_case1():
    expected = os.environ.get("EXPECTED_OUTPUT", "")
    assert test_() == expected
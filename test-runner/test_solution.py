import os, json, importlib, pytest

@pytest.fixture(scope="session")
def test_data():

    with open("/app/submission/test_cases.json") as f:

        return json.load(f)


@pytest.fixture(scope="session")
def user_func():

    function_name = os.environ.get("FUNCTION_NAME", "")
    module = importlib.import_module("submission.solution")

    try:

        Test = getattr(module, "Test")

        instance = Test()

        return getattr(instance, f"test_{function_name}")

    except AttributeError:
        raise AssertionError(

            f"Function '{function_name} not found in your submission'"
            f"Make sure to name your function exactly: {function_name}"

        )

def test_all_cases(test_data, user_func):

    for i, case in enumerate(test_data, start=1):

        input_data = case["input"]
        expected = case["expected"]
        actual = user_func(*input_data)

        assert actual == expected, (

            f"Test case {i} FAILED\n"
            f"  Input:    {input_data}\n"
            f"  Expected: {expected}\n"
            f"  Got:      {actual}"

        )

    
    
    

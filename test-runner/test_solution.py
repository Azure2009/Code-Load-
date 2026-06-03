import os, json, importlib

def test_all_cases():

    with open("/app/submission/test_cases.json") as f:

       test_cases = json.load(f)

    function_name = os.environ.get("FUNCTION_NAME", "")
    
    module = importlib.import_module("submission.solution")

    try:

        Test = getattr(module, "Test")

        instance = Test()

        user_func = getattr(instance, f"test_{function_name}")

        for i, case in enumerate(test_cases, start=1):

            input_data = case["input"]
            expected = case["expected"]
            actual = user_func(input_data)

            assert actual == expected, (

                f"Test case {i} FAILED\n"
                f"  Input:    {input_data}\n"
                f"  Expected: {expected}\n"
                f"  Got:      {actual}"

            )

    except AttributeError:
        raise AssertionError(

            f"Function '{function_name} not found in your submission'"
            f"Make sure to name your function exactly: {function_name}"

        )

    
    

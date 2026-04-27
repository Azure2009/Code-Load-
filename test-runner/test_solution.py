import os, json, importlib

def test_all_cases():

    raw = os.environ.get("TEST_CASES", "[]")
    function_name = os.environ.get("FUNCTION_NAME", "")
    actual = json.loads(raw)

    module = importlib.import_module("submission.solution")
    user_func = getattr(module, function_name)

    for i, case in enumerate(actual, start=1):

        input_data = case["input"]
        expected = case["expected"]
        actual = user_func(input_data)


        assert input_data == expected, (

            f"Test case {i} FAILED\n"
            f"  Input:    {input_data}\n"
            f"  Expected: {expected}\n"
            f"  Got:      {actual}"

        )
    

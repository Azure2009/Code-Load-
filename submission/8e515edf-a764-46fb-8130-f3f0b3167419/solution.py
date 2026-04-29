def test_romanToInt(input_data):
    roman_to_int = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000
        }
    result = 0
    for i in range(len(input_data)):
        if i + 1 < len(input_data) and roman_to_int[input_data[i]] < roman_to_int[input_data[i + 1]]:
            result -= roman_to_int[input_data[i]]
        else:
            result += roman_to_int[input_data[i]] 
    return result
        
        
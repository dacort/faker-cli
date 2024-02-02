def infer_column_names(col_names, col_types: str) -> list[str]:
    """
    Infer column names from column types
    """
    # For now, nothing special - but eventually we need to parse things out
    if col_names:
        return col_names.split(",")

    return col_types.split(",")


def parse_column_types(input_string: str) -> list[tuple[str, list]]:
    """
    Parse a string of the format "pyint(1;10),datetime,profile(ssn,birthdate)" and split it by commas with optional parenthese-inclosed arguments.
    """
    import re

    pattern = r"([\w\.]+)(\([^)]*\))?"
    matches = re.findall(pattern, input_string)

    # Extract the matched groups
    result = [
        (match[0], ([try_convert_to_int(val) for val in match[1].strip("()").split(";")] if match[1] else []))
        for match in matches
    ]

    # print(result)
    # [('pyint', ['1', '10']), ('datetime', []), ('profile', ['ssn,birthdate'])]

    return result


def try_convert_to_int(s):
    try:
        return int(s)
    except ValueError:
        return s

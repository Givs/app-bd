import re


def extract_table_from_error(error_msg: str) -> str:
    matches = re.findall(r'table "(.*?)"', error_msg)
    if matches:
        return matches[-1]
    return "unknown table"

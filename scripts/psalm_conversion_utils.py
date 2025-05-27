import json
from typing import Dict, Any
from pathlib import Path

def vul_and_douay_to_modern(psalm_num: int) -> int:
    if psalm_num == 9 or psalm_num == 113:
        return psalm_num
    elif 10 <= psalm_num <= 112:
        return psalm_num + 1
    elif psalm_num in (114, 115):
        return 116
    elif psalm_num == 116:
        return 117
    elif 117 <= psalm_num <= 145:
        return psalm_num + 1
    elif psalm_num in (146, 147):
        return 147
    else:
        return psalm_num  # Psalms 1–8 and 148–150 are the same

def convert_psalm_numbers(input_json_path: str, output_json_path: str) -> None:
    """
    Convert psalm numbers in a JSON file according to the vul_and_douay_to_modern function.

    Args:
        input_json_path: Path to the input JSON file
        output_json_path: Path where the converted JSON will be saved
    """
    # Read the input JSON file
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create a new dictionary for the converted data
    converted_data: Dict[str, Any] = {
        "Ps": {
            "title": data["Ps"]["title"],
            "chapters": {}
        }
    }

    # Convert each psalm number
    for old_num, content in data["Ps"]["chapters"].items():
        old_num_int = int(old_num)
        new_num = vul_and_douay_to_modern(old_num_int)
        converted_data["Ps"]["chapters"][str(new_num)] = content

    # Write the converted data to the output file
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Example usage
    input_path = "scripts/json/psalms_pr.json"
    output_path = "scripts/json/psalms_pr_modern.json"
    convert_psalm_numbers(input_path, output_path)

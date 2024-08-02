import re
import sys
from typing import List, Tuple, Optional
"""
Originally from https://github.com/ZeframLou
Slight improvements, YMMV
"""

def main() -> None:
    """
    Main function to process command-line arguments and generate Solidity interface.
    """
    # Check for correct number of arguments
    if len(sys.argv) != 3:
        print("Usage: python3 vyper_to_solidity_interface.py [input_vyper_file] [output_solidity_file]")
        sys.exit(1)

    input_vyper_file, output_solidity_file = sys.argv[1], sys.argv[2]

    # Read Vyper code
    vyper_code = read_file(input_vyper_file)

    # Generate Solidity interface
    solidity_interface = generate_solidity_interface(vyper_code)

    # Write Solidity interface to output file
    write_file(output_solidity_file, solidity_interface)

    print(f"Solidity interface generated successfully: {output_solidity_file}")

def read_file(file_path: str) -> str:
    """
    Read and return the content of a file.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)

def write_file(file_path: str, content: str) -> None:
    """
    Write content to a file.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")
        sys.exit(1)

def convert_vyper_arg_to_solidity(arg: str) -> str:
    """
    Convert a Vyper argument to Solidity format.
    """
    if ':' not in arg:
        return ''
    var_name, var_type = map(str.strip, arg.split(':'))
    return f"{var_type} {var_name}"

def parse_vyper_code(vyper_code: str) -> Tuple[List[Tuple[str, ...]], List[Tuple[str, str]], List[Tuple[str, str]], List[Tuple[str, str]]]:
    """
    Parse Vyper code and extract functions, public variables, constant variables, and mappings.
    """
    function_regex = r"@(external|public|view|pure|payable)(?:\s|\n)+def\s+(\w+)\(([^)]*)\)(?:\s*->\s*([^:\n{]*)(?::\s*[^{]*)?)?"
    public_var_regex = r"(\w+)\s*:\s*public\((\w+)\)"
    const_var_regex = r"const\s+(\w+)\s*:\s*(\w+)"
    mapping_regex = r"(\w+):\s*public\((HashMap\[\w+,\s*[\w\[\]]+\])\)"

    functions = re.findall(function_regex, vyper_code, re.MULTILINE)
    public_vars = re.findall(public_var_regex, vyper_code, re.MULTILINE)
    const_vars = re.findall(const_var_regex, vyper_code, re.MULTILINE)
    mappings = re.findall(mapping_regex, vyper_code, re.MULTILINE)

    return functions, public_vars, const_vars, mappings

def generate_function_signature(modifier: str, func_name: str, args: str, return_type: Optional[str]) -> str:
    """
    Generate a Solidity function signature from Vyper function components.
    """
    args_list = args.split(',')
    arg_str = ', '.join([convert_vyper_arg_to_solidity(arg) for arg in args_list if arg.strip()])
    return_type_str = f"returns ({return_type.strip()})" if return_type and return_type.strip() else ""
    return f"    function {func_name}({arg_str}) {modifier} {return_type_str};"

def generate_mapping_signature(mapping_name: str, mapping_type: str) -> str:
    """
    Generate a Solidity mapping signature from Vyper mapping components.
    """
    key_type, value_type = re.search(r"HashMap\[(\w+),\s*([\w\[\]]+)\]", mapping_type).groups()
    key_type_solidity = key_type.strip()  # Directly use key_type as it doesn't need conversion
    return f"    function {mapping_name}({key_type_solidity}) external view returns ({value_type});"

def generate_solidity_interface(vyper_code: str) -> str:
    """
    Generate a Solidity interface from Vyper code.
    """
    functions, public_vars, const_vars, mappings = parse_vyper_code(vyper_code)

    interface_lines = [
        "// SPDX-License-Identifier: MIT",
        "pragma solidity ^0.8.0;",
        "",
        "interface IVyperContract {",
    ]

    # Generate function signatures
    for modifier, func_name, args, return_type in functions:
        if func_name == "__init__":
            continue
        interface_lines.append(generate_function_signature(modifier, func_name, args, return_type))

    # Generate public and constant variable signatures
    for var_name, var_type in public_vars + const_vars:
        interface_lines.append(f"    function {var_name}() external view returns ({var_type});")

    # Generate mapping signatures
    for mapping_name, mapping_type in mappings:
        interface_lines.append(generate_mapping_signature(mapping_name, mapping_type))

    interface_lines.append("}")

    return '\n'.join(interface_lines)

if __name__ == '__main__':
    main()

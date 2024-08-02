# test_vyper_to_solidity.py

import pytest
import re
from hypothesis import given, strategies as st
from vyper_to_solidity_interface import (
    convert_vyper_arg_to_solidity,
    parse_vyper_code,
    generate_function_signature,
    generate_mapping_signature,
    generate_solidity_interface,
)

# Define strategies for Vyper argument generation
vyper_arg_strategy = st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_', min_size=1, max_size=10)
vyper_type_strategy = st.sampled_from(['uint256', 'int256', 'address', 'bool', 'bytes', 'string'])

# Generate a strategy for Vyper function argument format
vyper_function_args_strategy = st.lists(
    st.tuples(vyper_arg_strategy, vyper_type_strategy).map(lambda x: f"{x[0]}: {x[1]}"),
    min_size=0,
    max_size=5
).map(lambda args: ', '.join(args))


@pytest.mark.parametrize(
    "arg,expected",
    [
        ("arg1: uint256", "uint256 arg1"),
        ("arg2: address", "address arg2"),
        ("", ""),
        ("invalid_arg", ""),
    ]
)
def test_convert_vyper_arg_to_solidity(arg, expected):
    assert convert_vyper_arg_to_solidity(arg) == expected


@given(vyper_args=vyper_function_args_strategy, return_type=st.none() | vyper_type_strategy)
def test_generate_function_signature(vyper_args, return_type):
    func_name = "testFunction"
    modifier = "external"
    signature = generate_function_signature(modifier, func_name, vyper_args, return_type)
    assert signature.startswith("    function testFunction(")
    if return_type:
        assert f"returns ({return_type})" in signature


@given(vyper_code=st.text())
def test_parse_vyper_code(vyper_code):
    # Check that the parsing function can run without error on random inputs
    functions, public_vars, const_vars, mappings = parse_vyper_code(vyper_code)
    assert isinstance(functions, list)
    assert isinstance(public_vars, list)
    assert isinstance(const_vars, list)
    assert isinstance(mappings, list)


@given(
    mapping_name=vyper_arg_strategy,
    key_type=vyper_type_strategy,
    value_type=vyper_type_strategy
)
def test_generate_mapping_signature(mapping_name, key_type, value_type):
    mapping_type = f"HashMap[{key_type}, {value_type}]"
    signature = generate_mapping_signature(mapping_name, mapping_type)
    assert signature.startswith(f"    function {mapping_name}(")
    assert f"external view returns ({value_type});" in signature


@given(
    vyper_code=st.text()
)
def test_generate_solidity_interface(vyper_code):
    # Check that the generated interface is a valid Solidity interface syntax
    solidity_interface = generate_solidity_interface(vyper_code)
    assert solidity_interface.startswith("// SPDX-License-Identifier: MIT")
    assert "pragma solidity" in solidity_interface
    assert "interface IVyperContract {" in solidity_interface

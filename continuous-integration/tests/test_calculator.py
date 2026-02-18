# tests/test_calculator.py

import pytest

from calc import (
    add,
    subtract,
    multiply,
    divide,
    calculator_tool,
    evaluate_expression,
)

# ────────────────────────────────────────────────
# Basic arithmetic function tests
# ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (2, 3, 5),
        (-2, -3, -5),
        (0, 0, 0),
        (1.5, 2.5, 4.0),
    ],
)
def test_add(x, y, expected):
    assert add(x, y) == expected


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (5, 2, 3),
        (0, 5, -5),
        (-5, -5, 0),
        (10.0, 3.5, 6.5),
    ],
)
def test_subtract(x, y, expected):
    assert subtract(x, y) == expected


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (3, 4, 12),
        (-2, 3, -6),
        (0, 10, 0),
        (1.5, 4, 6.0),
    ],
)
def test_multiply(x, y, expected):
    assert multiply(x, y) == expected


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (10, 2, 5.0),
        (5, 2, 2.5),
        (-10, 2, -5.0),
        (7, 4, 1.75),
    ],
)
def test_divide(x, y, expected):
    assert divide(x, y) == pytest.approx(expected)


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


def test_divide_always_returns_float():
    assert isinstance(divide(10, 5), float)  # 2.0
    assert isinstance(divide(7, 2), float)  # 3.5


# ────────────────────────────────────────────────
# calculator_tool routing / dispatch tests
# ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "tool_name, x, y, expected",
    [
        ("add", 2, 3, 5),
        ("subtract", 5, 2, 3),
        ("multiply", 3, 4, 12),
        ("divide", 10, 2, 5.0),
        ("add", -1.5, 4.5, 3.0),
    ],
)
def test_calculator_tool(tool_name, x, y, expected):
    result = calculator_tool(tool_name, x, y)
    assert result == pytest.approx(expected)


def test_calculator_tool_unknown_tool():
    with pytest.raises(ValueError, match=r"Unknown tool: 'power'"):
        calculator_tool("power", 2, 3)


# ────────────────────────────────────────────────
# Safe expression evaluation tests
# ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("2 + 3 * 4", 14),
        ("(2 + 3) * 4", 20),
        ("10 / 2", 5.0),
        ("3 - 7", -4),
        ("-5 + 8", 3),
        ("2 * (3 + 4)", 14),
        ("10.5 - 2.5", 8.0),
    ],
)
def test_valid_expressions(expression, expected):
    assert evaluate_expression(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression",
    [
        "2 + 3a",  # invalid character
        "import os",  # name not allowed
        "__import__('os').system('ls')",  # dangerous code attempt
        "2 + abs(3)",  # function call not allowed
    ],
)
def test_invalid_or_unsafe_expressions(expression):
    with pytest.raises(ValueError):
        evaluate_expression(expression)


def test_syntax_error():
    with pytest.raises(ValueError, match="Invalid syntax in expression"):
        evaluate_expression("2 +")  # incomplete expression


def test_empty_expression():
    with pytest.raises(ValueError):
        evaluate_expression("")


# ────────────────────────────────────────────────
# Coverage for defensive error in _eval_ast
# ────────────────────────────────────────────────


def test_unsupported_ast_node_boolean():
    with pytest.raises(ValueError, match="unsupported operation or structure"):
        evaluate_expression("True")


def test_unsupported_ast_node_comparison():
    with pytest.raises(ValueError, match="unsupported operation or structure"):
        evaluate_expression("2 > 1")


def test_unsupported_ast_node_logical_not():
    with pytest.raises(ValueError, match="unsupported operation or structure"):
        evaluate_expression("not 5")


def test_unsupported_ast_node_bitwise():
    with pytest.raises(ValueError, match="unsupported operation or structure"):
        evaluate_expression("3 & 1")

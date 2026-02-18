from __future__ import annotations

import ast
import operator
from typing import Callable

Number = int | float


def add(x: Number, y: Number) -> Number:
    """Add two numbers."""
    return x + y


def subtract(x: Number, y: Number) -> Number:
    """Subtract y from x."""
    return x - y


def multiply(x: Number, y: Number) -> Number:
    """Multiply two numbers."""
    return x * y


def divide(x: Number, y: Number) -> float:
    """Divide x by y. Raises ValueError if y is zero."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y


def calculator_tool(tool_name: str, x: Number, y: Number) -> Number:
    """
    Route to the appropriate math operation based on tool_name.

    Supported operations:
        - add
        - subtract
        - multiply
        - divide

    Raises:
        ValueError: If tool_name is unknown.
    """
    tools: dict[str, Callable[[Number, Number], Number]] = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,  # fixed: no unnecessary lambda
    }

    if tool_name not in tools:
        raise ValueError(
            f"Unknown tool: {tool_name!r}. " f"Supported: {', '.join(sorted(tools))}"
        )

    return tools[tool_name](x, y)


# Safe AST-based expression evaluator
_BIN_OPS: dict[type[ast.operator], Callable[[Number, Number], Number]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

_UNARY_OPS: dict[type[ast.unaryop], Callable[[Number], Number]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluate_expression(expression: str) -> Number:
    """
    Safely evaluate a simple arithmetic expression using AST parsing.

    Allowed syntax:
        - Integers and floating-point numbers
        - Binary operators: +, -, *, /
        - Unary operators: +, -
        - Parentheses for grouping

    Disallowed:
        - Variable names, function calls, attribute access, indexing, etc.

    Raises:
        ValueError: If the expression is invalid or contains disallowed constructs.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        return _eval_ast(tree.body)
    except (SyntaxError, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid expression: {expression!r}") from exc


def _eval_ast(node: ast.AST) -> Number:
    """Recursively evaluate an AST node to a number."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in _BIN_OPS:
            left = _eval_ast(node.left)
            right = _eval_ast(node.right)
            return _BIN_OPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in _UNARY_OPS:
            operand = _eval_ast(node.operand)
            return _UNARY_OPS[op_type](operand)

    raise ValueError("Expression contains unsupported operation or structure")

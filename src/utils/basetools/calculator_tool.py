"""
Calculator Tool for mathematical operations
Supports basic arithmetic, scientific functions, and complex expressions
Designed for use with AI agents and includes Pydantic models for structured input/output
"""

import math
import re
from typing import Union,Optional
from decimal import getcontext
import ast
import operator
from pydantic import BaseModel, Field, validator
from enum import Enum


class OperationType(str, Enum):
    """Enum for different types of operations."""

    BASIC = "basic"
    TRIGONOMETRIC = "trigonometric"
    LOGARITHMIC = "logarithmic"
    ADVANCED = "advanced"
    EXPRESSION = "expression"


class CalculationInput(BaseModel):
    """Input model for calculator operations."""

    expression: str = Field(..., description="Mathematical expression to calculate")
    degrees: bool = Field(
        default=False, description="Whether to use degrees for trigonometric functions"
    )
    precision: Optional[int] = Field(
        default=None, description="Number of decimal places to round to"
    )

    @validator("expression")
    def validate_expression(cls, v):
        if not v or not v.strip():
            raise ValueError("Expression cannot be empty")
        return v.strip()


class CalculationOutput(BaseModel):
    """Output model for calculator operations."""

    result: Union[float, int] = Field(..., description="The calculated result")
    expression: str = Field(..., description="The original expression")
    formatted_result: str = Field(..., description="Human-readable formatted result")
    operation_type: OperationType = Field(
        ..., description="Type of operation performed"
    )
    success: bool = Field(
        default=True, description="Whether the calculation was successful"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if calculation failed"
    )


class BasicOperationInput(BaseModel):
    """Input model for basic arithmetic operations."""

    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")
    operation: str = Field(
        ..., description="Operation: add, subtract, multiply, divide, power"
    )


class TrigonometricInput(BaseModel):
    """Input model for trigonometric operations."""

    angle: float = Field(..., description="Angle value")
    function: str = Field(
        ..., description="Trigonometric function: sin, cos, tan, asin, acos, atan"
    )
    degrees: bool = Field(default=False, description="Whether angle is in degrees")


class LogarithmInput(BaseModel):
    """Input model for logarithmic operations."""

    number: float = Field(
        ..., gt=0, description="Number to calculate logarithm of (must be positive)"
    )
    base: float = Field(
        default=math.e,
        gt=0,
        description="Base of logarithm (default: e for natural log)",
    )

    @validator("base")
    def validate_base(cls, v):
        if v == 1:
            raise ValueError("Logarithm base cannot be 1")
        return v


class MemoryOperation(BaseModel):
    """Input model for memory operations."""

    operation: str = Field(
        ..., description="Memory operation: store, recall, clear, add, subtract"
    )
    value: Optional[float] = Field(
        default=None, description="Value for store/add/subtract operations"
    )


class CalculatorTool:
    """A comprehensive calculator tool with support for various mathematical operations."""

    # Set precision for decimal calculations
    getcontext().prec = 28

    # Safe operators for eval
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Safe functions
    SAFE_FUNCTIONS = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "factorial": math.factorial,
        "degrees": math.degrees,
        "radians": math.radians,
        "ceil": math.ceil,
        "floor": math.floor,
        "gcd": math.gcd,
        "pi": math.pi,
        "e": math.e,
    }

    def __init__(self):
        """Initialize the calculator tool."""
        self.history = []
        self.memory = 0

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self._add_to_history(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        result = a - b
        self._add_to_history(f"{a} - {b} = {result}")
        return result

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = a * b
        self._add_to_history(f"{a} × {b} = {result}")
        return result

    def divide(self, a: float, b: float) -> float:
        """Divide a by b."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        result = a / b
        self._add_to_history(f"{a} ÷ {b} = {result}")
        return result

    def power(self, base: float, exponent: float) -> float:
        """Raise base to the power of exponent."""
        result = base**exponent
        self._add_to_history(f"{base}^{exponent} = {result}")
        return result

    def square_root(self, number: float) -> float:
        """Calculate square root of a number."""
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(number)
        self._add_to_history(f"√{number} = {result}")
        return result

    def percentage(self, number: float, percent: float) -> float:
        """Calculate percentage of a number."""
        result = (number * percent) / 100
        self._add_to_history(f"{percent}% of {number} = {result}")
        return result

    def sin(self, angle: float, degrees: bool = False) -> float:
        """Calculate sine of an angle."""
        if degrees:
            angle = math.radians(angle)
        result = math.sin(angle)
        unit = "°" if degrees else "rad"
        self._add_to_history(f"sin({angle}{unit}) = {result}")
        return result

    def cos(self, angle: float, degrees: bool = False) -> float:
        """Calculate cosine of an angle."""
        if degrees:
            angle = math.radians(angle)
        result = math.cos(angle)
        unit = "°" if degrees else "rad"
        self._add_to_history(f"cos({angle}{unit}) = {result}")
        return result

    def tan(self, angle: float, degrees: bool = False) -> float:
        """Calculate tangent of an angle."""
        if degrees:
            angle = math.radians(angle)
        result = math.tan(angle)
        unit = "°" if degrees else "rad"
        self._add_to_history(f"tan({angle}{unit}) = {result}")
        return result

    def log(self, number: float, base: float = math.e) -> float:
        """Calculate logarithm of a number."""
        if number <= 0:
            raise ValueError("Logarithm input must be positive")
        if base <= 0 or base == 1:
            raise ValueError("Logarithm base must be positive and not equal to 1")

        if base == math.e:
            result = math.log(number)
            self._add_to_history(f"ln({number}) = {result}")
        elif base == 10:
            result = math.log10(number)
            self._add_to_history(f"log₁₀({number}) = {result}")
        else:
            result = math.log(number, base)
            self._add_to_history(f"log_{base}({number}) = {result}")
        return result

    def factorial(self, n: int) -> int:
        """Calculate factorial of a number."""
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if not isinstance(n, int):
            raise ValueError("Factorial input must be an integer")
        result = math.factorial(n)
        self._add_to_history(f"{n}! = {result}")
        return result

    def evaluate_expression(self, expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        try:
            # Clean the expression
            expression = expression.replace(" ", "")
            expression = self._replace_constants(expression)
            expression = self._replace_functions(expression)

            # Parse and evaluate safely
            node = ast.parse(expression, mode="eval")
            result = self._eval_node(node.body)

            self._add_to_history(f"{expression} = {result}")
            return result

        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")

    def _eval_node(self, node) -> float:
        """Safely evaluate an AST node."""
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return float(node.value)
            else:
                raise ValueError(f"Unsupported constant type: {type(node.value)}")
        elif isinstance(node, ast.Num):  # Python < 3.8
            if isinstance(node.n, (int, float)):
                return float(node.n)
            else:
                raise ValueError(f"Unsupported number type: {type(node.n)}")
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op:
                return float(op(left, right))
            else:
                raise ValueError(f"Unsupported operation: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op:
                return float(op(operand))
            else:
                raise ValueError(f"Unsupported unary operation: {type(node.op)}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.SAFE_FUNCTIONS:
                    args = [self._eval_node(arg) for arg in node.args]
                    result = self.SAFE_FUNCTIONS[func_name](*args)
                    return float(result)
                else:
                    raise ValueError(f"Unsupported function: {func_name}")
            else:
                raise ValueError("Complex function calls not supported")
        elif isinstance(node, ast.Name):
            if node.id in self.SAFE_FUNCTIONS:
                value = self.SAFE_FUNCTIONS[node.id]
                if isinstance(value, (int, float)):
                    return float(value)
                else:
                    raise ValueError(f"Cannot use {node.id} as a value")
            else:
                raise ValueError(f"Unsupported name: {node.id}")
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")

    def _replace_constants(self, expression: str) -> str:
        """Replace mathematical constants in expression."""
        expression = expression.replace("π", str(math.pi))
        expression = expression.replace("pi", str(math.pi))
        expression = expression.replace("e", str(math.e))
        return expression

    def _replace_functions(self, expression: str) -> str:
        """Replace function names for easier parsing."""
        # Handle sqrt specially
        expression = re.sub(r"sqrt\(([^)]+)\)", r"(\1)**(0.5)", expression)
        return expression

    def memory_store(self, value: float) -> None:
        """Store value in memory."""
        self.memory = value
        self._add_to_history(f"Memory stored: {value}")

    def memory_recall(self) -> float:
        """Recall value from memory."""
        self._add_to_history(f"Memory recalled: {self.memory}")
        return self.memory

    def memory_clear(self) -> None:
        """Clear memory."""
        self.memory = 0
        self._add_to_history("Memory cleared")

    def memory_add(self, value: float) -> None:
        """Add value to memory."""
        self.memory += value
        self._add_to_history(f"Memory + {value} = {self.memory}")

    def memory_subtract(self, value: float) -> None:
        """Subtract value from memory."""
        self.memory -= value
        self._add_to_history(f"Memory - {value} = {self.memory}")

    def get_history(self) -> list:
        """Get calculation history."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()

    def _add_to_history(self, operation: str) -> None:
        """Add operation to history."""
        self.history.append(operation)
        # Keep only last 100 operations
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def calculate_with_validation(
        self, input_data: CalculationInput
    ) -> CalculationOutput:
        """
        Main calculation method with Pydantic validation for agents.

        Args:
            input_data (CalculationInput): Validated input data

        Returns:
            CalculationOutput: Structured output with result and metadata
        """
        try:
            # Determine operation type
            operation_type = self._determine_operation_type(input_data.expression)

            # Calculate result
            result = self.evaluate_expression(input_data.expression)

            # Apply precision if specified
            if input_data.precision is not None:
                result = round(result, input_data.precision)

            # Format result
            formatted_result = self._format_result(result, input_data.precision)

            return CalculationOutput(
                result=result,
                expression=input_data.expression,
                formatted_result=formatted_result,
                operation_type=operation_type,
                success=True,
            )

        except Exception as e:
            return CalculationOutput(
                result=0,
                expression=input_data.expression,
                formatted_result="Error",
                operation_type=OperationType.EXPRESSION,
                success=False,
                error_message=str(e),
            )

    def basic_operation(self, input_data: BasicOperationInput) -> CalculationOutput:
        """Perform basic arithmetic operations with validation."""
        try:
            operations = {
                "add": self.add,
                "subtract": self.subtract,
                "multiply": self.multiply,
                "divide": self.divide,
                "power": self.power,
            }

            if input_data.operation not in operations:
                raise ValueError(f"Unsupported operation: {input_data.operation}")

            result = operations[input_data.operation](input_data.a, input_data.b)
            expression = f"{input_data.a} {input_data.operation} {input_data.b}"

            return CalculationOutput(
                result=result,
                expression=expression,
                formatted_result=str(result),
                operation_type=OperationType.BASIC,
                success=True,
            )

        except Exception as e:
            return CalculationOutput(
                result=0,
                expression=f"{input_data.a} {input_data.operation} {input_data.b}",
                formatted_result="Error",
                operation_type=OperationType.BASIC,
                success=False,
                error_message=str(e),
            )

    def trigonometric_operation(
        self, input_data: TrigonometricInput
    ) -> CalculationOutput:
        """Perform trigonometric operations with validation."""
        try:
            functions = {"sin": self.sin, "cos": self.cos, "tan": self.tan}

            if input_data.function not in functions:
                raise ValueError(
                    f"Unsupported trigonometric function: {input_data.function}"
                )

            result = functions[input_data.function](
                input_data.angle, input_data.degrees
            )
            unit = "°" if input_data.degrees else "rad"
            expression = f"{input_data.function}({input_data.angle}{unit})"

            return CalculationOutput(
                result=result,
                expression=expression,
                formatted_result=str(result),
                operation_type=OperationType.TRIGONOMETRIC,
                success=True,
            )

        except Exception as e:
            return CalculationOutput(
                result=0,
                expression=f"{input_data.function}({input_data.angle})",
                formatted_result="Error",
                operation_type=OperationType.TRIGONOMETRIC,
                success=False,
                error_message=str(e),
            )

    def logarithm_operation(self, input_data: LogarithmInput) -> CalculationOutput:
        """Perform logarithmic operations with validation."""
        try:
            result = self.log(input_data.number, input_data.base)

            if input_data.base == math.e:
                expression = f"ln({input_data.number})"
            elif input_data.base == 10:
                expression = f"log₁₀({input_data.number})"
            else:
                expression = f"log_{input_data.base}({input_data.number})"

            return CalculationOutput(
                result=result,
                expression=expression,
                formatted_result=str(result),
                operation_type=OperationType.LOGARITHMIC,
                success=True,
            )

        except Exception as e:
            return CalculationOutput(
                result=0,
                expression=f"log({input_data.number})",
                formatted_result="Error",
                operation_type=OperationType.LOGARITHMIC,
                success=False,
                error_message=str(e),
            )

    def memory_operation(self, input_data: MemoryOperation) -> dict:
        """Perform memory operations with validation."""
        try:
            operations = {
                "store": self.memory_store,
                "recall": self.memory_recall,
                "clear": self.memory_clear,
                "add": self.memory_add,
                "subtract": self.memory_subtract,
            }

            if input_data.operation not in operations:
                raise ValueError(
                    f"Unsupported memory operation: {input_data.operation}"
                )

            if input_data.operation in ["store", "add", "subtract"]:
                if input_data.value is None:
                    raise ValueError(
                        f"Value required for {input_data.operation} operation"
                    )
                result = operations[input_data.operation](input_data.value)
            else:
                result = operations[input_data.operation]()

            return {
                "success": True,
                "operation": input_data.operation,
                "result": result if result is not None else self.memory,
                "memory_value": self.memory,
            }

        except Exception as e:
            return {
                "success": False,
                "operation": input_data.operation,
                "error_message": str(e),
                "memory_value": self.memory,
            }

    def _determine_operation_type(self, expression: str) -> OperationType:
        """Determine the type of operation from expression."""
        expression = expression.lower()

        if any(
            func in expression for func in ["sin", "cos", "tan", "asin", "acos", "atan"]
        ):
            return OperationType.TRIGONOMETRIC
        elif any(func in expression for func in ["log", "ln", "log10", "log2"]):
            return OperationType.LOGARITHMIC
        elif any(func in expression for func in ["sqrt", "factorial", "exp", "pow"]):
            return OperationType.ADVANCED
        elif any(op in expression for op in ["+", "-", "*", "/", "**", "^"]):
            return OperationType.BASIC
        else:
            return OperationType.EXPRESSION

    def _format_result(self, result: float, precision: Optional[int] = None) -> str:
        """Format result for display."""
        if precision is not None:
            return f"{result:.{precision}f}"
        elif result == int(result):
            return str(int(result))
        else:
            return str(result)

    def calculate(
        self, expression: str, degrees: bool = False, precision: Optional[int] = None
    ) -> Union[float, int]:
        """
        Main calculation method that handles various input formats.

        Args:
            expression (str): Mathematical expression to evaluate
            degrees (bool): Whether to use degrees for trigonometric functions
            precision (Optional[int]): Number of decimal places to round to

        Returns:
            Union[float, int]: Result of the calculation

        Examples:
            calc.calculate("2 + 3")  # Returns 5
            calc.calculate("sqrt(16)")  # Returns 4.0
            calc.calculate("sin(30)", degrees=True)  # Returns 0.5
        """
        try:
            # Create input model for validation
            input_data = CalculationInput(
                expression=expression, degrees=degrees, precision=precision
            )

            # Use the validated calculation method
            output = self.calculate_with_validation(input_data)

            if output.success:
                return output.result
            else:
                raise ValueError(output.error_message)

        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")


# Global calculator instance for tool usage
_calculator_instance = CalculatorTool()


# Convenience function for quick calculations
def calculate(expression: str) -> Union[float, int]:
    """Quick calculation function."""
    calc = CalculatorTool()
    return calc.calculate(expression)


# Tool functions for agent usage
def calculate_expression(
    expression: str, degrees: bool = False, precision: Optional[int] = None
) -> str:
    """
    Calculate mathematical expressions for use in AI agents.

    Args:
        expression (str): Mathematical expression to evaluate (e.g., "2 + 3 * 4", "sin(30)", "sqrt(16)")
        degrees (bool): Whether to use degrees for trigonometric functions (default: False)
        precision (Optional[int]): Number of decimal places to round to (default: None)

    Returns:
        str: Formatted result with calculation details

    Examples:
        calculate_expression("2 + 3 * 4") -> "2 + 3 * 4 = 14"
        calculate_expression("sin(30)", degrees=True) -> "sin(30°) = 0.5"
        calculate_expression("sqrt(16) + 2^3") -> "sqrt(16) + 2^3 = 12.0"
    """
    try:
        input_data = CalculationInput(
            expression=expression, degrees=degrees, precision=precision
        )

        result = _calculator_instance.calculate_with_validation(input_data)

        if result.success:
            return f"{result.expression} = {result.formatted_result}"
        else:
            return f"Error calculating '{expression}': {result.error_message}"

    except Exception as e:
        return f"Error: {str(e)}"


def basic_math(a: float, b: float, operation: str) -> str:
    """
    Perform basic mathematical operations for use in AI agents.

    Args:
        a (float): First number
        b (float): Second number
        operation (str): Operation to perform (add, subtract, multiply, divide, power)

    Returns:
        str: Formatted result with calculation details

    Examples:
        basic_math(10, 3, "add") -> "10 + 3 = 13"
        basic_math(15, 3, "divide") -> "15 ÷ 3 = 5"
    """
    try:
        input_data = BasicOperationInput(a=a, b=b, operation=operation)
        result = _calculator_instance.basic_operation(input_data)

        if result.success:
            symbol_map = {
                "add": "+",
                "subtract": "-",
                "multiply": "×",
                "divide": "÷",
                "power": "^",
            }
            symbol = symbol_map.get(operation, operation)
            return f"{a} {symbol} {b} = {result.formatted_result}"
        else:
            return f"Error: {result.error_message}"

    except Exception as e:
        return f"Error: {str(e)}"


def trigonometry(angle: float, function: str, degrees: bool = True) -> str:
    """
    Calculate trigonometric functions for use in AI agents.

    Args:
        angle (float): Angle value
        function (str): Trigonometric function (sin, cos, tan, asin, acos, atan)
        degrees (bool): Whether angle is in degrees (default: True)

    Returns:
        str: Formatted result with calculation details

    Examples:
        trigonometry(30, "sin", True) -> "sin(30°) = 0.5"
        trigonometry(1.57, "cos", False) -> "cos(1.57 rad) = 0.0007963"
    """
    try:
        input_data = TrigonometricInput(angle=angle, function=function, degrees=degrees)
        result = _calculator_instance.trigonometric_operation(input_data)

        if result.success:
            return f"{result.expression} = {result.formatted_result}"
        else:
            return f"Error: {result.error_message}"

    except Exception as e:
        return f"Error: {str(e)}"


def logarithm(number: float, base: float = math.e) -> str:
    """
    Calculate logarithms for use in AI agents.

    Args:
        number (float): Number to calculate logarithm of (must be positive)
        base (float): Base of logarithm (default: e for natural log)

    Returns:
        str: Formatted result with calculation details

    Examples:
        logarithm(100, 10) -> "log₁₀(100) = 2.0"
        logarithm(2.718) -> "ln(2.718) = 0.999896"
    """
    try:
        input_data = LogarithmInput(number=number, base=base)
        result = _calculator_instance.logarithm_operation(input_data)

        if result.success:
            return f"{result.expression} = {result.formatted_result}"
        else:
            return f"Error: {result.error_message}"

    except Exception as e:
        return f"Error: {str(e)}"


def calculator_memory(operation: str, value: Optional[float] = None) -> str:
    """
    Perform memory operations for calculator in AI agents.

    Args:
        operation (str): Memory operation (store, recall, clear, add, subtract)
        value (Optional[float]): Value for store/add/subtract operations

    Returns:
        str: Formatted result with memory operation details

    Examples:
        calculator_memory("store", 42) -> "Memory stored: 42"
        calculator_memory("recall") -> "Memory recalled: 42"
        calculator_memory("add", 8) -> "Memory + 8 = 50"
    """
    try:
        input_data = MemoryOperation(operation=operation, value=value)
        result = _calculator_instance.memory_operation(input_data)

        if result["success"]:
            if operation == "recall":
                return f"Memory recalled: {result['memory_value']}"
            elif operation == "clear":
                return "Memory cleared"
            elif operation == "store":
                return f"Memory stored: {value}"
            elif operation == "add":
                return f"Memory + {value} = {result['memory_value']}"
            elif operation == "subtract":
                return f"Memory - {value} = {result['memory_value']}"
            else:
                return f"Memory operation completed: {result['memory_value']}"
        else:
            return f"Error: {result['error_message']}"

    except Exception as e:
        return f"Error: {str(e)}"

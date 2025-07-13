from langchain.tools import tool

class CalculatorTools:

    @tool("Make a calculation")
    def calculate(operation: str) -> str:
        """
        Perform basic mathematical calculations such as addition, subtraction,
        multiplication, and division.

        The input should be a valid mathematical expression.
        Examples:
          - '200 * 7'
          - '5000 / 2 * 10'
          - '100 + 250 - 50'

        Returns:
            The result of the calculation as a string, or an error message if invalid.
        """
        try:
            return str(eval(operation))
        except (SyntaxError, NameError, ZeroDivisionError) as e:
            return f"Error: {str(e)}"

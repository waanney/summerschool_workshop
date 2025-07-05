from pydantic_ai import RunContext
def get_current_date(ctx: RunContext) -> str:

    """Returns the current date."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


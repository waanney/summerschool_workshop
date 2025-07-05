class PromptTemplate:
    def __init__(self, template_string):
        """Initialize the template with a string."""
        self.template_string = template_string

    def apply(self, input_data):
        """Apply the template to the input data."""
        return self.template_string.format(input=input_data)

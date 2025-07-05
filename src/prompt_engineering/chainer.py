
from pydantic import BaseModel, Field
import openai

class InputData(BaseModel):
    """A Pydantic model for validating input data for the prompt generation."""
    context: str = Field(..., title="Context", description="The context from which to generate the prompt.")
    keywords: list[str] = Field(..., title="Keywords", description="A list of keywords relevant to the prompt.")
    
class Chainer:
    def __init__(self, templates, llm_model="gpt-3.5-turbo"):
        """Initialize the Chainer with templates and LLM model."""
        self.templates = templates
        self.llm_model = llm_model
        openai.api_key = "your-openai-api-key"  # Use your OpenAI API key here

    def generate_prompt(self, input_data: InputData):
        """Generate a dynamic prompt using the LLM and validated input data."""
        # Convert Pydantic model to dictionary to access attributes
        context = input_data.context
        keywords = ", ".join(input_data.keywords)
        
        # Generate prompt using the LLM
        prompt = f"Create a detailed prompt using the following context: {context} and keywords: {keywords}"
        
        response = openai.Completion.create(
            engine=self.llm_model,
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
        )
        return response.choices[0].text.strip()

    def chain(self, input_data: InputData):
        """Chain the generated prompts together and apply any templates."""
        # Generate a prompt dynamically using the LLM
        dynamic_prompt = self.generate_prompt(input_data)
        
        # Apply all templates to the generated prompt
        for template in self.templates:
            dynamic_prompt = template.apply(dynamic_prompt)
        
        return dynamic_prompt

# Examples và Use Cases

## 1. Customer Service Bot

### Scenario
Tạo một customer service bot cho trường đại học để trả lời các câu hỏi về tuyển sinh, học bổng, và chính sách.

### Implementation

### How to run this python file
```
chainlit run customer_service_bot.py
```

```python
# customer_service_bot.py
import os
import chainlit as cl
from data.milvus.indexing import MilvusIndexer
from llm.base import AgentClient
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from utils.basetools import create_faq_tool, create_send_email_tool, EmailToolInput
from data.cache.memory_handler import MessageMemoryHandler

# 1. Index FAQ data
indexer = MilvusIndexer(
    collection_name="university_faq",
    faq_file="src/data/mock_data/Admission_FAQ_final.csv"
)
indexer.run()

# 2. Setup model
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)

# 3. Create tools
faq_tool = create_faq_tool(collection_name="university_faq")
email_tool = create_send_email_tool(
    to_emails=["admissions@university.edu"],
    sender_email=None,
    sender_password=None
)

# 4. Memory handler
memory_handler = MessageMemoryHandler(max_messages=10)

# 5. Create agent
CUSTOMER_SERVICE_PROMPT = """
You are a friendly customer service representative for a university.

Your responsibilities:
1. Answer questions about admissions, scholarships, courses, and policies
2. Use the faq_tool to search for accurate information
3. If a question requires human attention, use email_tool to notify staff
4. Be helpful, professional, and empathetic
5. Remember the conversation context

Guidelines:
- Always search the FAQ first before responding
- If you can't find information, admit it and offer to escalate
- Use natural, conversational language
- Show empathy for student concerns
- End responses by asking if there's anything else you can help with
"""

agent = AgentClient(
    model=model,
    system_prompt=CUSTOMER_SERVICE_PROMPT,
    tools=[faq_tool, email_tool]
).create_agent()

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content="👋 Welcome to University Customer Service! I'm here to help you with questions about admissions, scholarships, courses, and policies. How can I assist you today?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    try:
        # Get message with history context
        full_message = memory_handler.get_history_message(message.content)
        
        # Process with agent
        response = await agent.run(full_message)
        
        # Store response in memory
        memory_handler.store_bot_response(str(response.output))
        
        # Send response
        await cl.Message(content=str(response.output)).send()
        
    except Exception as e:
        error_msg = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment, or contact our support team directly."
        await cl.Message(content=error_msg).send()
        
        # Send error notification
        email_tool(EmailToolInput(
            subject="Chatbot Error",
            body=f"Error occurred: {str(e)}\nUser message: {message.content}"
        ))

### Usage Examples

```
User: "How do I apply for a scholarship?"
Bot: "Based on our scholarship information, here are the steps to apply:
1. Complete the online application form
2. Submit required documents (transcripts, essays, recommendations)
3. Meet the deadline (typically March 1st for fall semester)
4. Attend an interview if selected

Would you like more details about any specific scholarship program?"

User: "What documents do I need?"
Bot: "For scholarship applications, you'll typically need:
- Official transcripts
- Personal statement/essay
- Letters of recommendation (2-3)
- Financial aid forms (if applicable)
- Portfolio (for art/design scholarships)

Is there anything else about the application process I can help clarify?"
```

---

## 2. E-commerce Support Agent

### Scenario
Tạo một support agent cho website thương mại điện tử để trả lời câu hỏi về sản phẩm, đơn hàng, và chính sách.

### Implementation

```python
# ecommerce_support_agent.py
import os
import chainlit as cl
from data.milvus.indexing import MilvusIndexer
from llm.base import AgentClient
from utils.basetools import create_faq_tool, http_tool, HttpRequest, HTTPMethod
from data.cache.memory_handler import MessageMemoryHandler

# Index product and policy data
indexer = MilvusIndexer(
    collection_name="ecommerce_kb",
    faq_file="src/data/mock_data/Product_Info_final.csv"
)
indexer.run()

# Create tools
faq_tool = create_faq_tool(collection_name="ecommerce_kb")

# Custom order lookup tool
class OrderLookupInput(BaseModel):
    order_id: str = Field(..., description="Order ID to lookup")

class OrderLookupOutput(BaseModel):
    order_status: str = Field(..., description="Current order status")
    tracking_number: str = Field(..., description="Tracking number if available")
    estimated_delivery: str = Field(..., description="Estimated delivery date")

def order_lookup_tool(input: OrderLookupInput) -> OrderLookupOutput:
    """Look up order status via API."""
    
    # Call order management API
    response = http_tool(HttpRequest(
        url=f"https://api.yourstore.com/orders/{input.order_id}",
        method=HTTPMethod.GET,
        headers={"Authorization": f"Bearer {os.getenv('STORE_API_KEY')}"}
    ))
    
    if response.status_code == 200:
        order_data = response.body
        return OrderLookupOutput(
            order_status=order_data.get("status", "Unknown"),
            tracking_number=order_data.get("tracking_number", "Not available"),
            estimated_delivery=order_data.get("estimated_delivery", "TBD")
        )
    else:
        return OrderLookupOutput(
            order_status="Not found",
            tracking_number="N/A",
            estimated_delivery="N/A"
        )

# Create agent
ECOMMERCE_PROMPT = """
You are a helpful e-commerce customer support agent.

Your capabilities:
1. Answer product questions using faq_tool
2. Look up order status using order_lookup_tool
3. Provide information about policies and procedures
4. Help with returns and exchanges

Guidelines:
- Be friendly and solution-oriented
- Search for product information before responding
- For order inquiries, use the order lookup tool
- Escalate complex issues appropriately
- Always confirm order details before making changes
"""

agent = AgentClient(
    model=model,
    system_prompt=ECOMMERCE_PROMPT,
    tools=[faq_tool, order_lookup_tool]
).create_agent()

@cl.on_message
async def main(message: cl.Message):
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()
```

---

## 3. Technical Documentation Assistant

### Scenario
Tạo một assistant để giúp developers tìm kiếm và hiểu technical documentation.

### Implementation

```python
# tech_doc_assistant.py
import os
import chainlit as cl
from data.milvus.indexing import MilvusIndexer
from utils.basetools import create_faq_tool, create_read_file_tool, web_scraping_tool
from llm.base import AgentClient

# Index technical documentation
indexer = MilvusIndexer(
    collection_name="tech_docs",
    faq_file="src/data/mock_data/technical_docs.csv"
)
indexer.run()

# Create tools
docs_tool = create_faq_tool(collection_name="tech_docs")
file_tool = create_read_file_tool(allowed_extensions=[".md", ".txt", ".py", ".js"])

# Custom code explanation tool
class CodeExplanationInput(BaseModel):
    code_snippet: str = Field(..., description="Code snippet to explain")
    language: str = Field("python", description="Programming language")

class CodeExplanationOutput(BaseModel):
    explanation: str = Field(..., description="Detailed code explanation")
    key_concepts: List[str] = Field(..., description="Key concepts used")
    suggestions: List[str] = Field(..., description="Improvement suggestions")

def code_explanation_tool(input: CodeExplanationInput) -> CodeExplanationOutput:
    """Explain code snippets in detail."""
    
    # Analyze code (simplified example)
    lines = input.code_snippet.split('\n')
    concepts = []
    
    # Simple pattern matching for key concepts
    for line in lines:
        if 'def ' in line:
            concepts.append("Function definition")
        elif 'class ' in line:
            concepts.append("Class definition")
        elif 'import ' in line:
            concepts.append("Module import")
        elif 'for ' in line:
            concepts.append("Loop iteration")
        elif 'if ' in line:
            concepts.append("Conditional logic")
    
    explanation = f"""
    This {input.language} code snippet contains {len(lines)} lines.
    
    Key elements:
    - {len(concepts)} programming concepts identified
    - Primary language: {input.language}
    
    The code appears to implement functionality related to the identified concepts.
    """
    
    return CodeExplanationOutput(
        explanation=explanation,
        key_concepts=list(set(concepts)),
        suggestions=["Add comments for clarity", "Consider error handling", "Use descriptive variable names"]
    )

# Create agent
TECH_DOC_PROMPT = """
You are a technical documentation assistant for developers.

Your capabilities:
1. Search technical documentation using docs_tool
2. Read and analyze code files using file_tool
3. Explain code snippets using code_explanation_tool
4. Provide best practices and recommendations

Guidelines:
- Provide accurate technical information
- Include code examples when helpful
- Explain complex concepts in simple terms
- Suggest best practices and improvements
- Reference official documentation when available
"""

agent = AgentClient(
    model=model,
    system_prompt=TECH_DOC_PROMPT,
    tools=[docs_tool, file_tool, code_explanation_tool]
).create_agent()

@cl.on_message
async def main(message: cl.Message):
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()
```

---

## 4. HR Assistant

### Scenario
Tạo một HR assistant để trả lời câu hỏi về chính sách công ty, benefits, và procedures.

### Implementation

```python
# hr_assistant.py
import os
import chainlit as cl
from data.milvus.indexing import MilvusIndexer
from utils.basetools import create_faq_tool, create_send_email_tool, EmailToolInput
from data.cache.memory_handler import MessageMemoryHandler
from datetime import datetime, timedelta

# Index HR policies and procedures
indexer = MilvusIndexer(
    collection_name="hr_policies",
    faq_file="src/data/mock_data/HR_FAQ.xlsx"
)
indexer.run()

# Create tools
hr_faq_tool = create_faq_tool(collection_name="hr_policies")
hr_email_tool = create_send_email_tool(
    to_emails=["hr@company.com"],
    sender_email=None,
    sender_password=None
)

# Custom leave calculation tool
class LeaveCalculationInput(BaseModel):
    employee_id: str = Field(..., description="Employee ID")
    leave_type: str = Field(..., description="Type of leave (annual, sick, etc.)")
    start_date: str = Field(..., description="Leave start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Leave end date (YYYY-MM-DD)")

class LeaveCalculationOutput(BaseModel):
    total_days: int = Field(..., description="Total leave days requested")
    working_days: int = Field(..., description="Working days excluding weekends")
    remaining_balance: str = Field(..., description="Estimated remaining balance")
    approval_required: bool = Field(..., description="Whether manager approval is required")

def leave_calculation_tool(input: LeaveCalculationInput) -> LeaveCalculationOutput:
    """Calculate leave days and check balance."""
    
    from datetime import datetime, timedelta
    
    start = datetime.strptime(input.start_date, "%Y-%m-%d")
    end = datetime.strptime(input.end_date, "%Y-%m-%d")
    
    # Calculate total days
    total_days = (end - start).days + 1
    
    # Calculate working days (excluding weekends)
    working_days = 0
    current_date = start
    while current_date <= end:
        if current_date.weekday() < 5:  # Monday=0, Friday=4
            working_days += 1
        current_date += timedelta(days=1)
    
    # Simplified logic for approval requirement
    approval_required = working_days > 3 or input.leave_type.lower() == "sick"
    
    return LeaveCalculationOutput(
        total_days=total_days,
        working_days=working_days,
        remaining_balance="Please check with HR for exact balance",
        approval_required=approval_required
    )

# Create agent
HR_PROMPT = """
You are a helpful HR assistant for company employees.

Your capabilities:
1. Answer questions about company policies using hr_faq_tool
2. Calculate leave days using leave_calculation_tool
3. Send requests to HR team using hr_email_tool
4. Provide information about benefits, procedures, and policies

Guidelines:
- Maintain confidentiality and professionalism
- Provide accurate policy information
- For sensitive matters, direct to HR team
- Calculate leave accurately and explain the process
- Be empathetic to employee concerns
"""

agent = AgentClient(
    model=model,
    system_prompt=HR_PROMPT,
    tools=[hr_faq_tool, leave_calculation_tool, hr_email_tool]
).create_agent()

memory_handler = MessageMemoryHandler(max_messages=8)

@cl.on_message
async def main(message: cl.Message):
    # Get message with context
    full_message = memory_handler.get_history_message(message.content)
    
    # Process with agent
    response = await agent.run(full_message)
    
    # Store response
    memory_handler.store_bot_response(str(response.output))
    
    await cl.Message(content=str(response.output)).send()
```

---

## 5. Educational Tutor

### Scenario
Tạo một AI tutor để giúp học sinh với các câu hỏi về môn học và homework.

### Implementation

```python
# educational_tutor.py
import os
import chainlit as cl
from data.milvus.indexing import MilvusIndexer
from utils.basetools import create_faq_tool, calculate, CalculationInput
from llm.base import AgentClient

# Index educational content
indexer = MilvusIndexer(
    collection_name="educational_content",
    faq_file="src/data/mock_data/Course_FAQ_final.csv"
)
indexer.run()

# Create tools
study_tool = create_faq_tool(collection_name="educational_content")

# Custom quiz generator tool
class QuizGeneratorInput(BaseModel):
    topic: str = Field(..., description="Topic for the quiz")
    difficulty: str = Field("medium", description="Difficulty level (easy, medium, hard)")
    num_questions: int = Field(5, description="Number of questions")

class QuizGeneratorOutput(BaseModel):
    questions: List[str] = Field(..., description="Generated quiz questions")
    topic: str = Field(..., description="Quiz topic")
    difficulty: str = Field(..., description="Quiz difficulty level")

def quiz_generator_tool(input: QuizGeneratorInput) -> QuizGeneratorOutput:
    """Generate quiz questions on a given topic."""
    
    # Sample quiz questions (in a real implementation, these would be generated dynamically)
    question_templates = {
        "easy": [
            f"What is the definition of {input.topic}?",
            f"List three key features of {input.topic}.",
            f"True or False: {input.topic} is important in daily life.",
        ],
        "medium": [
            f"Explain how {input.topic} works.",
            f"What are the advantages and disadvantages of {input.topic}?",
            f"Give an example of {input.topic} in real life.",
        ],
        "hard": [
            f"Analyze the impact of {input.topic} on society.",
            f"Compare and contrast {input.topic} with related concepts.",
            f"Design a solution using {input.topic} principles.",
        ]
    }
    
    questions = question_templates.get(input.difficulty, question_templates["medium"])
    selected_questions = questions[:input.num_questions]
    
    return QuizGeneratorOutput(
        questions=selected_questions,
        topic=input.topic,
        difficulty=input.difficulty
    )

# Create agent
TUTOR_PROMPT = """
You are an encouraging and knowledgeable educational tutor.

Your capabilities:
1. Answer study questions using study_tool
2. Perform mathematical calculations using calculate
3. Generate quiz questions using quiz_generator_tool
4. Provide explanations and examples

Guidelines:
- Be patient and encouraging
- Explain concepts clearly with examples
- Use the Socratic method to guide learning
- Provide step-by-step solutions for problems
- Encourage critical thinking
- Celebrate learning achievements
"""

agent = AgentClient(
    model=model,
    system_prompt=TUTOR_PROMPT,
    tools=[study_tool, calculate, quiz_generator_tool]
).create_agent()

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content="📚 Hello! I'm your AI tutor. I'm here to help you learn and understand new concepts. What would you like to study today?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()
```

---

## 6. Personal Finance Assistant

### Scenario
Tạo một assistant để giúp quản lý tài chính cá nhân và đưa ra lời khuyên.

### Implementation

```python
# finance_assistant.py
import os
import chainlit as cl
from utils.basetools import calculate, CalculationInput, http_tool, HttpRequest
from llm.base import AgentClient

# Custom budget analysis tool
class BudgetAnalysisInput(BaseModel):
    income: float = Field(..., description="Monthly income")
    expenses: Dict[str, float] = Field(..., description="Monthly expenses by category")
    savings_goal: float = Field(..., description="Monthly savings goal")

class BudgetAnalysisOutput(BaseModel):
    total_expenses: float = Field(..., description="Total monthly expenses")
    remaining_income: float = Field(..., description="Income after expenses")
    savings_potential: float = Field(..., description="Potential savings")
    recommendations: List[str] = Field(..., description="Budget recommendations")

def budget_analysis_tool(input: BudgetAnalysisInput) -> BudgetAnalysisOutput:
    """Analyze budget and provide recommendations."""
    
    total_expenses = sum(input.expenses.values())
    remaining_income = input.income - total_expenses
    
    recommendations = []
    
    if remaining_income >= input.savings_goal:
        recommendations.append("Great! You're meeting your savings goal.")
    else:
        shortage = input.savings_goal - remaining_income
        recommendations.append(f"You need to reduce expenses by ${shortage:.2f} to meet your savings goal.")
    
    # Analyze expense categories
    for category, amount in input.expenses.items():
        percentage = (amount / input.income) * 100
        if percentage > 30 and category.lower() != "housing":
            recommendations.append(f"Consider reducing {category} expenses (currently {percentage:.1f}% of income).")
    
    return BudgetAnalysisOutput(
        total_expenses=total_expenses,
        remaining_income=remaining_income,
        savings_potential=max(0, remaining_income),
        recommendations=recommendations
    )

# Investment calculator tool
class InvestmentCalculatorInput(BaseModel):
    principal: float = Field(..., description="Initial investment amount")
    monthly_contribution: float = Field(..., description="Monthly contribution")
    annual_return: float = Field(..., description="Expected annual return (as percentage)")
    years: int = Field(..., description="Number of years")

class InvestmentCalculatorOutput(BaseModel):
    final_amount: float = Field(..., description="Final investment value")
    total_contributions: float = Field(..., description="Total contributions made")
    interest_earned: float = Field(..., description="Interest earned")
    breakdown: Dict[str, float] = Field(..., description="Year-by-year breakdown")

def investment_calculator_tool(input: InvestmentCalculatorInput) -> InvestmentCalculatorOutput:
    """Calculate investment growth over time."""
    
    monthly_rate = input.annual_return / 100 / 12
    total_months = input.years * 12
    
    # Calculate future value with monthly contributions
    future_value = input.principal * (1 + monthly_rate) ** total_months
    
    if monthly_rate > 0:
        monthly_contribution_value = input.monthly_contribution * (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
    else:
        monthly_contribution_value = input.monthly_contribution * total_months
    
    final_amount = future_value + monthly_contribution_value
    total_contributions = input.principal + (input.monthly_contribution * total_months)
    interest_earned = final_amount - total_contributions
    
    return InvestmentCalculatorOutput(
        final_amount=final_amount,
        total_contributions=total_contributions,
        interest_earned=interest_earned,
        breakdown={"Note": "Detailed breakdown available upon request"}
    )

# Create agent
FINANCE_PROMPT = """
You are a knowledgeable personal finance assistant.

Your capabilities:
1. Analyze budgets using budget_analysis_tool
2. Calculate investments using investment_calculator_tool
3. Perform financial calculations using calculate
4. Provide financial advice and tips

Guidelines:
- Provide practical, actionable advice
- Be encouraging about financial goals
- Explain financial concepts clearly
- Emphasize the importance of emergency funds
- Suggest diversification for investments
- Remind users this is educational information, not professional advice
"""

agent = AgentClient(
    model=model,
    system_prompt=FINANCE_PROMPT,
    tools=[budget_analysis_tool, investment_calculator_tool, calculate]
).create_agent()

@cl.on_message
async def main(message: cl.Message):
    response = await agent.run(message.content)
    await cl.Message(content=str(response.output)).send()
```

---

## Running the Examples

### 1. Setup Environment
```bash
# Install dependencies
pip install .

# Set environment variables
export GEMINI_API_KEY="your_api_key"
export OPENAI_API_KEY="your_openai_key"
export MILVUS_URI="http://localhost:19530"
```

### 2. Run Individual Examples
```bash
# Customer service bot
chainlit run customer_service_bot.py

# E-commerce support
chainlit run ecommerce_support_agent.py

# Technical documentation assistant
chainlit run tech_doc_assistant.py

# HR assistant
chainlit run hr_assistant.py

# Educational tutor
chainlit run educational_tutor.py

# Personal finance assistant
chainlit run finance_assistant.py
```

### 3. Customization Tips

1. **Data Sources**: Replace CSV files with your own data
2. **System Prompts**: Customize prompts for your domain
3. **Tools**: Add or remove tools based on needs
4. **UI**: Modify Chainlit interface for branding
5. **Integration**: Connect with existing systems via APIs

### 4. Advanced Features

```python
# Add authentication
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Implement your authentication logic
    return cl.User(identifier=username, metadata={"role": "user"})

# Add file upload
@cl.on_chat_start
async def on_chat_start():
    files = await cl.AskFileMessage(
        content="Please upload your document for analysis.",
        accept=["text/plain", "application/pdf"]
    ).send()
    
    # Process uploaded files
    for file in files:
        # Handle file processing
        pass
```

Những examples này cung cấp một foundation mạnh mẽ cho việc xây dựng các AI agents chuyên biệt cho nhiều domains khác nhau!

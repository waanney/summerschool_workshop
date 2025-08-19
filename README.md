# AI Agent for High School Students - Summer School Workshop

## Overview

This project is an AI Agent system designed for high school students, utilizing modern AI technologies to create an intelligent chatbot that can answer admission questions and support students.

> **Official Reference Materials**: [EAAI AI Agent for High School Students Materials Official 2025](./EAAI_AI_Agent_for_High_School_Students_Materials_Official_2025.pdf)

## Key Features

- **AI Chatbot**: Intelligent chatbot powered by Gemini AI model
- **FAQ System**: Frequently Asked Questions system with vector search
- **Memory Management**: Conversation memory management with Redis cache
- **Email Integration**: Automated email sending integration
- **Vector Database**: Using Milvus for storing and searching vector embeddings
- **Web Interface**: Web interface built with Chainlit

## Installation and Setup

> 📖 **Handbook Reference**: Section 2 - Environment Setup

### System Requirements

- Python 3.12+
- Redis server
- Milvus vector database

### 1. Clone repository

> 📖 **Handbook Reference**: Section 2.2 - Getting Started

```bash
git clone https://github.com/user/summerschool_workshop.git
cd summerschool_workshop
```

### 2. Install dependencies
#### Using UV (Recommended):
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

#### Or using pip:
```bash
pip install -e .
```

### 3. Environment Configuration

> 📖 **Handbook Reference**: Section 2.5 - The .env File

Create `.env` file from template:

```bash
cp .env.example .env
```

Update environment variables in `.env`:

```env
GEMINI_API_KEY=
MILVUS_URI=
MILVUS_TOKEN=
```

### 4. Database Setup

> 📖 **Handbook Reference**: Section 2.3 - Redis-server and Section 5.3 - Database setup with Milvus

Start Milvus and Redis services locally or use cloud services.
Read more details in hands-on book.

## Building Your AI Agent - From Idea to Implementation
### Step 1: Conceptualize Your Agent
Before writing any code, clearly define:

**1. Agent's Purpose**
- What problem does your agent solve?
- Who are your target users?
- What are the main use cases?

**Example**: *"Create a university admission assistant that helps prospective students find information about courses, requirements, and application processes."*

**2. Define Agent Capabilities**
List specific tasks your agent should perform, for example:
- Answer FAQ about admission requirements
- Send application forms via email
- Search course catalogs
- Calculate GPA requirements
- Provide deadline reminders

**3. Identify Required Data Sources**
Base on your agent and create some data like this:
- FAQ documents (Excel/PDF)
- Course catalogs
- Application forms
- Student databases
- External APIs (university websites)

### Step 2: Data Collection and Preparation
**1. Gather Your Data**  
Find data on Google or reputable websites.

- Search on Google with keywords  
  - `site:kaggle.com [your topic] dataset`  
  - `[your topic] open dataset`  
  - `[your topic] csv file download`  

- Use trusted dataset websites  
  - Kaggle: https://www.kaggle.com/datasets  
  - Google Dataset Search: https://datasetsearch.research.google.com  
  - UCI ML Repository: https://archive.ics.uci.edu/ml 

- Use public APIs  
  - OpenWeather API: https://openweathermap.org/api  
  - Spotify API: https://developer.spotify.com  
  - Twitter API: https://developer.twitter.com  
  - News API: https://newsapi.org  

- Academic and research data sources  
  - Harvard Dataverse: https://dataverse.harvard.edu  
  - Zenodo: https://zenodo.org  
  - IEEE DataPort: https://ieee-dataport.org  
  - Figshare: https://figshare.com  

- Community-sourced datasets  
  - Reddit r/datasets: https://www.reddit.com/r/datasets  
  - Awesome Public Datasets: https://github.com/awesomedata/awesome-public-datasets  

- Web scraping (if no APIs are available)  
  - Use Python libraries: BeautifulSoup, Selenium, Scrapy  
  - Check website’s Terms of Service before scraping


**2. Data Sources**
Save your data in `src/data/mock_data`, for example:
- `university_faq.xlsx` - Common questions and answers
- `course_catalog.pdf` - Available courses and requirements

### Step 3: Database Design and Setup

> 📖 **Handbook Reference**: Section 4 - Dataset Construction and Section 6.2 (Step 1 and 2) - Practical Implementation

**1. Plan Your Collections**
For our university admission agent:
```python
# Collection naming strategy
collections = {
    "university_faq": "General admission questions",
    "course_catalog": "Course information and requirements", 
    "application_info": "Application procedures and forms",
    "scholarship_info": "Financial aid and scholarship data"
}
```

**2. Database Collection Setup**
In your workflow file, you'll handle indexing directly:
```python
# In workflow/your_agent.py - Run once for setup
from data.milvus.indexing import MilvusIndexer

# Setup collections (run only once)
def setup_database():
    # FAQ Collection
    faq_indexer = MilvusIndexer(
        collection_name="university_faq",
        faq_file="src/data/mock_data/university_faq.xlsx"
    )
    faq_indexer.run()
    
    # Course Catalog Collection  
    course_indexer = MilvusIndexer(
        collection_name="course_catalog",
        faq_file="src/data/mock_data/courses.xlsx" 
    )
    course_indexer.run()

# Uncomment and run this function once, then comment it out
```

### Step 4: Tool Development

> 📖 **Handbook Reference**: Section 5.4.2 - Create Tools and Section 6.2 (Step 4.4 and Step 4.5)

**1. Analyze Existing MCP Tools**
Study available tools in `src/utils/basetools/`:
- `faq_tool.py` - Vector search in FAQ database
- `send_email_tool.py` - Email automation
- `file_reading_tool.py` - Document processing
- `search_web_tool.py` - Web search capabilities
- `calculator_tool.py` - Mathematical calculations

**2. Design Your Custom Tools**
**All custom tools go in `src/utils/basetools/`** following existing patterns.

**Example: Course Search Tool**
Create `src/utils/basetools/course_search_tool.py`:
```python
from pydantic import BaseModel
from typing import List, Optional
from data.milvus.milvus_client import MilvusClient

class CourseSearchInput(BaseModel):
    query: str
    program_type: Optional[str] = None
    gpa_requirement: Optional[float] = None

def create_course_search_tool(collection_name: str = "course_catalog"):
    """Create a tool to search university courses"""
    
    def search_courses(input_data: CourseSearchInput) -> str:
        try:
            # Use existing MilvusClient pattern
            client = MilvusClient(collection_name=collection_name)
            results = client.search(
                query_text=input_data.query,
                top_k=5
            )
            
            if not results:
                return f"No courses found for: {input_data.query}"
            
            response = f"Found {len(results)} courses:\n\n"
            for result in results:
                response += f"• {result['course_name']}\n"
                response += f"  Requirements: {result['requirements']}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error searching courses: {str(e)}"
    
    return search_courses
```

**Example: GPA Calculator Tool**
Create `src/utils/basetools/gpa_calculator_tool.py`:
```python
from pydantic import BaseModel
from typing import List

class GPACalculatorInput(BaseModel):
    grades: List[str]  # ["A", "B+", "C", ...]
    credit_hours: List[int]  # [3, 4, 2, ...]

def gpa_calculator_tool(input_data: GPACalculatorInput) -> str:
    """Calculate GPA based on grades and credit hours"""
    try:
        grade_points = {
            "A": 4.0, "A-": 3.7, 
            "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D+": 1.3, "D": 1.0, "F": 0.0
        }
        
        if len(input_data.grades) != len(input_data.credit_hours):
            return "Error: Number of grades must match number of credit hours"
        
        total_points = sum(
            grade_points.get(grade, 0) * credits 
            for grade, credits in zip(input_data.grades, input_data.credit_hours)
        )
        total_credits = sum(input_data.credit_hours)
        
        if total_credits == 0:
            return "Error: Total credit hours cannot be zero"
        
        gpa = total_points / total_credits
        return f"Your calculated GPA is: {gpa:.2f}/4.0"
        
    except Exception as e:
        return f"Error calculating GPA: {str(e)}"
```

**3. Tool Integration Pattern**
All tools in `src/utils/basetools/` follow this structure:
```
src/utils/basetools/your_tool_name.py
├── Input Model (Pydantic BaseModel)
├── Tool Function with error handling
├── Use existing clients (MilvusClient, etc.)
└── Return Formatted String Response
```

**Key Points:**
- Always add tools to `src/utils/basetools/` directory
- Follow existing patterns from other tools in the folder
- Use existing clients like `MilvusClient`, `RedisCache`
- Include proper error handling
- Return formatted string responses

### Step 5: Agent Workflow Integration

> 📖 **Handbook Reference**: Section 5.4.4 - Multi Agent System and Section 6.2 (Step 4.6 and 4.7 and step 5)

**1. Create Your Agent File**
Create a new workflow file like `workflow/university_agent.py`:

```python
from data.milvus.indexing import MilvusIndexer
import os
from llm.base import AgentClient
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
import chainlit as cl
from data.cache.memory_handler import MessageMemoryHandler

# Import your custom tools from basetools
from utils.basetools.faq_tool import create_faq_tool
from utils.basetools.course_search_tool import create_course_search_tool
from utils.basetools.gpa_calculator_tool import gpa_calculator_tool
from utils.basetools.send_email_tool import send_email_tool

# Database setup (run only once, then comment out)
def setup_database():
    # FAQ Collection
    faq_indexer = MilvusIndexer(
        collection_name="university_faq",
        faq_file="src/data/mock_data/university_faq.xlsx"
    )
    faq_indexer.run()
    
    # Course Collection
    course_indexer = MilvusIndexer(
        collection_name="course_catalog",
        faq_file="src/data/mock_data/courses.xlsx"
    )
    course_indexer.run()

# Uncomment to run database setup once, then comment out
# setup_database()

# Custom prompt
UNIVERSITY_AGENT_PROMPT = """
You are a University Admission Assistant AI agent.

Your capabilities:
1. Answer questions about university admission requirements
2. Search for course information and prerequisites  
3. Calculate GPA based on grades provided
4. Send application forms and information via email
5. Provide guidance on application deadlines

Always be helpful, accurate, and ask clarifying questions when needed.
"""

# Initialize model and memory
provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
model = GeminiModel('gemini-2.0-flash', provider=provider)
memory_handler = MessageMemoryHandler()

# Initialize your tools
faq_tool = create_faq_tool(collection_name="university_faq")
course_tool = create_course_search_tool(collection_name="course_catalog")

# Initialize agent with all tools
agent = AgentClient(
    model=model,
    system_prompt=UNIVERSITY_AGENT_PROMPT,
    tools=[faq_tool, course_tool, gpa_calculator_tool, send_email_tool],
    memory_handler=memory_handler
)

@cl.on_chat_start
async def start():
    cl.user_session.set("agent", agent)
    await cl.Message(
        content="Hello! I'm your University Admission Assistant. I can help you with:\n"
                "• Admission requirements and FAQ\n" 
                "• Course search and prerequisites\n"
                "• GPA calculations\n"
                "• Application forms and deadlines\n\n"
                "What would you like to know?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    response = await agent.run(message.content)
    await cl.Message(content=response).send()
```

**2. Test Your Agent**
```bash
# Run your custom agent
uv run chainlit run workflow/university_agent.py -w
```


## Project Structure

> 📖 **Handbook Reference**: Section 6.1 - Folder Structure Overview

```
summerschool_workshop/
├── src/
│   ├── data/
│   │   ├── cache/              # Redis cache and memory handling
│   │   ├── embeddings/         # Embedding engine
│   │   ├── milvus/            # Milvus vector database
│   │   ├── prompts/           # AI prompts
│   │   └── mock_data/         # Sample data (FAQ)
│   ├── handlers/              # Error handlers
│   ├── llm/                   # LLM base classes
│   ├── utils/
│   │   └── basetools/         # Basic tools (FAQ, email, etc.)
│   └── workflow/              # Main application workflow
├── config/                    # Configuration files
├── logs/                      # Log files
└── pyproject.toml            # Project dependencies
```
## Documentation References

- **Official Paper**: See attached PDF file in repository
- **Milvus Documentation**: https://milvus.io/docs
- **Chainlit Documentation**: https://docs.chainlit.io
- **Pydantic AI Documentation**: https://ai.pydantic.dev
- **Gemini AI Documentation**: https://ai.google.dev



## In Addition

We've pre-packaged a basic setup that allows you to get started quickly using Docker.

### Quick Start with Docker

If you want to skip the manual setup process and get the AI Agent running immediately, you can use our pre-configured Docker environment:

1. **Clone the repository**
   ```bash
   git clone https://github.com/user/repo.git
   cd repo
   ```

2. **Set up environment variables**
   ```bash
   make setup
   # Edit .env file with your API keys
   ```

3. **Start all services**
   ```bash
   make build
   ```

4. **Access the application**
   - **Chainlit Interface**: http://localhost:8000
   - **MinIO Console**: http://localhost:9001

5. **Run the chatbot**
   ```
   make run-chatbot
   ```

This Docker setup includes:
- **Milvus vector database** with pre-configured collections
- **Redis cache** for memory management
- **Web application** with Chainlit interface
- **Sample data** already indexed and ready to use

Perfect for workshops, demos, or quick prototyping!

> 💡 **Note**: The Docker setup is ideal for getting started quickly, but for production use or extensive customization, we recommend following the manual installation steps above.

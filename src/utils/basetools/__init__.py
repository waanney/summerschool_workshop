"""
Base tools and utilities package for the summerschool workshop.

This package provides a comprehensive collection of utility tools and functions
for various common tasks including:

- Text classification and semantic search
- Document processing and chunking
- File operations (reading, merging, searching)
- HTTP requests and web scraping
- Email sending and communication
- Calculator and mathematical operations
- FAQ and knowledge base management

All tools follow strong typing principles with proper input/output models,
comprehensive error handling, and detailed documentation. Each tool is designed
to be modular, reusable, and maintainable following enterprise software standards.

Key Features:
- Strong typing with no use of 'Any' types
- Comprehensive docstrings for all functions and classes
- Enum-based configuration for better type safety
- Structured input/output models using Pydantic
- Proper error handling and status reporting
- Factory functions for tool configuration
- Multilingual language support where applicable

Usage:
    from src.utils.basetools import classification_tool, faq_tool, http_tool

    # Use tools with proper input models
    result = classification_tool(SearchInput(query="text"), labels=["label1", "label2"])
"""

# Import all tools for easy access
from .classfication_tool import (
    SearchInput as ClassificationInput,
    SearchOutput as ClassificationOutput,
    classify_scholarship_http,
    ClassificationMode,
)

from .semantic_splitter import (
    SemanticSplitter,
    load_txt,
    load_pdf,
    load_docx,
    Language,
    FileType,
)

from .document_chunking_tool import (
    DocumentChunkingInput,
    DocumentChunkingOutput,
    document_chunking_tool,
    DocumentStatus,
)

from .faq_tool import (
    SearchInput as FAQSearchInput,
    SearchOutput as FAQSearchOutput,
    FAQResult,
    faq_tool,
    create_faq_tool,
    SearchMode,
)

from .file_reading_tool import (
    FileContentOutput,
    read_file_tool,
    create_read_file_tool,
    FileType as FileReadingType,
    FileStatus as FileReadingStatus,
)

from .http_tool import (
    HttpRequest,
    HttpResponse,
    http_tool,
    BodyType,
    ResponseType,
    HTTPMethod,
)

from .merge_files_tool import (
    MergeInput,
    MergeOutput,
    merge_files_tool,
    MergeStatus,
)

from .search_in_file_tool import (
    SearchInput as FileSearchInput,
    SearchOutput as FileSearchOutput,
    SearchResult as FileSearchResult,
    search_in_file,
    create_search_in_file_tool,
    SearchMode as FileSearchMode,
    SearchStatus as FileSearchStatus,
)

from .search_relevant_document_tool import (
    SearchRelevantDocumentInput,
    SearchRelevantDocumentOutput,
    DocumentResult,
    search_relevant_document,
    SearchStatus as DocumentSearchStatus,
)

from .search_web_tool import (
    SearchInput as WebSearchInput,
    SearchOutput as WebSearchOutput,
    SearchResult as WebSearchResult,
    search_web,
    SearchEngine,
    SearchStatus as WebSearchStatus,
)

from .send_email_tool import (
    EmailToolInput,
    EmailToolOutput,
    send_email_tool,
    create_send_email_tool,
    EmailProvider,
    EmailStatus,
)

from .calculator_tool import (
    CalculatorTool,
    CalculationInput,
    CalculationOutput,
    BasicOperationInput,
    BasicOperationOutput,
    TrigonometricInput,
    TrigonometricOutput,
    LogarithmInput,
    LogarithmOutput,
    MemoryOperation,
    MemoryOutput,
    HistoryOutput,
    OperationType,
    calculate,
    calculate_expression,
    basic_math,
    trigonometry,
    logarithm,
    calculator_memory,
    get_calculation_history,
    clear_calculation_history,
)

# Version information
__version__ = "1.0.0"
__author__ = "Summerschool Workshop Team"
__description__ = "Base tools and utilities for the summerschool workshop project"

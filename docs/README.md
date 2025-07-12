# Summerschool Workshop Documentation

Chào mừng đến với tài liệu hướng dẫn chi tiết cho Summerschool Workshop - một hệ thống AI Agent platform tích hợp vector search, memory management, và conversational AI.

## 📚 Tài liệu

### Bắt đầu nhanh
- [🚀 Hướng dẫn cài đặt](setup.md) - Cài đặt và cấu hình hệ thống
- [⚡ Quick Start](quickstart.md) - Chạy demo đầu tiên trong 5 phút
- [🏗️ Kiến trúc hệ thống](architecture.md) - Tổng quan về architecture

### Phát triển
- [🔧 API Reference](api.md) - Tài liệu API chi tiết
- [🛠️ Tools và Extensions](tools.md) - Hướng dẫn sử dụng và tạo tools
- [💡 Examples](examples.md) - Các ví dụ thực tế và use cases

### Vận hành
- [🌍 Environment Configuration](environment.md) - Cấu hình môi trường
- [🔍 MCP Tools](mcp.md) - Model Context Protocol integration
- [🐛 Troubleshooting](troubleshooting.md) - Giải quyết vấn đề thường gặp

## 🎯 Tính năng chính

### 🧠 AI Agent Platform
- **PydanticAI Integration**: Framework hiện đại cho AI agents
- **Google Gemini 2.0**: LLM mạnh mẽ với context window lớn
- **Tool System**: Extensible tool system cho custom functionality
- **Memory Management**: Short-term memory với Redis

### 🔍 Vector Search
- **Milvus Vector DB**: High-performance vector database
- **Hybrid Search**: Kết hợp semantic và keyword search
- **BM25 Integration**: Full-text search với sparse vectors
- **Dynamic Schema**: Tự động tạo schema từ dữ liệu

### 💬 Conversational UI
- **Chainlit Integration**: Modern chat interface
- **Session Management**: Multi-user session support
- **Real-time Updates**: Live conversation updates
- **File Upload**: Support file upload và processing

### 🛠️ Developer Tools
- **Built-in Tools**: FAQ, HTTP, Email, Calculator, File tools
- **Custom Tools**: Easy-to-create custom tools
- **API Integration**: RESTful API support
- **Testing Framework**: Comprehensive testing support

## 🚀 Use Cases

### 🎓 Education
- **Student Support**: Trả lời câu hỏi về khóa học, học bổng
- **Academic Assistant**: Hỗ trợ học tập và research
- **FAQ Management**: Quản lý câu hỏi thường gặp

### 🏢 Enterprise
- **Customer Support**: Automated customer service
- **HR Assistant**: Hỗ trợ nhân sự và policies
- **Knowledge Management**: Tổ chức và tìm kiếm knowledge base

### 🛍️ E-commerce
- **Product Support**: Hỗ trợ sản phẩm và dịch vụ
- **Order Management**: Tra cứu đơn hàng và tracking
- **Sales Assistant**: Hỗ trợ bán hàng và marketing

### 💼 Professional Services
- **Legal Assistant**: Hỗ trợ legal research
- **Financial Advisor**: Tư vấn tài chính cá nhân
- **Technical Support**: Hỗ trợ kỹ thuật và documentation

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
│                     (Chainlit Web UI)                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      Agent Layer                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  PydanticAI     │  │  Tool System    │  │  Memory Handler │ │
│  │  (Orchestrator) │  │  (Extensions)   │  │  (Context)      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      Data Layer                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Milvus Vector  │  │  Redis Cache    │  │  Embedding      │ │
│  │  Database       │  │  (Memory)       │  │  Engine         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                   External Services                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Google Gemini  │  │  OpenAI API     │  │  SMTP/Email     │ │
│  │  (LLM)          │  │  (Embeddings)   │  │  (Notifications)│ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Core Components

### 🤖 Agent System
- **AgentClient**: Wrapper cho PydanticAI
- **System Prompts**: Customizable agent personalities
- **Tool Integration**: Seamless tool access
- **Context Management**: Conversation context handling

### 💾 Data Management
- **MilvusClient**: Vector database client
- **ShortTermMemory**: Redis-based memory
- **EmbeddingEngine**: Text embedding generation
- **MilvusIndexer**: Data indexing utilities

### 🔧 Tool Ecosystem
- **FAQ Tool**: Knowledge base search
- **HTTP Tool**: API integration
- **Email Tool**: Email notifications
- **Calculator Tool**: Mathematical operations
- **File Tools**: File processing

## 🛣️ Roadmap

### 📅 Upcoming Features
- [ ] **Multi-language Support**: Hỗ trợ nhiều ngôn ngữ
- [ ] **Advanced Analytics**: Analytics và reporting
- [ ] **Plugin System**: Plugin architecture
- [ ] **Cloud Deployment**: One-click cloud deployment
- [ ] **API Gateway**: Advanced API management

### 🔄 Continuous Improvements
- [ ] **Performance Optimization**: Cải thiện performance
- [ ] **Security Enhancements**: Tăng cường bảo mật
- [ ] **UI/UX Improvements**: Cải thiện giao diện
- [ ] **Documentation Updates**: Cập nhật tài liệu

## 🤝 Contributing

Chúng tôi hoan nghênh mọi đóng góp cho dự án!

### 🐛 Bug Reports
- Sử dụng GitHub Issues
- Cung cấp thông tin chi tiết về lỗi
- Include logs và error messages

### 💡 Feature Requests
- Mô tả tính năng cần thiết
- Giải thích use case và benefits
- Thảo luận implementation approach

### 🔀 Pull Requests
- Fork repository
- Tạo feature branch
- Viết tests cho code mới
- Submit pull request với mô tả chi tiết

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

Nếu bạn cần hỗ trợ:

1. **📖 Documentation**: Đọc tài liệu chi tiết
2. **🐛 Issues**: Tạo GitHub issue cho bugs
3. **💬 Discussions**: Tham gia GitHub discussions
4. **📧 Email**: Liên hệ qua email cho support

---

**Happy Building! 🚀**

*Chúc bạn xây dựng những AI agents tuyệt vời với Summerschool Workshop!*

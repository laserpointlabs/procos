# ProcOS - Process-Oriented Operating System

## 🎯 **What is ProcOS?**

ProcOS is a revolutionary **process-driven virtual operating system** where BPMN (Business Process Model and Notation) serves as the "kernel language." Unlike traditional operating systems that manage files and programs, ProcOS manages and executes business processes as first-class citizens.

## 🏗️ **Core Philosophy: "Processes Drive Everything"**

- **BPMN as Kernel Language**: All system operations are defined as BPMN processes
- **Minimal Microkernel**: Ultra-lightweight Python bootstrap that starts Camunda
- **External Task Pattern**: Decoupled workers handle specific tasks (AI, HTTP, email, etc.)
- **Process-First Design**: Even system management is handled through BPMN workflows

## 🚀 **Quick Start**

```bash
# Clone and setup
git clone <your-repo-url> procos
cd procos

# Start the system (one command!)
./procos.sh start

# Deploy sample processes (optional)
python scripts/deploy_processes.py

# Test AI query workflow
curl -X POST localhost:8080/engine-rest/process-definition/key/ai_query/start \
  -H "Content-Type: application/json" \
  -d '{"variables": {"query": {"value": "Hello ProcOS!"}}}'
```

## 🧪 Development

- Python 3.11+
- Create `.env` from `env.example`
- Manage stack: `./procos.sh start|stop|status|logs|test|down`
- Run tests: `make pytest`
- CI runs lint and tests on push/PR

## 📁 **Repository Structure**

```
procos/
├── README.md                    # This file
├── docker-compose.yml           # Infrastructure setup  
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
│
├── src/                         # Core implementation
│   ├── microkernel/            # Python microkernel
│   ├── workers/                # External task workers
│   └── processes/              # BPMN process definitions
│
├── tests/                      # Testing framework
│   ├── unit/                   # Unit tests
│   └── integration/            # End-to-end tests
│
├── scripts/                    # Automation scripts
│   ├── start.sh               # One-command startup
│   ├── deploy_processes.py    # BPMN deployment
│   └── health_check.py        # System monitoring
│
├── docs/                       # Documentation
│   ├── architecture/          # Design specifications
│   ├── api/                   # API documentation
│   └── deployment/            # Deployment guides
│
└── examples/                   # Sample processes and workflows
```

## 🧠 **Key Components**

### **1. Microkernel (`src/microkernel/`)**
Ultra-minimal Python bootstrap that:
- Validates environment and dependencies
- Starts Camunda BPMN engine
- Deploys root orchestration processes
- Monitors system health

### **2. Workers (`src/workers/`)**
Specialized external task handlers:
- **Generic Worker**: HTTP requests, email, file operations
- **AI Worker**: OpenAI/Ollama integration for intelligent processing
- **Custom Workers**: Domain-specific business logic

### **3. Processes (`src/processes/`)**
BPMN process definitions:
- **System Orchestrator**: Root process managing system operations
- **User Workflows**: Business-specific process templates
- **Management Processes**: System administration and monitoring

## 🎓 **Learning Resources**

### **For Beginners**
- 📚 **[ProcOS for Dummies](./docs/architecture/ProcOS_For_Dummies.md)** - Fun, accessible introduction with analogies
- 🎯 **[Quick Start Tutorial](./examples/README.md)** - Step-by-step first process

### **For Developers**
- 🔧 **[Implementation Guide Part 1](./docs/architecture/ProcOS_Implementation_Guide_Part1.md)** - Foundation and setup
- 🔧 **[Implementation Guide Part 2](./docs/architecture/ProcOS_Implementation_Guide_Part2.md)** - Advanced integration
- 🏛️ **[Architecture Specification](./docs/architecture/ProcOS_Architecture_Specification.md)** - Complete technical specification

### **For System Architects**
- 📊 **[Architecture Overview](./docs/architecture/README.md)** - High-level system design
- 🔗 **[Integration Patterns](./docs/api/README.md)** - External system integration
- 🚀 **[Deployment Guide](./docs/deployment/README.md)** - Production deployment strategies

## 💡 **Example: Simple AI Query Process**

```xml
<!-- ai_query.bpmn -->
<bpmn:process id="ai_query" name="AI Query Process">
  <bpmn:startEvent id="start"/>
  <bpmn:serviceTask id="process_query" name="Process AI Query">
    <bpmn:extensionElements>
      <camunda:properties>
        <camunda:property name="topic" value="ai_query"/>
        <camunda:property name="type" value="external"/>
      </camunda:properties>
    </bpmn:extensionElements>
  </bpmn:serviceTask>
  <bpmn:endEvent id="end"/>
</bpmn:process>
```

## 🔄 **Development Status**

- ✅ **Documentation Complete**: Architecture and implementation guides ready
- 🔨 **In Development**: Core microkernel and basic workers
- 📋 **Planned**: Advanced workers and production deployment
- 🎯 **Goal**: MVP backend within 1 week

## 📋 **For New Team Members & Development Sessions**

**NEW TO THE PROJECT?** Start here: **[PROJECT_CONTEXT_TRANSFER.md](./PROJECT_CONTEXT_TRANSFER.md)**

This comprehensive document provides:
- 🎯 **Complete Project Context**: What ProcOS is and why it exists
- 🔄 **Migration Story**: How we got from DADMS to ProcOS
- 🏗️ **Current Architecture**: What's built, what's TODO
- 🚀 **Development Guide**: Immediate next steps and workflows
- 🧠 **Technical Decisions**: Key choices and patterns
- 💡 **AI Assistant Instructions**: Perfect for new development sessions

## 🤝 **Contributing**

1. **Read the context**: Start with [PROJECT_CONTEXT_TRANSFER.md](./PROJECT_CONTEXT_TRANSFER.md)
2. **Learn the basics**: [ProcOS for Dummies](./docs/architecture/ProcOS_For_Dummies.md)
3. **Technical deep-dive**: [Implementation Guide](./docs/architecture/ProcOS_Implementation_Guide_Part1.md)
4. **Set up locally**: Follow the [Quick Start Guide](./QUICK_START.md)
5. **Run tests**: `pytest tests/` (when implemented)
6. **Submit PRs**: Focus on workers and process definitions

## 📄 **License**

[License details to be added]

---

**ProcOS: Where Business Processes Are the Operating System** 🚀
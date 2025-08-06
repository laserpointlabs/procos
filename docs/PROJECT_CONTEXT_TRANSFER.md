# ProcOS Project Context & Transfer Document

**Date**: January 2025  
**Version**: 1.0  
**Purpose**: Complete briefing document for new development sessions  

---

## 🎯 **Project Overview**

### **What is ProcOS?**
ProcOS (Process-Oriented Operating System) is a revolutionary **process-driven backend architecture** where BPMN (Business Process Model and Notation) serves as the "kernel language." Unlike traditional operating systems that manage files and programs, ProcOS manages and executes business processes as first-class citizens.

### **Core Innovation**
- **BPMN as Kernel Language**: All system operations defined as visual BPMN workflows
- **Microkernel Architecture**: Ultra-minimal Python bootstrap (< 500 lines)
- **External Task Pattern**: Decoupled workers handle specific operations
- **Process-First Design**: Even system management runs through BPMN processes

---

## 🔄 **Migration Story: From DADMS to ProcOS**

### **The Problem We Solved**
We had a complex DADMS (Decision Analysis and Decision Management System) with tightly-coupled frontend and backend, making rapid backend development difficult. The React UI complexity was slowing down backend innovation.

### **The Solution: Repository Split**
**Decision**: Create a separate ProcOS repository for clean backend development
- ✅ **New Repo**: `https://github.com/laserpointlabs/procos`
- ✅ **Backend Focus**: Process-driven architecture without frontend constraints
- ✅ **Future Integration**: API-first design for eventual DADMS UI connection

### **What We Preserved**
- 🧠 **Complete Documentation**: All ProcOS architecture specs migrated
- 📋 **Domain Knowledge**: Decision intelligence and process automation expertise  
- 🔗 **Integration Patterns**: External system connection strategies
- 👥 **Team Understanding**: Architectural vision and technical direction

---

## 🏗️ **Current Architecture Status**

### **✅ COMPLETED: Backend Foundation**

#### **🔬 Microkernel (READY)**
**File**: `src/microkernel/procos_kernel.py`
- **6-Phase Bootstrap**: Environment → Camunda → Processes → Monitor
- **Minimal Design**: Ultra-lightweight startup system
- **Health Monitoring**: Continuous system state checking
- **Signal Handling**: Graceful shutdown capabilities

#### **🔧 Generic Worker (OPERATIONAL)**  
**File**: `src/workers/generic_worker.py`
- **HTTP Operations**: GET, POST, PUT, DELETE requests
- **Email Integration**: SMTP-based email sending
- **File Operations**: Read, write, delete, exists checking
- **Data Processing**: Validation and transformation utilities

#### **🐳 Infrastructure (LIVE)**
**File**: `docker-compose.yml`
- **Camunda Engine**: BPMN execution platform (port 8080)
- **RabbitMQ**: Message broker (port 5672, admin 15672)
- **Redis**: Caching layer (port 6379)
- **Health Checks**: Automated service monitoring

#### **📋 System Orchestrator (DEPLOYED)**
**File**: `src/processes/system_orchestrator.bpmn`
- **Root Process**: Main system coordination workflow
- **External Tasks**: Worker management and health monitoring
- **Event-Driven**: Responds to user requests and system events

#### **🚀 Automation (COMPLETE)**
- **`./scripts/start.sh`**: One-command system startup
- **`./scripts/stop.sh`**: Graceful shutdown
- **`./scripts/health_check.py`**: Comprehensive system diagnostics

### **📋 TODO: Next Development Priorities**

#### **🤖 AI Worker (HIGH PRIORITY)**
- **OpenAI Integration**: GPT-4 API connectivity
- **Ollama Support**: Local LLM execution
- **Task Topics**: `ai_query`, `text_generation`, `analysis`
- **Template**: Copy and adapt `generic_worker.py`

#### **📊 Process Library (MEDIUM PRIORITY)**
- **User Management**: Authentication and authorization workflows
- **Document Processing**: Upload, analysis, storage processes
- **Decision Workflows**: Multi-step decision-making processes
- **Error Handling**: Robust failure recovery patterns

#### **🧪 Testing Framework (MEDIUM PRIORITY)**
- **Unit Tests**: Worker and microkernel testing
- **Integration Tests**: End-to-end process execution
- **Performance Tests**: Load and stress testing
- **CI/CD**: Automated testing pipeline

---

## 🌐 **Service Architecture Details**

### **Port Allocation**
| Service | Port | Purpose | Status |
|---------|------|---------|---------|
| Camunda Engine | 8080 | BPMN execution & REST API | ✅ LIVE |
| Camunda Cockpit | 8080/camunda | Visual process monitoring | ✅ LIVE |
| RabbitMQ AMQP | 5672 | Message broker | ✅ LIVE |
| RabbitMQ Admin | 15672 | Queue management UI | ✅ LIVE |
| Redis | 6379 | Caching layer | ✅ LIVE |

### **External Task Topics**
| Topic | Handler | Purpose | Status |
|-------|---------|---------|---------|
| `http_request` | Generic Worker | HTTP operations | ✅ READY |
| `email_send` | Generic Worker | Email sending | ✅ READY |
| `file_operation` | Generic Worker | File management | ✅ READY |
| `data_validation` | Generic Worker | Input validation | ✅ READY |
| `data_transform` | Generic Worker | Data processing | ✅ READY |
| `ai_query` | AI Worker | LLM integration | 📋 TODO |
| `system_initialization` | System Worker | Startup tasks | 📋 TODO |
| `health_monitoring` | Monitor Worker | System health | 📋 TODO |

---

## 📁 **Repository Structure Guide**

```
procos/                                    # 🎯 Main repository
├── 📄 README.md                          # Project overview
├── 🚀 QUICK_START.md                     # Immediate development guide
├── 📋 PROJECT_CONTEXT_TRANSFER.md        # This document
├── 🐳 docker-compose.yml                 # Infrastructure setup
├── 📦 requirements.txt                   # Python dependencies
├── ⚙️  env.example                       # Configuration template
│
├── 🧠 src/                               # Core implementation
│   ├── microkernel/                     # Bootstrap system
│   │   ├── procos_kernel.py             # ✅ Main microkernel
│   │   └── __init__.py                  # Package setup
│   ├── workers/                         # External task handlers
│   │   ├── generic_worker.py            # ✅ HTTP/email/files
│   │   ├── ai_worker.py                 # 📋 TODO: AI integration
│   │   └── __init__.py                  # Package setup
│   └── processes/                       # BPMN definitions
│       ├── system_orchestrator.bpmn     # ✅ Root process
│       ├── ai_query.bpmn                # 📋 TODO: AI workflow
│       └── user_management.bpmn         # 📋 TODO: Auth workflow
│
├── 🧪 tests/                            # Testing framework
│   ├── unit/                           # 📋 TODO: Unit tests
│   └── integration/                    # 📋 TODO: E2E tests
│
├── 🔧 scripts/                          # Automation utilities
│   ├── start.sh                        # ✅ System startup
│   ├── stop.sh                         # ✅ Graceful shutdown
│   ├── health_check.py                 # ✅ System diagnostics
│   └── deploy_processes.py             # 📋 TODO: BPMN deployment
│
└── 📚 docs/                             # Documentation
    ├── architecture/                   # Complete ProcOS specs
    │   ├── ProcOS_Architecture_Specification.md      # 🏛️ Full ARC42 spec
    │   ├── ProcOS_Implementation_Guide_Part1.md      # 🔧 Foundation guide
    │   ├── ProcOS_Implementation_Guide_Part2.md      # 🔧 Advanced guide
    │   ├── ProcOS_For_Dummies.md                     # 🎓 Beginner intro
    │   ├── DADMS_to_ProcOS_Migration_Decision.md     # 📋 Migration rationale
    │   └── README.md                                  # Architecture index
    ├── api/                            # 📋 TODO: API documentation
    └── deployment/                     # 📋 TODO: Production guides
```

---

## 🔗 **DADMS Frontend Integration Strategy**

### **Current State**
- **DADMS UI**: React application (scaffolded, not linked to ProcOS yet)
- **Location**: Separate from ProcOS repository
- **Status**: Ready for integration once ProcOS backend is stable

### **Integration Phases**

#### **Phase 1: Backend Stability (THIS WEEK)**
- ✅ **Microkernel**: Operational and tested
- 🔨 **AI Worker**: Core AI integration working
- 📋 **Basic Processes**: User authentication, document processing
- ✅ **API Documentation**: Clear endpoints for frontend integration

#### **Phase 2: API Integration (NEXT WEEK)**
- 🌐 **REST Endpoints**: Process-driven API design
- ⚡ **WebSocket Events**: Real-time process state updates
- 📊 **Status Monitoring**: Process execution visibility
- 🔗 **CORS Configuration**: Frontend connection setup

#### **Phase 3: React Integration (WEEK 3+)**
```javascript
// Example: Process-driven UI pattern
const processInstance = await procOS.startProcess('user_authentication', {
  username: formData.username,
  password: formData.password
});

// Real-time process updates
procOS.subscribeToProcess(processInstance.id, (event) => {
  switch(event.activityId) {
    case 'auth_success':
      setUser(event.variables.user);
      break;
    case 'auth_failed':
      setError(event.variables.errorMessage);
      break;
  }
});
```

#### **Phase 4: Full Migration (MONTH 2)**
- 🎨 **Component Library**: Process-aware React components
- 📊 **Process Dashboard**: Visual workflow monitoring
- 🔄 **State Synchronization**: BPMN variables ↔ React state
- 🚀 **Production Deployment**: Complete DADMS 2.0 system

---

## 🧠 **Key Technical Decisions**

### **Architecture Patterns**
- **Microkernel**: Minimal, focused bootstrap system
- **External Tasks**: Decoupled worker architecture
- **Event-Driven**: Message-based communication
- **Process-First**: BPMN workflows drive all operations

### **Technology Choices**
- **Process Engine**: Camunda (mature, production-ready)
- **Message Broker**: RabbitMQ (reliable, well-understood)
- **Caching**: Redis (fast, simple)
- **Language**: Python (team expertise, rapid development)
- **Containerization**: Docker (consistent environments)

### **Development Principles**
- **API-First**: Backend design independent of frontend
- **Documentation-Driven**: Comprehensive specs guide implementation
- **Test-Driven**: Quality assurance from day one
- **Process-Oriented**: Business logic visible in BPMN diagrams

---

## 🚀 **Quick Development Commands**

### **Start Development Session**
```bash
cd /home/jdehart/procos
./scripts/start.sh                    # Start all services
./scripts/health_check.py             # Verify system health
```

### **Access Services**
- **Camunda Cockpit**: http://localhost:8080/camunda
- **Process API**: http://localhost:8080/engine-rest
- **RabbitMQ Admin**: http://localhost:15672 (procos/procos123)

### **Test Basic Operations**
```bash
# Test process deployment
curl -X POST http://localhost:8080/engine-rest/process-definition/key/system_orchestrator/start

# Test external task polling
curl -X POST http://localhost:8080/engine-rest/external-task/fetchAndLock \
  -H "Content-Type: application/json" \
  -d '{"workerId": "test", "maxTasks": 1, "topics": [{"topicName": "http_request", "lockDuration": 30000}]}'
```

### **Development Workflow**
```bash
# Create feature branch
git checkout -b feature/ai-worker

# Make changes...
# Test locally...

# Commit and push
git add .
git commit -m "Add AI worker integration"
git push -u origin feature/ai-worker
```

---

## 🎯 **Immediate Next Steps**

### **Today (High Priority)**
1. **🧪 System Verification**: Run `./scripts/start.sh` and verify all services start correctly
2. **🔧 AI Worker Development**: Create `src/workers/ai_worker.py` based on generic worker template
3. **📋 First Process**: Create a simple AI query BPMN process

### **This Week (Medium Priority)**
1. **🧪 Testing Framework**: Set up pytest and basic integration tests
2. **📊 Process Library**: Create common workflow templates
3. **📚 API Documentation**: Document all external task topics and REST endpoints

### **Next Week (Future Planning)**
1. **🌐 Frontend Integration**: Design API patterns for React connection
2. **📈 Performance**: Load testing and optimization
3. **🚀 Deployment**: Production deployment strategies

---

## 📋 **Common Issues & Solutions**

### **Startup Issues**
- **Camunda not starting**: Check Docker is running, ports not conflicted
- **Workers not connecting**: Verify RabbitMQ is healthy, check environment variables
- **Process deployment fails**: Ensure BPMN files are valid, check Camunda logs

### **Development Tips**
- **Use Camunda Cockpit**: Visual process monitoring and debugging
- **Check health regularly**: `./scripts/health_check.py` shows system status
- **Read the docs**: Comprehensive guides in `docs/architecture/`

### **Git Workflow**
- **Repository**: https://github.com/laserpointlabs/procos
- **Branch Strategy**: Feature branches for all development
- **Commit Messages**: Clear, descriptive commits with context

---

## 🏆 **Success Metrics**

### **Week 1 Goals**
- [ ] **5-Second Startup**: `./scripts/start.sh` gets everything running quickly
- [ ] **Basic AI Query**: End-to-end process from API call to AI response  
- [ ] **Error Recovery**: Graceful handling of common failure scenarios
- [ ] **Clear APIs**: Well-documented interfaces for frontend integration

### **MVP Definition**
- ✅ **Process Execution**: BPMN workflows run reliably
- 🔨 **Worker Ecosystem**: HTTP, AI, email, file operations (in progress)
- ✅ **Monitoring**: Health checks and system status
- 📋 **Integration Ready**: APIs for frontend connection (planned)

---

## 💡 **For New Team Members**

### **Getting Started**
1. **Read This Document**: Complete context understanding
2. **Read [ProcOS for Dummies](./docs/architecture/ProcOS_For_Dummies.md)**: Beginner-friendly introduction
3. **Follow [Quick Start Guide](./QUICK_START.md)**: Immediate development setup
4. **Review [Implementation Guide](./docs/architecture/ProcOS_Implementation_Guide_Part1.md)**: Technical deep dive

### **Key Concepts to Understand**
- **Process-First Thinking**: Everything is a BPMN workflow
- **External Tasks**: How workers connect to Camunda
- **Microkernel Philosophy**: Minimal bootstrap, maximum flexibility
- **API-First Design**: Backend independent of frontend

### **Development Environment**
- **Repository**: Clone from https://github.com/laserpointlabs/procos
- **Dependencies**: Docker, Python 3.8+, Node.js (for future frontend)
- **IDE**: VSCode recommended with BPMN and Python extensions

---

## 📞 **Context for AI Assistants**

### **Project Continuation Instructions**
When starting a new development session, an AI assistant should:

1. **Read this document completely** to understand project context
2. **Check current repository state** with `git status` and `git log --oneline -10`
3. **Verify system health** with `./scripts/health_check.py`
4. **Review recent changes** to understand latest development focus
5. **Ask clarifying questions** about specific goals for the session

### **Key Relationships**
- **ProcOS ↔ DADMS**: Backend-frontend separation strategy
- **Microkernel ↔ Workers**: Bootstrap system + external task handlers
- **BPMN ↔ Business Logic**: Visual workflows drive all operations
- **Documentation ↔ Implementation**: Specs guide all development

### **Development Priorities**
1. **Backend Stability**: Core microkernel and worker reliability
2. **Process Library**: Common BPMN workflow templates
3. **API Design**: Clear interfaces for frontend integration
4. **Testing**: Comprehensive quality assurance
5. **Documentation**: Keep specs current with implementation

---

**This document should be updated regularly as the project evolves. It serves as the complete context transfer for maintaining development continuity across sessions and team members.**

---

*Last Updated: January 2025 - After successful repository creation and initial implementation*
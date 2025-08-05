# 🚀 ProcOS Quick Start Guide

## 🎯 **You're Ready to Go!**

Your new **ProcOS** repository is fully set up and ready for rapid backend development. Here's everything you need to know to get started immediately.

## 📦 **What's Already Done**

✅ **Complete Project Structure**  
✅ **Docker Infrastructure** (Camunda + RabbitMQ + Redis)  
✅ **Python Microkernel** (6-phase bootstrap)  
✅ **Generic Worker** (HTTP, email, files)  
✅ **System Orchestrator BPMN**  
✅ **Automation Scripts** (start, stop, health check)  
✅ **Comprehensive Documentation**  
✅ **Git Repository Initialized**  

## ⚡ **Start ProcOS Right Now**

```bash
# Navigate to your new repository
cd /home/jdehart/procos

# One-command startup (handles everything!)
./scripts/start.sh

# Check if everything is working
./scripts/health_check.py
```

## 🌐 **Access Your Services**

After startup, these URLs will be available:

- **Camunda Engine**: http://localhost:8080
- **Camunda Cockpit**: http://localhost:8080/camunda  
- **RabbitMQ Admin**: http://localhost:15672 (procos/procos123)
- **Redis**: localhost:6379

## 🔧 **Test Your First Process**

```bash
# Deploy a simple test process
curl -X POST http://localhost:8080/engine-rest/process-definition/key/system_orchestrator/start \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "test_message": {"value": "Hello ProcOS!"}
    }
  }'
```

## 📋 **Immediate Development Tasks**

### **Today: Core Workers** ⭐
1. **Test Generic Worker**:
   ```bash
   # Test HTTP request capability
   curl -X POST http://localhost:8080/engine-rest/external-task/fetchAndLock \
     -H "Content-Type: application/json" \
     -d '{"workerId": "test", "maxTasks": 1, "topics": [{"topicName": "http_request", "lockDuration": 30000}]}'
   ```

2. **Create AI Worker**: Copy and adapt `src/workers/generic_worker.py` for AI tasks

3. **Add Sample Processes**: Create BPMN files in `src/processes/`

### **This Week: Feature Development** 🔥
- **Process Library**: Build common workflow templates
- **Custom Workers**: Domain-specific external task handlers  
- **API Integration**: Connect to external services
- **Error Handling**: Robust failure recovery patterns
- **Monitoring**: Enhanced health checks and metrics

### **Next Week: Frontend Integration** 🎨
- **Process-Driven UI**: React components that trigger BPMN processes
- **Real-time Updates**: WebSocket streams from Camunda
- **Process Monitoring**: Visual workflow status dashboards

## 🏗️ **Project Structure Overview**

```
procos/
├── 📄 README.md                    # Main project documentation
├── 🐳 docker-compose.yml           # Infrastructure setup
├── 📋 requirements.txt             # Python dependencies
├── ⚙️  env.example                 # Configuration template
│
├── 🧠 src/                         # Core implementation
│   ├── microkernel/               # Python microkernel (DONE ✅)
│   ├── workers/                   # External task workers (STARTED 🔨)
│   └── processes/                 # BPMN definitions (BASIC ✅)
│
├── 🧪 tests/                       # Testing framework (TODO 📋)
│   ├── unit/                      # Unit tests
│   └── integration/               # End-to-end tests
│
├── 🔧 scripts/                     # Automation (DONE ✅)
│   ├── start.sh                   # One-command startup
│   ├── stop.sh                    # Graceful shutdown
│   └── health_check.py            # System monitoring
│
└── 📚 docs/                        # Complete documentation (DONE ✅)
    ├── architecture/              # Design specifications
    ├── api/                       # API documentation (TODO 📋)
    └── deployment/                # Deployment guides (TODO 📋)
```

## 🎓 **Learning Path**

### **For Beginners**
1. 📚 **[ProcOS for Dummies](./docs/architecture/ProcOS_For_Dummies.md)** - Start here!
2. 🔧 **Experiment**: Try the basic scripts and see what happens
3. 📋 **Create Process**: Design your first BPMN workflow

### **For Developers**  
1. 🏗️ **[Implementation Guide Part 1](./docs/architecture/ProcOS_Implementation_Guide_Part1.md)** - Deep dive
2. 🔧 **Build Worker**: Create a custom external task worker
3. 📊 **Monitor**: Use Camunda Cockpit to watch processes execute

### **For Architects**
1. 🏛️ **[Architecture Specification](./docs/architecture/ProcOS_Architecture_Specification.md)** - Complete design
2. 📈 **Scale**: Design production deployment patterns
3. 🔗 **Integrate**: Connect to existing systems

## 🤝 **Team Workflow**

### **Daily Development**
```bash
# Start your development session
./scripts/start.sh

# Make changes to workers/processes
# ... code, code, code ...

# Test changes
./scripts/health_check.py

# Commit your work
git add .
git commit -m "Add feature X"
```

### **Branch Strategy**
```bash
# Create feature branch
git checkout -b feature/ai-worker-enhancement

# Work on feature...
# Commit changes...

# Merge back to main
git checkout main
git merge feature/ai-worker-enhancement
```

## 🎯 **Success Metrics**

### **Week 1 Goals**
- [ ] **5-second startup**: `./scripts/start.sh` gets everything running quickly
- [ ] **Basic AI query**: End-to-end process from API call to AI response
- [ ] **Error recovery**: Graceful handling of common failure scenarios
- [ ] **Documentation**: Clear API docs for frontend integration

### **MVP Definition**
- ✅ **Process execution**: BPMN workflows run reliably
- ✅ **Worker ecosystem**: HTTP, AI, email, file operations
- ✅ **Monitoring**: Health checks and system status
- ✅ **Integration ready**: APIs for frontend connection

## 🔄 **Moving from DADMS**

### **What Changed**
- 📁 **Location**: Separate repo for clean development
- 🏗️ **Architecture**: Microkernel + BPMN processes instead of microservices
- 🔧 **Development**: Backend-first without frontend complexity
- 📊 **Monitoring**: Process-driven system visibility

### **What Stayed**
- 🧠 **Intelligence**: AI/LLM integration patterns
- 📋 **Business Logic**: Decision-making workflows
- 🔗 **Integration**: External system connections
- 👥 **Team Knowledge**: Architecture understanding

### **Frontend Integration Plan**
- **Phase 1**: Backend stability (THIS WEEK)
- **Phase 2**: API completion (NEXT WEEK)  
- **Phase 3**: React integration (WEEK 3+)
- **Phase 4**: Full migration (MONTH 2)

---

## 🎉 **You're All Set!**

**Your ProcOS backend is ready for rapid development.** The hardest part (setup) is done. Now you can focus on building amazing process-driven features without any frontend complexity holding you back.

**Next step**: Run `./scripts/start.sh` and watch the magic happen! 🚀

---

**Questions?** Check the docs in `docs/architecture/` or create a simple test process to experiment with the system.
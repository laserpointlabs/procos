# ProcOS Infrastructure Architecture

## 🏗️ Infrastructure Overview

ProcOS follows a microkernel architecture with Camunda BPMN engine as the core orchestrator, supported by essential infrastructure services for data persistence, messaging, caching, and AI inference.

## 🐳 Container Architecture

```mermaid
graph TB
    subgraph "ProcOS Infrastructure Stack"
        subgraph "Core Orchestration"
            CAMUNDA[Camunda Platform :8080]
        end
        
        subgraph "Data Persistence"
            POSTGRES[(PostgreSQL :5432)]
        end
        
        subgraph "Worker Communication"
            RABBITMQ[RabbitMQ :5672/:15672]
        end
        
        subgraph "Caching Layer"
            REDIS[(Redis :6379)]
        end
        
        subgraph "AI Inference"
            OLLAMA[Ollama LLM :11434]
        end
        
        subgraph "Application Layer"
            KERNEL[ProcOS Kernel]
            AI_WORKER[AI Worker]
            GENERIC_WORKER[Generic Worker]
        end
    end
    
    subgraph "Data Flow"
        CAMUNDA --> POSTGRES
        CAMUNDA -.-> REDIS
        CAMUNDA -.-> RABBITMQ
        
        AI_WORKER --> CAMUNDA
        AI_WORKER --> OLLAMA
        GENERIC_WORKER --> CAMUNDA
        
        KERNEL --> CAMUNDA
    end
```

## 📊 Service Dependencies

```mermaid
graph LR
    subgraph "Startup Order"
        POSTGRES --> CAMUNDA
        REDIS --> CAMUNDA
        CAMUNDA --> KERNEL
        KERNEL --> AI_WORKER
        KERNEL --> GENERIC_WORKER
        OLLAMA --> AI_WORKER
    end
```

## 🔧 Service Specifications

### **PostgreSQL Database** ⚠️ **CRITICAL AI CONFIGURATION**
```yaml
Purpose: Primary data store for Camunda process engine + AI context
Container: postgres:15-alpine
Port: 5432
Database: procos
Credentials: procos/procos123
Volumes: postgres_data:/var/lib/postgresql/data
Init Script: ./scripts/init-db.sql

CRITICAL AI Requirements:
  - TEXT/JSONB columns for large AI context (prevents truncation)
  - Custom procos_ai_context table for guaranteed storage
  - Full-text search indexes for AI content
  - AI model management tables
  - Optimized indexes for AI query patterns

Data Stored:
  - Process instance state and history
  - Variable values (with AI-optimized storage)
  - AI context, prompts, and responses (BLOB/TEXT format)
  - Task execution records
  - User operation logs
  - Deployment artifacts (BPMN, DMN)
  - Authorization data
  - AI model configurations and performance stats

Health Check: pg_isready -U procos
```

### **Camunda Platform**
```yaml
Purpose: BPMN workflow engine and process orchestrator
Container: camunda/camunda-bpm-platform:latest
Port: 8080
Database: PostgreSQL (procos database)
Web Interface: http://localhost:8080/camunda/

Components:
  - Process Engine (REST API)
  - Cockpit (Process monitoring)
  - Tasklist (Human task management)
  - Admin (User/tenant management)

Health Check: curl -f http://localhost:8080/engine-rest/engine
```

### **RabbitMQ Message Broker**
```yaml
Purpose: Message queue for worker communication (future use)
Container: rabbitmq:3-management
Ports: 
  - 5672 (AMQP protocol)
  - 15672 (Management UI)
Credentials: procos/procos123
Management UI: http://localhost:15672

Use Cases:
  - Async notifications
  - Worker coordination
  - Event publishing
  - Dead letter queues

Health Check: rabbitmq-diagnostics -q ping
```

### **Redis Cache**
```yaml
Purpose: Session storage and caching layer
Container: redis:7-alpine
Port: 6379
Persistence: redis_data:/data

Use Cases:
  - Camunda session storage
  - Application caching
  - Temporary data storage
  - Rate limiting data

Health Check: redis-cli ping
```

### **Ollama AI Inference**
```yaml
Purpose: Local LLM inference for AI worker
Container: ollama/ollama:latest
Port: 11434
Model Storage: ollama_data:/root/.ollama
Configuration: CPU mode (no GPU requirements)

Models:
  - llama3.2:1b (lightweight for CPU)
  - Configurable for additional models

Health Check: curl -f http://localhost:11434/api/tags
```

## 🚀 Deployment Configurations

### **Development Profile (Default)**
```bash
# Starts core services with PostgreSQL
docker-compose up -d

Services Started:
✅ PostgreSQL (persistent storage)
✅ Camunda (connected to PostgreSQL)
✅ Redis (caching)
✅ RabbitMQ (messaging)
✅ Ollama (AI inference)
```

### **Production Profile**
```bash
# Production configuration with enhanced settings
docker-compose --profile production up -d

Additional Features:
✅ Enhanced health checks
✅ Resource limits
✅ Backup configurations
✅ Monitoring exports
✅ Security hardening
```

## 📈 Resource Requirements

### **Minimum Development**
```yaml
CPU: 4 cores
RAM: 8GB
Storage: 20GB
Network: Bridge networking

Service Allocation:
  - Camunda: 2GB RAM, 2 CPU
  - PostgreSQL: 1GB RAM, 1 CPU  
  - Ollama: 4GB RAM, 2 CPU
  - Redis: 512MB RAM
  - RabbitMQ: 512MB RAM
```

### **Production Recommendations**
```yaml
CPU: 8+ cores
RAM: 16GB+
Storage: 100GB+ (SSD recommended)
Network: Dedicated subnet

Service Allocation:
  - Camunda: 4GB RAM, 4 CPU
  - PostgreSQL: 4GB RAM, 2 CPU
  - Ollama: 8GB RAM, 4 CPU
  - Redis: 1GB RAM
  - RabbitMQ: 1GB RAM
```

## 🔒 Network Security

### **Internal Communication**
```yaml
Network: procos-network (bridge)
Isolation: Services communicate only within network
External Access: Only exposed ports (8080, 5432, etc.)

Inter-Service Communication:
  - Camunda ↔ PostgreSQL (5432)
  - AI Worker ↔ Camunda (8080)
  - AI Worker ↔ Ollama (11434)
  - Generic Worker ↔ Camunda (8080)
```

### **Port Allocation**
```yaml
External Ports:
  8080: Camunda Web Interface & REST API
  5432: PostgreSQL (for external tools)
  15672: RabbitMQ Management UI
  6379: Redis (for external tools)
  11434: Ollama API

Internal Only:
  All inter-service communication
  Health check endpoints
```

## 💾 Data Persistence Strategy

### **PostgreSQL Data Volumes**
```yaml
Volume: postgres_data
Mount: /var/lib/postgresql/data
Backup Strategy: Regular pg_dump exports
Retention: All process execution history

Critical Data:
  - Active process instances
  - Historical execution data
  - Variable values and changes
  - User operation audit logs
  - Deployed process definitions
```

## 🤖 AI Context Data Management

### **⚠️ CRITICAL: AI Context Truncation Prevention**

**Problem**: Standard Camunda variable storage can truncate large AI responses
**Solution**: Dual storage strategy with guaranteed TEXT/JSONB storage

### **AI Data Storage Architecture**
```yaml
Primary Storage (Camunda Variables):
  - Basic process orchestration data
  - Small variables and flags
  - Standard Camunda process state

AI-Optimized Storage (procos_ai_context table):
  - Large AI prompts and responses (TEXT columns)
  - Structured AI metadata (JSONB columns)
  - Token usage statistics
  - AI model information
  - Full conversation history

Backup Storage Pattern:
  1. Always store in custom procos_ai_context table (guaranteed)
  2. Also store in Camunda variables for process flow
  3. Use TEXT/JSONB types to prevent truncation
```

### **AI Context Table Schema**
```sql
CREATE TABLE procos_ai_context (
    id UUID PRIMARY KEY,
    process_instance_id VARCHAR(64) NOT NULL,
    task_id VARCHAR(64),
    activity_id VARCHAR(255),
    context_type VARCHAR(50) NOT NULL, -- 'input', 'output', 'system'
    content_data JSONB NOT NULL,      -- Structured data
    content_text TEXT,                -- Full text content
    ai_provider VARCHAR(50),
    model_used VARCHAR(100),
    token_usage JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### **Database Optimization for AI Workloads**
```yaml
Extensions Enabled:
  - uuid-ossp: UUID generation
  - pg_trgm: Full-text search optimization

Indexes Created:
  - GIN indexes on JSONB columns (content_data, token_usage)
  - Full-text search indexes on content_text
  - Process instance correlation indexes
  - AI provider and model indexes
  - Time-based indexes for analytics

Query Optimization:
  - Optimized for AI conversation retrieval
  - Fast process instance correlation
  - Efficient full-text search
  - Token usage analytics queries
```

### **AI Data Lifecycle Management**
```yaml
Storage Phases:
  1. Real-time: Active AI context in procos_ai_context
  2. Historical: Retained for analytics and improvement
  3. Archived: Long-term storage for compliance
  4. Purged: Configurable retention policies

Backup Strategy:
  - Daily backups of AI context tables
  - Separate backup schedule for large text content
  - Point-in-time recovery for critical AI data
  - Export capabilities for AI training data
```

### **Application Data Volumes**
```yaml
Redis: redis_data (cache persistence)
RabbitMQ: rabbitmq_data (queue persistence)
Ollama: ollama_data (model storage)

Backup Priority:
  1. PostgreSQL (critical - process data)
  2. Ollama (important - model cache)
  3. RabbitMQ (moderate - message queues)
  4. Redis (low - cache data)
```

## 🔄 Health Monitoring

### **Health Check Strategy**
```yaml
All Services: Configured with Docker health checks
Intervals: 30-second checks
Timeout: 10-second response limit
Retries: 3-5 attempts before marking unhealthy
Start Period: 60-90 seconds for complex services

Monitoring Endpoints:
  - Camunda: /engine-rest/engine
  - PostgreSQL: pg_isready command
  - Redis: redis-cli ping
  - RabbitMQ: rabbitmq-diagnostics
  - Ollama: /api/tags endpoint
```

### **Service Dependencies**
```yaml
Dependency Chain:
  PostgreSQL → Camunda → Workers

Failure Handling:
  - PostgreSQL down → Camunda cannot start
  - Camunda down → Workers wait and retry
  - Worker down → Tasks queue in Camunda
  - Ollama down → AI tasks fail gracefully
```

## 🔧 Configuration Management

### **Environment Variables**
```yaml
Database Configuration:
  DB_DRIVER: org.postgresql.Driver
  DB_URL: jdbc:postgresql://postgres:5432/procos
  DB_USERNAME: procos
  DB_PASSWORD: procos123

Service URLs:
  CAMUNDA_BASE_URL: http://camunda:8080/engine-rest
  OLLAMA_BASE_URL: http://ollama:11434
  REDIS_URL: redis://redis:6379
  RABBITMQ_URL: amqp://procos:procos123@rabbitmq:5672/
```

### **Volume Mounts**
```yaml
Configuration Files:
  - BPMN Processes: ./src/processes → /camunda/processes
  - Database Init: ./scripts/init-db.sql → /docker-entrypoint-initdb.d/

Data Persistence:
  - postgres_data: PostgreSQL database files
  - redis_data: Redis persistence files
  - rabbitmq_data: RabbitMQ data and configuration
  - ollama_data: Downloaded AI models
```

## 🚨 Critical Infrastructure Notes

### **⚠️ PostgreSQL is Required**
- **H2 in-memory database loses all data on container restart**
- **PostgreSQL provides persistent storage for process execution data**
- **All AI context, process history, and variable data stored in PostgreSQL**
- **Development and production should both use PostgreSQL for consistency**

### **🔄 Startup Sequence**
1. **PostgreSQL** must start first (data dependency)
2. **Camunda** connects to PostgreSQL (may retry on startup)
3. **Workers** connect to Camunda (external task polling)
4. **Support services** (Redis, RabbitMQ, Ollama) can start in parallel

### **💾 Data Recovery**
- **PostgreSQL backup strategy is critical**
- **Process instances in flight will be recovered on restart**
- **Variable history preserved across restarts**
- **AI context and responses maintained**

---

**This infrastructure provides a production-ready foundation for ProcOS development with persistent data storage, scalable worker patterns, and robust service orchestration.**
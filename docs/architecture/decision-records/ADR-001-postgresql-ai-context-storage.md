# ADR-001: PostgreSQL AI Context Storage Architecture

## Status
**Accepted** - January 18, 2025

## Context

ProcOS is a BPMN-driven microkernel architecture using Camunda as the process orchestration engine. During development, we encountered critical data truncation issues that compromised AI conversation continuity and data reliability.

### Problems Identified

1. **AI Context Truncation**: Camunda's standard variable storage truncated large AI responses, breaking conversation flow
2. **Data Loss**: H2 in-memory database lost all process data on container restarts
3. **Production Readiness**: In-memory storage unsuitable for production AI workloads
4. **Audit Requirements**: No persistent history for AI interactions and decisions

### Technical Constraints

- Must maintain compatibility with Camunda BPMN engine
- External task pattern requires reliable variable storage
- AI responses can exceed 8KB (standard database field limits)
- Process instance data needs persistence across deployments
- Performance requirements for real-time AI interactions

## Decision

**Implement PostgreSQL as primary database with dual AI context storage strategy**

### Core Architecture Changes

1. **Replace H2 with PostgreSQL**
   - PostgreSQL 15 as primary database for Camunda
   - Persistent storage across container restarts
   - Production-grade reliability and performance

2. **Dual Storage Strategy for AI Context**
   - **Camunda Variables**: Small orchestration data, flags, status
   - **Custom AI Tables**: Large AI content using TEXT/JSONB columns
   - Guaranteed no truncation for AI responses

3. **AI-Optimized Database Schema**
   ```sql
   CREATE TABLE procos_ai_context (
       id UUID PRIMARY KEY,
       process_instance_id VARCHAR(64) NOT NULL,
       content_data JSONB NOT NULL,      -- Unlimited structured data
       content_text TEXT,                -- Unlimited text content
       ai_provider VARCHAR(50),
       token_usage JSONB,
       created_at TIMESTAMP WITH TIME ZONE
   );
   ```

4. **Performance Optimizations**
   - GIN indexes on JSONB columns for fast queries
   - Full-text search indexes using pg_trgm extension
   - Process correlation indexes for conversation tracking
   - Automatic timestamp management via triggers

## Implementation Details

### Database Configuration
```yaml
PostgreSQL Setup:
  - Container: postgres:15-alpine
  - Database: procos
  - Credentials: procos/procos123
  - Port: 5432
  - Persistence: postgres_data volume
  - Init Script: scripts/init-db.sql
```

### Camunda Integration
```yaml
Environment Variables:
  DB_DRIVER: org.postgresql.Driver
  DB_URL: jdbc:postgresql://postgres:5432/procos
  DB_USERNAME: procos
  DB_PASSWORD: procos123
  WAIT_FOR_DB: postgres:5432
```

### AI Context Storage Strategy
```yaml
Primary Storage (procos_ai_context):
  - content_data: JSONB for structured queries
  - content_text: TEXT for unlimited content
  - token_usage: JSONB for analytics
  - Full audit trail with timestamps

Secondary Storage (Camunda Variables):
  - Process flow control
  - Status flags and metadata
  - Small reference data
```

## Consequences

### Positive Consequences

1. **Data Reliability**
   - ✅ Zero AI context truncation
   - ✅ Complete persistence across restarts
   - ✅ Full conversation history preservation
   - ✅ Production-ready data storage

2. **Performance Benefits**
   - ✅ Optimized indexes for AI workload queries
   - ✅ JSONB compression for structured data
   - ✅ Full-text search capabilities
   - ✅ Efficient process correlation

3. **Development Experience**
   - ✅ Automated schema initialization
   - ✅ Clean deployment process
   - ✅ Comprehensive documentation
   - ✅ Memory system integration

4. **Operational Benefits**
   - ✅ Standard PostgreSQL backup/recovery
   - ✅ Monitoring and alerting capabilities
   - ✅ Scalability for production workloads
   - ✅ Security and compliance features

### Negative Consequences

1. **Infrastructure Complexity**
   - ❌ Additional PostgreSQL container required
   - ❌ Increased memory usage (+200MB)
   - ❌ Longer startup time (+30 seconds)
   - ❌ More complex backup requirements

2. **Migration Challenges**
   - ❌ H2 to PostgreSQL migration required
   - ❌ Breaking change for existing deployments
   - ❌ Data loss from previous H2 instances
   - ❌ Configuration updates needed

3. **Development Overhead**
   - ❌ Database maintenance workflow required
   - ❌ Schema migration management
   - ❌ Additional monitoring complexity
   - ❌ PostgreSQL expertise needed

## Alternatives Considered

### Alternative 1: Enhanced Camunda Variable Storage
**Rejected** - Would require modifying Camunda internals, losing upgrade compatibility and support.

### Alternative 2: External File Storage
**Rejected** - Would complicate backup/recovery, create consistency issues, and reduce query performance.

### Alternative 3: NoSQL Database (MongoDB/Redis)
**Rejected** - Would add another data store, increase complexity, and lose ACID transaction guarantees.

### Alternative 4: Hybrid H2/PostgreSQL
**Rejected** - Would create data consistency issues and complicate deployment/backup procedures.

## Implementation Plan

### Phase 1: Database Infrastructure (Completed)
- [x] PostgreSQL container configuration
- [x] Camunda connection setup
- [x] Basic schema initialization
- [x] Service dependency management

### Phase 2: AI Context Storage (Completed)
- [x] Custom AI context tables
- [x] Optimized indexes and extensions
- [x] AI model management tables
- [x] Query performance optimization

### Phase 3: Documentation and Processes (Completed)
- [x] Database management guide
- [x] Architecture documentation updates
- [x] Init script maintenance workflow
- [x] MCP memory system integration

### Phase 4: Validation and Release (Current)
- [x] Infrastructure testing
- [x] AI context storage validation
- [x] Performance benchmarking
- [x] Release documentation

## Monitoring and Success Metrics

### Technical Metrics
```yaml
AI Context Storage:
  - Zero truncation incidents
  - Sub-second query response times
  - 100% data persistence across restarts
  - Successful conversation correlation

Database Performance:
  - Index utilization > 90%
  - Query performance < 100ms
  - Connection pool efficiency
  - Storage growth tracking
```

### Operational Metrics
```yaml
Deployment Success:
  - Clean initialization on fresh deployments
  - Successful schema migrations
  - Health check pass rates
  - Service startup sequence reliability
```

## Review and Evolution

### Quarterly Review Schedule
- **Q2 2025**: Performance optimization review
- **Q3 2025**: Scaling requirements assessment
- **Q4 2025**: Security and compliance audit
- **Q1 2026**: Architecture evolution planning

### Potential Future Enhancements
- Connection pooling optimization
- Read replica configuration for analytics
- Advanced backup automation
- Performance monitoring integration
- Multi-tenant database strategies

## References

- [Camunda Platform 7 Database Configuration](https://docs.camunda.org/manual/latest/installation/database/)
- [PostgreSQL Performance Tuning Guide](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [JSONB Indexing Best Practices](https://www.postgresql.org/docs/current/datatype-json.html)
- `docs/architecture/database-management.md` - ProcOS Database Management Guide
- `docs/architecture/infrastructure.md` - Infrastructure Architecture
- `scripts/init-db.sql` - Database Initialization Script

---

**Decision Made By**: ProcOS Architecture Team  
**Implementation Lead**: Infrastructure Team  
**Review Date**: January 18, 2025  
**Next Review**: April 18, 2025
# ProcOS Database Management Guide

## 🎯 Overview

This guide covers critical database management requirements for ProcOS, with special focus on AI context storage, truncation prevention, and the mandatory `init-db.sql` maintenance workflow.

## 🚨 Critical Issue: AI Context Truncation

### **The Problem**
- **Camunda standard variables** can truncate large AI responses
- **VARCHAR columns** have size limits that cut off AI content
- **Lost AI context** breaks conversation continuity
- **Production failures** from incomplete data storage

### **The Solution: Dual Storage Strategy**
```yaml
Strategy: Use both Camunda variables AND custom AI tables

Camunda Variables (Standard):
  - Process orchestration flags
  - Small metadata (provider, model name)
  - Status indicators
  - Process flow control

Custom AI Tables (Guaranteed Storage):
  - Large AI prompts and responses (TEXT columns)
  - Full conversation context (JSONB columns)
  - Token usage statistics
  - Complete metadata with no truncation risk
```

## 📊 Database Schema Architecture

### **Core Tables Created by init-db.sql**

#### **1. procos_ai_context**
```sql
-- PRIMARY AI STORAGE - Guaranteed no truncation
CREATE TABLE procos_ai_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_instance_id VARCHAR(64) NOT NULL,
    task_id VARCHAR(64),
    activity_id VARCHAR(255),
    context_type VARCHAR(50) NOT NULL, -- 'input', 'output', 'system'
    content_data JSONB NOT NULL,      -- Structured data, unlimited size
    content_text TEXT,                -- Full text content, unlimited size
    ai_provider VARCHAR(50),
    model_used VARCHAR(100),
    token_usage JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Purpose**: Store complete AI interactions without size limits
**Benefits**: 
- TEXT columns prevent truncation
- JSONB allows structured queries
- Indexed for fast retrieval
- Complete audit trail

#### **2. procos_ai_models**
```sql
-- AI MODEL MANAGEMENT AND VERSIONING
CREATE TABLE procos_ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    version VARCHAR(100),
    config_data JSONB,
    performance_stats JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(model_name, provider, version)
);
```

**Purpose**: Track AI model configurations and performance
**Benefits**:
- Version control for AI models
- Performance tracking
- Configuration management
- Provider comparison data

### **3. procos_ai_conversations VIEW**
```sql
-- EASY QUERY INTERFACE FOR AI CONVERSATIONS
CREATE VIEW procos_ai_conversations AS
SELECT 
    process_instance_id,
    task_id,
    activity_id,
    ai_provider,
    model_used,
    created_at,
    CASE WHEN context_type = 'input' THEN content_data->>'query' END AS query_text,
    CASE WHEN context_type = 'input' THEN content_data->>'context' END AS input_context,
    CASE WHEN context_type = 'output' THEN content_data->>'content' END AS ai_response,
    CASE WHEN context_type = 'output' THEN token_usage END AS usage_stats
FROM procos_ai_context
ORDER BY process_instance_id, created_at;
```

## 🔧 Database Optimization Features

### **PostgreSQL Extensions**
```sql
-- Required extensions for AI workloads
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- Full-text search optimization
```

### **AI-Optimized Indexes**
```sql
-- Camunda table optimizations
CREATE INDEX idx_act_ru_variable_name_text 
ON act_ru_variable USING gin(name_ gin_trgm_ops) 
WHERE text_ IS NOT NULL;

CREATE INDEX idx_act_hi_varinst_proc_inst_ai 
ON act_hi_varinst (proc_inst_id_, name_) 
WHERE name_ IN ('query', 'context', 'content', 'ai_provider', 'usage');

-- AI context table indexes
CREATE INDEX idx_procos_ai_context_proc_inst ON procos_ai_context (process_instance_id);
CREATE INDEX idx_procos_ai_context_content_search ON procos_ai_context USING gin(content_text gin_trgm_ops);
CREATE INDEX idx_procos_ai_context_content_jsonb ON procos_ai_context USING gin(content_data);
CREATE INDEX idx_procos_ai_context_usage_jsonb ON procos_ai_context USING gin(token_usage);
```

### **Automatic Maintenance**
```sql
-- Auto-update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
CREATE TRIGGER trigger_procos_ai_context_updated_at
    BEFORE UPDATE ON procos_ai_context
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## 📋 Mandatory init-db.sql Maintenance Workflow

### **⚠️ CRITICAL RULE: Always Update init-db.sql**

**When to Update init-db.sql**:
- Adding new tables or columns
- Changing data types (especially for AI context)
- Adding new indexes for performance
- Modifying permissions or functions
- Adding new extensions or features
- Updating AI model configurations

### **Update Process**
```bash
# 1. Make schema changes in init-db.sql first
vim scripts/init-db.sql

# 2. Test with clean database
docker-compose down -v  # Remove all data
docker-compose up -d postgres  # Start fresh

# 3. Verify schema creation
docker-compose logs postgres | grep "ProcOS PostgreSQL"

# 4. Test with Camunda startup
docker-compose up -d camunda

# 5. Verify AI tables and indexes exist
docker-compose exec postgres psql -U procos -d procos \
  -c "\dt" -c "\di" -c "SELECT * FROM procos_ai_models;"

# 6. Test AI worker integration
# Run AI worker and verify data storage
```

### **Schema Change Checklist**
- [ ] **init-db.sql updated** with all schema changes
- [ ] **Indexes added** for new query patterns  
- [ ] **Permissions granted** for procos user
- [ ] **Functions/triggers** created for automation
- [ ] **Default data** inserted for AI models
- [ ] **Documentation updated** with schema changes
- [ ] **Clean deployment tested** from scratch
- [ ] **AI context storage verified** (no truncation)

## 🔍 Monitoring and Troubleshooting

### **AI Context Storage Validation**
```sql
-- Check for truncated AI content (content suspiciously short)
SELECT 
    process_instance_id,
    ai_provider,
    LENGTH(content_text) as content_length,
    content_text
FROM procos_ai_context 
WHERE context_type = 'output' 
  AND LENGTH(content_text) < 50
ORDER BY created_at DESC;

-- Check Camunda variable storage sizes
SELECT 
    name_,
    LENGTH(text_) as text_length,
    LENGTH(long_) as long_length,
    proc_inst_id_
FROM act_ru_variable 
WHERE name_ IN ('content', 'query', 'context')
  AND (LENGTH(text_) > 8000 OR LENGTH(long_) > 8000)
ORDER BY text_length DESC;
```

### **Performance Monitoring**
```sql
-- Monitor AI context table growth
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT process_instance_id) as unique_conversations,
    AVG(LENGTH(content_text)) as avg_content_length,
    MAX(LENGTH(content_text)) as max_content_length,
    ai_provider
FROM procos_ai_context 
GROUP BY ai_provider;

-- Check index usage
SELECT 
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE relname = 'procos_ai_context'
ORDER BY idx_scan DESC;
```

### **Backup Verification**
```bash
# Verify AI context data in backups
docker-compose exec postgres pg_dump -U procos procos \
  --table=procos_ai_context \
  --table=procos_ai_models \
  -f /tmp/ai_context_backup.sql

# Check backup contains AI data
docker-compose exec postgres grep -c "INSERT INTO procos_ai_context" /tmp/ai_context_backup.sql
```

## 🚀 Best Practices

### **Development Workflow**
1. **Always start with clean database** when testing schema changes
2. **Update init-db.sql before any schema modifications**
3. **Test AI worker storage** after database changes
4. **Verify no truncation** occurs with large AI responses
5. **Document schema changes** in architecture documentation

### **Production Considerations**
```yaml
Backup Strategy:
  - Daily full backups including AI context tables
  - Point-in-time recovery capability
  - Separate backup validation for AI data

Monitoring:
  - Track AI context table sizes
  - Monitor for truncation warnings
  - Alert on index performance degradation
  - Watch for storage space consumption

Performance Tuning:
  - Regular VACUUM and ANALYZE on AI tables
  - Monitor and tune checkpoint settings
  - Optimize work_mem for JSONB operations
  - Consider partitioning for very large datasets
```

### **Troubleshooting Common Issues**

#### **Problem: AI responses getting truncated**
```sql
-- Solution: Verify storage in custom table
SELECT content_text FROM procos_ai_context 
WHERE process_instance_id = 'your_process_id' 
  AND context_type = 'output';
```

#### **Problem: Poor query performance on AI data**
```sql
-- Solution: Check if indexes are being used
EXPLAIN ANALYZE 
SELECT * FROM procos_ai_context 
WHERE process_instance_id = 'your_process_id';
```

#### **Problem: Database schema outdated after deployment**
```bash
# Solution: Run post-deployment optimization
docker-compose exec postgres psql -U procos -d procos \
  -c "SELECT optimize_camunda_for_ai();"
```

---

## 🎯 Summary

The database management strategy for ProcOS is built around preventing AI context truncation while maintaining compatibility with Camunda's standard workflow patterns. The dual storage approach ensures that:

1. **Process orchestration continues** using standard Camunda variables
2. **AI context is preserved** using custom TEXT/JSONB tables  
3. **Performance is optimized** with AI-specific indexes
4. **Schema maintenance is automated** through init-db.sql updates

**Remember**: Always update `init-db.sql` first, then test with clean deployments to ensure reliable database configuration across all environments.

---

*This database management approach ensures ProcOS can reliably handle large AI workloads without data loss or truncation issues.*
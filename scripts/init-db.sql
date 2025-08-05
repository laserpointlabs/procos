-- ProcOS PostgreSQL Database Initialization Script
-- This script is automatically executed when PostgreSQL container starts
-- 
-- CRITICAL: This script must be updated whenever database schema changes
-- to ensure clean deployments and proper AI context storage

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search optimization

-- Camunda will create its own schema, but we need to ensure proper data types
-- for AI context storage to prevent truncation issues

-- Post-Camunda schema modifications for AI workloads
-- This function will be called after Camunda creates its schema
CREATE OR REPLACE FUNCTION optimize_camunda_for_ai() RETURNS void AS $$
BEGIN
    -- Ensure ACT_RU_VARIABLE uses TEXT instead of VARCHAR for large AI content
    -- Note: This may need to be run after Camunda startup if schema already exists
    
    -- Check if Camunda tables exist (they may not on first run)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'act_ru_variable') THEN
        -- Modify variable value columns to handle large AI context
        -- Camunda uses LONG_ columns for large data, ensure they're properly typed
        RAISE NOTICE 'Camunda tables detected - checking for AI optimization needs';
        
        -- Add indexes for AI workload queries
        CREATE INDEX IF NOT EXISTS idx_act_ru_variable_name_text 
        ON act_ru_variable USING gin(name_ gin_trgm_ops) 
        WHERE text_ IS NOT NULL;
        
        CREATE INDEX IF NOT EXISTS idx_act_hi_varinst_name_value 
        ON act_hi_varinst (name_, create_time_) 
        WHERE var_type_ = 'string';
        
        CREATE INDEX IF NOT EXISTS idx_act_hi_varinst_proc_inst_ai 
        ON act_hi_varinst (proc_inst_id_, name_) 
        WHERE name_ IN ('query', 'context', 'content', 'ai_provider', 'usage');
        
    ELSE
        RAISE NOTICE 'Camunda tables not yet created - will need manual optimization after startup';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create custom tables for AI-specific data that needs guaranteed proper storage
CREATE TABLE IF NOT EXISTS procos_ai_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_instance_id VARCHAR(64) NOT NULL,
    task_id VARCHAR(64),
    activity_id VARCHAR(255),
    context_type VARCHAR(50) NOT NULL, -- 'input', 'output', 'system'
    content_data JSONB NOT NULL,      -- Store as JSONB for queryability
    content_text TEXT,                -- Full text for search
    ai_provider VARCHAR(50),
    model_used VARCHAR(100),
    token_usage JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for AI context table
CREATE INDEX IF NOT EXISTS idx_procos_ai_context_proc_inst 
ON procos_ai_context (process_instance_id);

CREATE INDEX IF NOT EXISTS idx_procos_ai_context_task 
ON procos_ai_context (task_id) WHERE task_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_procos_ai_context_activity 
ON procos_ai_context (activity_id) WHERE activity_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_procos_ai_context_type 
ON procos_ai_context (context_type);

CREATE INDEX IF NOT EXISTS idx_procos_ai_context_provider 
ON procos_ai_context (ai_provider) WHERE ai_provider IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_procos_ai_context_created 
ON procos_ai_context (created_at);

-- Full text search index for AI content
CREATE INDEX IF NOT EXISTS idx_procos_ai_context_content_search 
ON procos_ai_context USING gin(content_text gin_trgm_ops);

-- JSONB indexes for structured queries
CREATE INDEX IF NOT EXISTS idx_procos_ai_context_content_jsonb 
ON procos_ai_context USING gin(content_data);

CREATE INDEX IF NOT EXISTS idx_procos_ai_context_usage_jsonb 
ON procos_ai_context USING gin(token_usage);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto-updating updated_at
CREATE TRIGGER trigger_procos_ai_context_updated_at
    BEFORE UPDATE ON procos_ai_context
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create table for AI model management and versioning
CREATE TABLE IF NOT EXISTS procos_ai_models (
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

-- Indexes for AI models table
CREATE INDEX IF NOT EXISTS idx_procos_ai_models_name_provider 
ON procos_ai_models (model_name, provider);

CREATE INDEX IF NOT EXISTS idx_procos_ai_models_active 
ON procos_ai_models (is_active) WHERE is_active = true;

-- Trigger for AI models updated_at
CREATE TRIGGER trigger_procos_ai_models_updated_at
    BEFORE UPDATE ON procos_ai_models
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for easy AI context querying
CREATE OR REPLACE VIEW procos_ai_conversations AS
SELECT 
    process_instance_id,
    task_id,
    activity_id,
    ai_provider,
    model_used,
    created_at,
    CASE 
        WHEN context_type = 'input' THEN content_data->>'query'
        ELSE NULL 
    END AS query_text,
    CASE 
        WHEN context_type = 'input' THEN content_data->>'context'
        ELSE NULL 
    END AS input_context,
    CASE 
        WHEN context_type = 'output' THEN content_data->>'content'
        ELSE NULL 
    END AS ai_response,
    CASE 
        WHEN context_type = 'output' THEN token_usage
        ELSE NULL 
    END AS usage_stats
FROM procos_ai_context
ORDER BY process_instance_id, created_at;

-- Grant permissions for procos user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO procos;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO procos;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO procos;

-- Insert default AI model configurations
INSERT INTO procos_ai_models (model_name, provider, version, config_data, is_active) VALUES
('llama3.2:1b', 'ollama', '1.0', '{"temperature": 0.7, "max_tokens": 2048}', true),
('gpt-4o-mini', 'openai', 'latest', '{"temperature": 0.7, "max_tokens": 4096}', true)
ON CONFLICT (model_name, provider, version) DO NOTHING;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE '=== ProcOS PostgreSQL Database Initialized Successfully ===';
    RAISE NOTICE 'Database: procos';
    RAISE NOTICE 'User: procos';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pg_trgm';
    RAISE NOTICE 'AI context tables created with proper BLOB/TEXT storage';
    RAISE NOTICE 'Indexes optimized for AI workloads';
    RAISE NOTICE 'Custom AI context storage: procos_ai_context table';
    RAISE NOTICE 'AI model management: procos_ai_models table';
    RAISE NOTICE 'AI conversation view: procos_ai_conversations';
    RAISE NOTICE 'Camunda tables will be created automatically on engine startup';
    RAISE NOTICE 'Run optimize_camunda_for_ai() function after Camunda startup if needed';
    RAISE NOTICE '============================================================';
END $$;
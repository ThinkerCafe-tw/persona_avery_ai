-- 🌌 五行團隊共享記憶宇宙 - pgvector 架構設計
-- Cruz 的 PostgreSQL + pgvector 共享資料庫

-- 啟用 pgvector 擴展
CREATE EXTENSION IF NOT EXISTS vector;

-- 🏛️ 命名空間表 (區分不同 AI 人格)
CREATE TABLE IF NOT EXISTS ai_personas (
    id SERIAL PRIMARY KEY,
    namespace VARCHAR(50) UNIQUE NOT NULL, -- 'avery', 'cruz', 'serena', 'wuji'
    persona_name VARCHAR(100) NOT NULL,
    element VARCHAR(20), -- '木', '火', '土', '金', '水', '無極'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🧠 用戶記憶表 (每個人格的用戶記憶)
CREATE TABLE IF NOT EXISTS user_memories (
    id SERIAL PRIMARY KEY,
    namespace VARCHAR(50) NOT NULL, -- 關聯到 ai_personas.namespace
    user_id VARCHAR(255) NOT NULL, -- LINE User ID
    memory_type VARCHAR(50) NOT NULL, -- 'profile', 'conversation', 'preference'
    content TEXT NOT NULL,
    metadata JSONB, -- 額外資訊 (情緒、標籤等)
    embedding vector(1536), -- OpenAI text-embedding-ada-002 向量
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (namespace) REFERENCES ai_personas(namespace)
);

-- 🗣️ 對話記錄表 (完整對話歷史)
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    namespace VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(100), -- 對話會話ID
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    emotion_tag VARCHAR(50), -- 情緒標籤
    metadata JSONB,
    message_embedding vector(1536), -- 用戶訊息向量
    response_embedding vector(1536), -- AI 回應向量
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (namespace) REFERENCES ai_personas(namespace)
);

-- 🌟 跨人格共享記憶表 (團隊協作記憶)
CREATE TABLE IF NOT EXISTS shared_insights (
    id SERIAL PRIMARY KEY,
    source_namespace VARCHAR(50) NOT NULL, -- 記憶來源人格
    insight_type VARCHAR(50) NOT NULL, -- 'lesson_learned', 'user_pattern', 'system_insight'
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    relevance_score FLOAT DEFAULT 1.0,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_namespace) REFERENCES ai_personas(namespace)
);

-- 📊 索引優化 (向量相似度搜尋)
CREATE INDEX IF NOT EXISTS idx_user_memories_embedding ON user_memories USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_conversations_message_embedding ON conversations USING ivfflat (message_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_conversations_response_embedding ON conversations USING ivfflat (response_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_shared_insights_embedding ON shared_insights USING ivfflat (embedding vector_cosine_ops);

-- 🔍 查詢優化索引
CREATE INDEX IF NOT EXISTS idx_user_memories_namespace_user ON user_memories(namespace, user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_namespace_user ON conversations(namespace, user_id);
CREATE INDEX IF NOT EXISTS idx_user_memories_type ON user_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);

-- 🌌 初始化五行人格
INSERT INTO ai_personas (namespace, persona_name, element, description) VALUES
('wuji', '無極', '無極', '系統哲學觀察者，總結反思，平衡調節'),
('cruz', 'Cruz', '金', '決斷推進，直接果斷，精煉守護'),
('avery', 'Avery', '木', '創新成長，外聯拓展，產品管理'),
('serena', 'Serena', '陰', '溫和支援，情緒協調，平衡調節')
ON CONFLICT (namespace) DO NOTHING;

-- 🔧 實用查詢函數

-- 獲取用戶最近記憶 (相似度搜尋)
CREATE OR REPLACE FUNCTION get_similar_memories(
    p_namespace VARCHAR(50),
    p_user_id VARCHAR(255),
    p_query_embedding vector(1536),
    p_limit INTEGER DEFAULT 5
) RETURNS TABLE (
    memory_id INTEGER,
    content TEXT,
    similarity FLOAT,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        um.id,
        um.content,
        (um.embedding <=> p_query_embedding) AS similarity,
        um.created_at
    FROM user_memories um
    WHERE um.namespace = p_namespace 
    AND um.user_id = p_user_id
    ORDER BY um.embedding <=> p_query_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 跨人格洞察搜尋
CREATE OR REPLACE FUNCTION get_cross_persona_insights(
    p_query_embedding vector(1536),
    p_limit INTEGER DEFAULT 3
) RETURNS TABLE (
    insight_id INTEGER,
    source_persona VARCHAR(50),
    title VARCHAR(200),
    content TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        si.id,
        si.source_namespace,
        si.title,
        si.content,
        (si.embedding <=> p_query_embedding) AS similarity
    FROM shared_insights si
    ORDER BY si.embedding <=> p_query_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
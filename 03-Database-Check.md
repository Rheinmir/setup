# CONTEXT
Before writing the core application, we need to ensure the **Cognee Knowledge Graph** (Neo4j, Supabase, Azure LLM) database connection infrastructure is ready.

# INSTRUCTIONS
1. Read the contents of the `.env.cognee` file in the root directory.
2. CHECK CONDITION:
   - IF `LLM_API_KEY`, `GRAPH_DATABASE_PASSWORD`, or `VECTOR_DB_PASSWORD` are empty, missing or blank: 
     STOP. Tell the user: "⚠️ Vui lòng mở file `.env.cognee` và điền thông tin kết nối Cognee (Azure LLM, Neo4j, Supabase). Nếu bạn chưa có, tôi có thể hướng dẫn. Sau khi điền xong, hãy gõ 'tiếp tục'."
     Do not proceed further until the user says "tiếp tục".
   - IF the variables have valid values:
     BYPASS the warning. Tell the user: "✅ Đã tìm thấy cấu hình kết nối Cognee."
3. If bypassed (or after user says "tiếp tục" and provides info), set up the initial backend configurations to load these credentials so the Cognee MCP / integration can connect successfully.

# ACTION
Execute the logic above now. Check the configuration state and act accordingly.

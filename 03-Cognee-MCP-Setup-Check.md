# CONTEXT
Before writing the core application, we need to ensure the **Cognee Memory MCP** is installed and configured on this machine.

# INSTRUCTIONS
1. CHECK if Cognee is installed by running: `pip show cognee` or `python -c "import cognee"`.
   - IF the command itself fails (pip/python not found): STOP. Tell the user the exact error and ask them to check their Python environment. Do not proceed until user says "tiếp tục", then RE-RUN this check — do not skip it.
   - IF Cognee is NOT installed: STOP. Tell the user: "⚠️ Cognee chưa được cài. Chạy `pip install cognee` rồi gõ 'tiếp tục'." Do not proceed until user says "tiếp tục", then RE-RUN this check — do not skip it.
   - IF Cognee IS installed: continue to step 2.

2. Attempt a connection test immediately — initialize the Cognee client and call a basic ping/health method to verify Neo4j and Supabase are reachable. Cognee may have credentials persisted internally even if env vars appear empty.
   - If the test passes: tell the user "✅ Cognee MCP kết nối thành công." and proceed to step 04. Do not block on missing env vars.
   - If the test fails: continue to step 3.

3. Connection failed — now check why. For each of `LLM_API_KEY`, `GRAPH_DATABASE_PASSWORD`, `VECTOR_DB_PASSWORD`:
   - Check system/shell environment variables first.
   - If not found, check `.env.cognee` file (if file does not exist, treat as missing).
   - Report exactly which variables are missing and which service each maps to (LLM / Neo4j / Supabase).
   - Show the original connection error alongside the missing variables.
   - STOP. Do not proceed until user says "tiếp tục", then RE-RUN from step 2 — do not skip straight to success.

# ACTION
Execute the logic above now. Check the configuration state and act accordingly.

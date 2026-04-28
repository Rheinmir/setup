# CONTEXT
Before writing the core application, we need to ensure the **Cognee Memory MCP** is installed and configured on this machine.

# INSTRUCTIONS
1. CHECK if Cognee is installed by running: `pip show cognee` or `python -c "import cognee"`.
   - IF the command itself fails (pip/python not found): STOP. Tell the user the exact error and ask them to check their Python environment. Do not proceed until user says "tiếp tục", then RE-RUN this check — do not skip it.
   - IF Cognee is NOT installed: STOP. Tell the user: "⚠️ Cognee chưa được cài. Chạy `pip install cognee` rồi gõ 'tiếp tục'." Do not proceed until user says "tiếp tục", then RE-RUN this check — do not skip it.
   - IF Cognee IS installed: continue to step 2.

2. CHECK each of `LLM_API_KEY`, `GRAPH_DATABASE_PASSWORD`, `VECTOR_DB_PASSWORD`:
   - Check system/shell environment variables first.
   - If not found in environment, check `.env.cognee` file (if the file does not exist, treat all file-sourced values as missing).
   - IF all three are resolved: tell the user "✅ Cognee Memory MCP đã cài và cấu hình đầy đủ." and note which source each came from (env or file). Continue to step 3.
   - IF any are missing: STOP. Tell the user exactly which variables are missing. Do not proceed until user says "tiếp tục", then RE-CHECK the variables — do not skip straight to step 3.

3. Load the resolved credentials into the runtime environment (via `python-dotenv` or equivalent). Then run a minimal connection test — initialize the Cognee client and call a basic ping/health method to verify Neo4j and Supabase are reachable.
   - If the test passes: tell the user "✅ Cognee MCP kết nối thành công." and proceed.
   - If the test fails: show the exact error, identify which service failed (Neo4j / Supabase / LLM), and STOP. Do not proceed to step 04 until the issue is resolved.

# ACTION
Execute the logic above now. Check the configuration state and act accordingly.

/** Entry stdio cho client trên cùng máy (Claude Code `claude mcp add`, dsh `transport: stdio`). Không cần token. */
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { buildServer } from "./server.ts";

const server = buildServer();
await server.connect(new StdioServerTransport());

/** Entry HTTP: PORT (8791), BIND (0.0.0.0 trong container; compose map ra 127.0.0.1). Token: env → file trong volume → sinh mới. */
import { serve } from "@hono/node-server";
import { createApp } from "./http.ts";
import { loadCatalog, OVERSTACK_ROOT } from "./catalog.ts";
import { buildServer, toolModeFromEnv } from "./server.ts";
import { NodeSource } from "./source-node.ts";
import { resolveToken } from "./token.ts";
import { workspacesDir } from "./workspace.ts";

const PORT = Number(process.env.PORT ?? 8791);
const BIND = process.env.BIND ?? "0.0.0.0";
const catalog = loadCatalog();
const source = new NodeSource(OVERSTACK_ROOT, catalog);
const auth = resolveToken(workspacesDir());
const app = createApp({ token: auth.token, tokenSource: auth.source, catalog, source, harness: await source.harnessVersion(), workspacesDir: workspacesDir(),
  build: (o) => buildServer({ catalog: o.catalog, mode: o.mode, source: o.source }) });
serve({ fetch: app.fetch, port: PORT, hostname: BIND }, (info) => {
  console.log(`overstack-mcp ${toolModeFromEnv()} on http://${info.address}:${info.port}/mcp  root=${OVERSTACK_ROOT}  workspaces=${workspacesDir()}  skills=${catalog.skills.length} rules=${catalog.rules.length} tools=${catalog.tools.length}`);
  if (auth.source !== "env") console.log(`bearer token ${auth.source === "generated" ? "GENERATED" : "read"} from ${auth.path} — operator: docker exec overstack-mcp cat ${auth.path}`);
});

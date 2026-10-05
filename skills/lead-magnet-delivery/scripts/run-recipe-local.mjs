#!/usr/bin/env node
// Run a hosted OXYGEN durable recipe locally, routing every ctx.tools.run call
// through the `oxygen` CLI so LinkedIn calls still pass the API's per-account
// quota enforcer. A fallback for when hosted runs fail with
// linkedin_quota_enforcement_unavailable. Same recipe code, same ledger table, same pacing.
//
//   node run.mjs recipes/<post-slug>-delivery.mjs [--input '{"audit":true}'] [--workflow <slug>]
//
// --workflow: if that hosted workflow's latest scheduled run completed, the
// hosted runtime works again and this local run exits without acting.

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFileSync, writeFileSync, openSync, closeSync, unlinkSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const run = promisify(execFile);
const PROFILE = process.env.OXYGEN_PROFILE ?? "default";
const OXYGEN = process.env.OXYGEN_BIN ?? "oxygen";
const arg = (name) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : undefined;
};
const recipePath = resolve(process.argv[2] ?? "");
const input = JSON.parse(arg("input") ?? "{}");
const hostedSlug = arg("workflow");
const log = (...a) => console.log(`[${new Date().toISOString()}]`, ...a);

async function cli(args) {
  try {
    const { stdout } = await run(OXYGEN, ["--profile", PROFILE, ...args], { maxBuffer: 64 * 1024 * 1024 });
    return JSON.parse(stdout.slice(stdout.indexOf("{")));
  } catch (error) {
    const out = String(error.stdout ?? "");
    if (out.includes("{")) return JSON.parse(out.slice(out.indexOf("{")));
    throw error;
  }
}

const WRITES = new Set(["linkedin.chats_create", "linkedin.chats_messages_send", "linkedin.posts_comment_create"]);

async function tool(name, args, opts = {}) {
  if (name.startsWith("linkedin.")) {
    const cmd = ["tools", "run", name, "--input-json", JSON.stringify(args), "--mode", "live"];
    if (opts.connectionId) cmd.push("--connection-id", opts.connectionId);
    if (WRITES.has(name)) cmd.push("--approved");
    const out = await cli(cmd);
    if (out?.ok === false) return out;
    return out.result ?? out.data?.result ?? out.data ?? out;
  }
  let out;
  switch (name) {
    case "oxygen.rows_query":
      out = await cli(["tables", "query", args.table, "--limit", String(args.limit ?? 100), "--json"]);
      break;
    case "oxygen.rows_upsert":
      out = await cli(["tables", "upsert", args.table, "--key", args.key, "--rows-json", JSON.stringify(args.rows), "--json"]);
      break;
    case "oxygen_suppressions_list":
      out = await cli(["suppressions", "list", "--search", String(args.search), "--limit", String(args.limit ?? 100), "--json"]);
      break;
    case "oxygen_sequences_list": {
      const cmd = ["sequences", "list", "--json"];
      if (args.status) cmd.push("--status", args.status);
      if (args.operational_state) cmd.push("--operational-state", args.operational_state);
      out = await cli(cmd);
      break;
    }
    case "oxygen_sequences_enrollments":
      out = await cli(["sequences", "enrollments", args.sequence, "--limit", String(args.limit ?? 500), "--json"]);
      break;
    case "oxygen_sequences_contacts": {
      const cmd = ["sequences", "contacts", args.sequence, "--limit", String(args.limit ?? 20), "--json"];
      if (args.cursor) cmd.push("--cursor", args.cursor);
      out = await cli(cmd);
      break;
    }
    default:
      throw new Error(`No local mapping for tool ${name}`);
  }
  if (out?.ok === false) {
    if (opts.optional) return out;
    throw new Error(`${name} failed: ${JSON.stringify(out.error).slice(0, 400)}`);
  }
  return out.data ?? out;
}

async function hostedWorks(slug) {
  const out = await cli(["workflows", "runs", "--workflow", slug, "--mode", "live", "--limit", "5", "--json"]);
  const runs = Object.values(out.data ?? {}).find(Array.isArray) ?? [];
  const scheduled = runs.find((r) => (r.triggerType ?? r.trigger_type) === "cron");
  return scheduled?.status === "completed";
}

// One run at a time per recipe.
const lock = join(dirname(recipePath), `.${recipePath.split("/").pop()}.lock`);
if (existsSync(lock)) {
  log("previous run still active, skipping", lock);
  process.exit(0);
}
closeSync(openSync(lock, "w"));
const release = () => { try { unlinkSync(lock); } catch {} };
process.on("exit", release);
process.on("SIGINT", () => process.exit(130));
process.on("SIGTERM", () => process.exit(143));

try {
  if (hostedSlug && await hostedWorks(hostedSlug)) {
    log(`hosted workflow ${hostedSlug} completed its latest scheduled run; local runner stands down`);
    process.exit(0);
  }
  // Swap the SDK import for an identity shim so the recipe loads outside the bundler.
  const source = readFileSync(recipePath, "utf8").replace(
    /import \{ defineRecipe \} from "@oxygen\/recipe-sdk";/,
    "const defineRecipe = (r) => r;",
  );
  const shim = join(dirname(recipePath), `.${recipePath.split("/").pop()}.local.mjs`);
  writeFileSync(shim, source);
  const recipe = (await import(pathToFileURL(shim).href + `?t=${Date.now()}`)).default;
  const ctx = {
    mode: "live",
    input,
    now: async () => new Date().toISOString(),
    wait: async (key, { seconds }) => {
      log(`wait ${seconds}s (${key})`);
      await new Promise((r) => setTimeout(r, seconds * 1000));
    },
    tools: { run: tool },
  };
  log(`running ${recipe.name} input=${JSON.stringify(input)}`);
  const result = await recipe.run(ctx);
  log(JSON.stringify(result, null, 1));
} catch (error) {
  log("FAILED", error.stack ?? error);
  process.exitCode = 1;
}

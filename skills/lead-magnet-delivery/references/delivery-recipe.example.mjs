import { defineRecipe } from "@oxygen/recipe-sdk";

// Comment-to-DM delivery for 1 LinkedIn lead-magnet post, as an OXYGEN durable recipe.
// Fill in every <PLACEHOLDER> below from your own workspace before applying it.
// Per new lead magnet, change only: POST, ASSET, TABLE, wantsAsset(), the DM text in run() ("Heyo ..."),
// the recipe id and name. Keep the rest.
// Dates are parsed with isoMs: the durable sandbox rejects Date.parse, new Date and Date.now on scheduled runs.
var ACCOUNT = "<YOUR_LINKEDIN_ACCOUNT_ID>"; // oxygen senders list --json
var SENDER = "<YOUR_SENDER_ID>"; // the sender id that owns ACCOUNT
var CONNECTION = "<YOUR_LINKEDIN_CONNECTION_ID>";
var ME = "<YOUR_LINKEDIN_PROVIDER_ID>"; // your own LinkedIn member id, to skip your own comments
var POST = "<COMPOSITE_POST_ID>"; // response.id of linkedin.posts_get
// Must be unique per post: the delivery check looks for ASSET inside the DM thread, so a URL an earlier
// magnet already sent would count as delivered. Use a README anchor or a UTM-tagged URL per post.
var ASSET = "<RESOURCE_URL>";
var TABLE = "<LEDGER_TABLE_ID>";
// Switch off when comment writes on a busy post keep timing out or the provider reports it is busy. DMs keep
// running; turn it back on, then run once with {"backfill_acknowledgements": true} to post the missing replies.
var PUBLIC_REPLIES = true;
// The working-hours guard below computes Central European time (CET/CEST, EU daylight-saving rule). Set this to
// the sender's working-hours timezone; for another zone, adapt STANDARD_OFFSET_MIN and the DST rule in localClock,
// otherwise the guard is skipped and only the cron hours limit sending.
var CLOCK_TIMEZONE = "Europe/Berlin";
var STANDARD_OFFSET_MIN = 60;
var CONNECT_REPLIES = [
  "We first need to connect :) Send me a connection request so I can send you the repo.",
  "Shoot me a connection request and I'll get it to you \u{1F64F}\u{1F3FB}",
  "We need to be connected first :) Send me a request and the repo is yours."
];
var SENT_REPLIES = [
  "Sent it over:)",
  "Sent:)",
  "It's in your inbox\u{1F44D}\u{1F3FB}",
  "Just sent it over\u{1F64F}\u{1F3FB}",
  "Check your DMs:)"
];
function pick(list2, key) {
  let h = 0;
  for (const ch of String(key)) h = h * 31 + ch.codePointAt(0) >>> 0;
  return list2[h % list2.length];
}
var MAX_INSPECTED_PER_CYCLE = 150;
var MAX_DMS_PER_CYCLE = 12;
var MAX_PUBLIC_REPLIES_PER_CYCLE = 6;
var MAX_DELIVERY_REPLIES_PER_CYCLE = 12;
var MESSAGE_RESERVE = 2;
var OTHER_CAMPAIGN_RECHECK_MS = 24 * 60 * 60 * 1e3;
var RETRY_UNCONFIRMED_AFTER_MS = 15 * 60 * 1e3;
var MAX_WRITE_ATTEMPTS = 2;
var MAX_THREAD_READS_PER_CYCLE = 3;
var THREAD_READ_BACKOFF_MS = 3 * 60 * 60 * 1e3;
var BREAKER_ID = "~reply-thread-reads";
var FIRST_DEGREE = ["FIRST_DEGREE", "DISTANCE_1"];
var SECOND_DEGREE = ["SECOND_DEGREE", "DISTANCE_2"];
// 3rd-degree commenters cannot be DMed but can still send a connection request, so they get the same
// public "connect first" reply; the DM follows once connected.
var THIRD_DEGREE = ["THIRD_DEGREE", "DISTANCE_3"];
// Give every automation on the same LinkedIn account its own cron minutes (here :07/:22/:37/:52). 2 workflows on
// the same quarter hour race for the sender spacing, and a sender_spacing refusal ends the run as an uncertain write.
function civilDays(y, mo, d) {
  const yy = y - (mo <= 2 ? 1 : 0);
  const era = Math.floor(yy / 400);
  const yoe = yy - era * 400;
  const doy = Math.floor((153 * (mo + (mo > 2 ? -3 : 9)) + 2) / 5) + d - 1;
  return era * 146097 + yoe * 365 + Math.floor(yoe / 4) - Math.floor(yoe / 100) + doy - 719468;
}
function isoMs(value) {
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?Z$/.exec(String(value ?? ""));
  if (!m) return NaN;
  const days = civilDays(+m[1], +m[2], +m[3]);
  return ((days * 24 + +m[4]) * 60 + +m[5]) * 6e4 + +m[6] * 1e3 + +(m[7] ?? "0").slice(0, 3).padEnd(3, "0");
}
function localClock(value) {
  const ms = isoMs(value);
  if (!Number.isFinite(ms)) return null;
  const y = +String(value).slice(0, 4);
  const lastSunday = (mo) => {
    const days = civilDays(y, mo, 31);
    return days - (days + 4) % 7;
  };
  const summer = ms >= lastSunday(3) * 864e5 + 36e5 && ms < lastSunday(10) * 864e5 + 36e5;
  const local = Math.floor(ms / 6e4) + STANDARD_OFFSET_MIN + (summer ? 60 : 0);
  const weekday = (Math.floor(local / 1440) + 4) % 7;
  return { minute: (local % 1440 + 1440) % 1440, weekday: weekday === 0 ? 7 : weekday };
}
function withinWorkingHours(hours, now) {
  if (!hours || hours.timezone !== CLOCK_TIMEZONE) return true;
  const clock = localClock(now);
  const toMinute = (hhmm) => {
    const m = /^(\d{1,2}):(\d{2})$/.exec(String(hhmm ?? ""));
    return m ? +m[1] * 60 + +m[2] : NaN;
  };
  const start = toMinute(hours.start), end = toMinute(hours.end);
  if (!clock || !Number.isFinite(start) || !Number.isFinite(end)) return true;
  if (Array.isArray(hours.days) && hours.days.length && !hours.days.includes(clock.weekday)) return false;
  return clock.minute >= start && clock.minute < end - 5;
}
function effectiveSendCap(value, factors) {
  let cap = Number(value);
  if (!Number.isFinite(cap) || cap <= 0) return cap;
  for (const factor of factors) if (factor > 0 && factor < 1) cap = Math.max(1, Math.floor(cap * factor));
  return cap;
}
function unpack(value) {
  if (value?.structuredContent) return unpack(value.structuredContent);
  if (Array.isArray(value?.content)) {
    const text = value.content.find((c) => c.type === "text")?.text;
    if (text) {
      try {
        return unpack(JSON.parse(text));
      } catch {
      }
    }
  }
  if (value?.ok === false || value?.isError) throw new Error(JSON.stringify(value.error ?? value));
  return value?.data && !Array.isArray(value.data) ? value.data : value;
}
function page(value) {
  const r = unpack(value);
  return r?.response ?? r;
}
function list(value) {
  const p = page(value);
  return p?.items ?? p?.data ?? [];
}
function next(value) {
  const p = page(value);
  return p?.cursor ?? p?.next_cursor ?? p?.next_page_token;
}
function own(c) {
  return c.is_sender === true || c.author?.id === ME;
}
function wantsAsset(c) {
  const text = String(c.text ?? "");
  if (/\b(send|share)\b.*\b(repo|resource|system|template|skills?|kit|it|over)\b/i.test(text)) return true;
  // Bare asks without a noun ("please send :)") are requests too.
  if (/\bplease send\b|\bsend (it|me|over|pls|please)\b|\bsend\W*$/i.test(text)) return true;
  return /\bKEYWORD\b/i.test(text); // replace KEYWORD with the post's CTA keyword, tolerant of typos
}
function blocksRequestedResource(s) {
  return !(s?.reason === "replied" && s?.source === "linkedin_inbound");
}
function profileKey(value) {
  return String(value ?? "").trim().toLowerCase().replace(new RegExp("^https?://(?:[a-z]+\\.)?linkedin\\.com/"), "linkedin.com/").split(/[?#]/)[0].replace(/\/$/, "");
}
var OPEN_ENROLLMENT_STATUSES = ["pending", "active", "waiting_connection", "waiting_signal"];
async function readCampaignHistory(call) {
  const sequences = /* @__PURE__ */ new Map();
  const collect = async (filters, key, depth) => {
    const result = await call("oxygen_sequences_list", filters, key);
    if (!Array.isArray(result.sequences)) throw new Error("Campaign exclusion check unavailable.");
    const clipped = result.structured_truncation?.dropped_items?.sequences > 0 || result.sequences.length < result.count;
    if (clipped) {
      if (depth === 0) {
        await collect({ status: "active" }, `${key}-active`, 1);
        return;
      }
      throw new Error("Campaign list remains truncated; refusing outreach.");
    }
    for (const s of result.sequences) {
      if (!Array.isArray(s.channels)) throw new Error("Campaign channel metadata unavailable.");
      if (s.channels.includes("linkedin") && s.status === "active") sequences.set(s.id, s);
    }
  };
  await collect({}, "campaigns", 0);
  const complete = (page2) => Array.isArray(page2.enrollments) && page2.enrollments.length < 500 && page2.enrollments.length >= (page2.count ?? 0) && !page2.structured_truncation;
  const history = [];
  for (const s of sequences.values()) {
    const all = await call("oxygen_sequences_enrollments", { sequence: s.id, limit: 500 }, `campaign-enrollments-${s.id}`);
    if (complete(all)) {
      history.push(...all.enrollments);
      continue;
    }
    // OXYGEN can trim large tool results for context size (structured_truncation), so a full-view page of 500 may
    // return only a few enrollments. Page each open status by offset: this page's offset plus the rows shown.
    for (const status of OPEN_ENROLLMENT_STATUSES) {
      let offset = 0;
      for (let p = 0; ; p++) {
        if (p >= 60) throw new Error("Open enrollment list too long; refusing outreach.");
        const open = await call("oxygen_sequences_enrollments", { sequence: s.id, status, limit: 25, ...offset ? { offset } : {} }, `campaign-enrollments-${s.id}-${status}-${offset}`);
        if (!Array.isArray(open.enrollments)) throw new Error("Open enrollment list unavailable; refusing outreach.");
        history.push(...open.enrollments);
        offset += open.enrollments.length;
        if (offset >= (open.count ?? 0)) break;
        if (open.enrollments.length === 0) throw new Error("Open enrollment list truncated; refusing outreach.");
      }
    }
  }
  return history;
}
var recipe_default = defineRecipe({
  id: "<post-slug>-delivery",
  name: "<Resource name>: Resource Delivery (15 min)",
  status: "disabled",
  trigger: { type: "cron", cron: "7,22,37,52 7-23 * * *", timezone: "<YOUR_TIMEZONE>", status: "disabled", metadata: { catchup: "coalesce" } },
  inputSchema: { type: "object", properties: { audit: { type: "boolean" }, backfill_acknowledgements: { type: "boolean" }, backfill_requests: { type: "boolean" }, target_provider_ids: { type: "array", items: { type: "string", minLength: 1 }, maxItems: 100, uniqueItems: true } }, additionalProperties: false },
  tools: ["linkedin.posts_comments_list", "linkedin.posts_comment_create", "linkedin.chats_list", "linkedin.chats_messages_list", "linkedin.chats_create", "linkedin.chats_messages_send", "oxygen.rows_query", "oxygen.rows_upsert", "oxygen_suppressions_list", "oxygen_sequences_list", "oxygen_sequences_enrollments", "oxygen_sequences_contacts", "oxygen_senders_get"],
  async run(ctx) {
    const now = await ctx.now();
    const input = ctx.input ?? {};
    const audit = input.audit === true || ctx.mode !== "live";
    const backfill = input.backfill_acknowledgements === true;
    const requestBackfill = input.backfill_requests === true;
    const targets = new Set(input.target_provider_ids ?? []);
    if (requestBackfill && (!targets.size || backfill)) throw new Error("Request backfill requires explicit recipient scope and cannot combine with acknowledgement-only mode.");
    const inspectionLimit = backfill || requestBackfill ? 100 : MAX_INSPECTED_PER_CYCLE;
    const deliveryReplyLimit = backfill ? 40 : MAX_DELIVERY_REPLIES_PER_CYCLE;
    const connectionReplyLimit = requestBackfill ? 12 : MAX_PUBLIC_REPLIES_PER_CYCLE;
    if (input.scheduled_for && isoMs(now) - isoMs(input.scheduled_for) > 9 * 60 * 1e3) return { skipped: "stale_tick" };
    const call = async (tool, args, key) => unpack(await ctx.tools.run(tool, args, { key, ...tool.startsWith("linkedin.") ? { connectionId: CONNECTION } : {} }));
    const ledgerPage = await call("oxygen.rows_query", { table: TABLE, limit: 1e3 }, "ledger");
    const ledger = new Map((ledgerPage.rows ?? []).map((r) => [r.provider_id, r]));
    if ((ledgerPage.rows ?? []).length >= 1e3) throw new Error("Ledger capacity reached; review before extending scope.");
    const comments = [];
    let cursor;
    for (let p = 0; p < 5; p++) {
      const response = await call("linkedin.posts_comments_list", { account_id: ACCOUNT, post_id: POST, limit: 100, sort_by: "MOST_RECENT", ...cursor ? { cursor } : {} }, `comments-${p}`);
      comments.push(...list(response));
      cursor = next(response);
      if (!cursor) break;
    }
    if (cursor) throw new Error("Post exceeds 500 comments; complete scan required before sending.");
    // LinkedIn's MOST_RECENT list can lag and leave out the newest comments. Read MOST_RELEVANT as well and merge by
    // comment id; if that read fails, keep the MOST_RECENT list.
    const seenComments = new Set(comments.map((c) => c.id));
    let relevantCursor;
    for (let p = 0; p < 5; p++) {
      const raw = await ctx.tools.run("linkedin.posts_comments_list", { account_id: ACCOUNT, post_id: POST, limit: 100, sort_by: "MOST_RELEVANT", ...relevantCursor ? { cursor: relevantCursor } : {} }, { key: `comments-relevant-${p}`, optional: true, connectionId: CONNECTION });
      if (raw?.ok === false) break;
      let response;
      try {
        response = unpack(raw);
      } catch {
        break;
      }
      for (const c of list(response)) {
        if (c?.id && !seenComments.has(c.id)) {
          seenComments.add(c.id);
          comments.push(c);
        }
      }
      relevantCursor = next(response);
      if (!relevantCursor) break;
    }
    let chats;
    const loadChats = async () => {
      if (chats) return chats;
      chats = /* @__PURE__ */ new Map();
      let chatCursor;
      for (let p = 0; p < 2; p++) {
        const response = await call("linkedin.chats_list", { account_id: ACCOUNT, limit: 20, ...chatCursor ? { cursor: chatCursor } : {} }, `chats-${p}`);
        const batch = list(response);
        for (const chat of batch) if (chat.is_1to1 && chat.user_id) chats.set(chat.user_id, chat);
        chatCursor = next(response);
        if (!chatCursor || batch.length < 20) break;
      }
      return chats;
    };
    const groups = /* @__PURE__ */ new Map();
    for (const c of comments) {
      const id = c.author?.id;
      if (id && !own(c) && (!targets.size || targets.has(id))) groups.set(id, [...groups.get(id) ?? [], c]);
    }
    const plan = [];
    let inspected = 0, sent = 0, dmAttempts = 0, publicWrites = 0, deliveryReplies = 0, connectionReplies = 0;
    let externalAttempts = 0, accountReads = 0;
    let dmFull = false, commentFull = false, outOfHours = false;
    const account = async (key, at) => {
      accountReads++;
      const raw = await ctx.tools.run("oxygen_senders_get", { id: SENDER }, { key: `account-${key}`, optional: true });
      let data;
      try {
        data = unpack(raw);
      } catch {
        return { known: false };
      }
      const sender = data?.account?.sender ?? data?.sender ?? data ?? {};
      const limits = sender.limits ?? {};
      const today = sender.usage?.today ?? {};
      const meta = sender.metadata ?? {};
      const slots = [meta.sequence_next_action_at, meta.interactive_next_action_at].map(isoMs).filter((n) => Number.isFinite(n));
      const clock = sender.workingHours?.timezone === CLOCK_TIMEZONE ? localClock(at) : null;
      const weekend = meta.weekend_full_volume !== true && clock && clock.weekday >= 6 ? 0.5 : 1;
      const factors = [weekend, Number(meta.health?.factor)];
      const rampMessages = Number(sender.warmup?.effective_messages_per_day);
      const messageCap = Math.min(effectiveSendCap(limits.messages_per_day, factors), Number.isFinite(rampMessages) ? rampMessages : Infinity);
      const messagesLeft = messageCap - Number(today.message ?? 0);
      const commentsLeft = effectiveSendCap(limits.comments_per_day, factors) - Number(today.comment ?? 0);
      const actionsLeft = effectiveSendCap(limits.total_actions_per_day, factors) - Number(sender.usage?.sendsToday);
      if (!Number.isFinite(messagesLeft) || !Number.isFinite(commentsLeft)) return { known: false };
      return { known: true, messagesLeft, commentsLeft, actionsLeft, nextAt: slots.length ? Math.max(...slots) : NaN, hours: sender.workingHours };
    };
    const beforeWrite = async (kind, key) => {
      const at = await ctx.now();
      const state = await account(key, at);
      if (state.known) {
        if (state.actionsLeft <= 0) {
          dmFull = true;
          commentFull = true;
          return "action_cap_reached";
        }
        if (kind === "dm" && state.messagesLeft <= MESSAGE_RESERVE) {
          dmFull = true;
          return "dm_cap_reached";
        }
        if (kind === "reply" && state.commentsLeft <= 0) {
          commentFull = true;
          return "comment_cap_reached";
        }
        if (!withinWorkingHours(state.hours, at)) {
          outOfHours = true;
          return "outside_working_hours";
        }
        const waitMs = state.nextAt - isoMs(at);
        if (waitMs > 0) await ctx.wait(`spacing-${key}`, { seconds: Math.ceil(waitMs / 1e3) + 5 });
      } else if (externalAttempts > 0) {
        await ctx.wait(`pace-${key}`, { seconds: 140 });
      }
      externalAttempts++;
      return "ok";
    };
    const save = async (row, suffix) => {
      if (audit) return;
      await call("oxygen.rows_upsert", { table: TABLE, key: "provider_id", rows: [row], return: "summary" }, `save-${row.provider_id}-${suffix}`);
      ledger.set(row.provider_id, row);
    };
    const saveIntent = async (row, kind, suffix, retrying) => {
      const earlier = row.write_intent?.kind === kind ? Number(row.write_intent.attempts) || 0 : 0;
      row.write_intent = { kind, at: await ctx.now(), attempts: Math.max(earlier, retrying ? 1 : 0) + 1 };
      await save(row, suffix);
    };
    const retryable = (previous, kind) => {
      const intent = previous?.write_intent?.kind === kind ? previous.write_intent : null;
      const attempts = intent ? Number(intent.attempts) || 1 : 1;
      const at = isoMs(intent ? intent.at : previous?.last_checked_at);
      return attempts < MAX_WRITE_ATTEMPTS && Number.isFinite(at) && isoMs(now) - at >= RETRY_UNCONFIRMED_AFTER_MS;
    };
    const isDelivery = (m) => (m?.sender_id === ME || m?.sender?.id === ME) && String(m?.text ?? "").includes(ASSET) && m?.is_deleted !== true;
    const suppressed = async (pid, url) => {
      const keys = [pid, ...url ? [profileKey(url).split("/").pop()] : []];
      for (let i = 0; i < keys.length; i++) {
        const data = await call("oxygen_suppressions_list", { search: keys[i], limit: 500 }, `suppression-${pid}-${i}`);
        if (!Array.isArray(data.suppressions) || data.suppressions.length >= 500 || data.structured_truncation?.dropped_items?.suppressions) throw new Error("Incomplete suppression check; refusing outreach.");
        if (data.suppressions.some((s) => blocksRequestedResource(s) && (s.leadProviderId === pid || url && profileKey(s.leadProviderId) === profileKey(url)))) return true;
      }
      return false;
    };
    let otherEnrollments;
    const enrollmentHistory = async () => {
      if (otherEnrollments) return otherEnrollments;
      otherEnrollments = await readCampaignHistory(call);
      return otherEnrollments;
    };
    // DMs first: uncertain DMs, then first-degree requests without a delivery (including people who connected after a
    // public "connect first" reply), then open public replies. Otherwise reply work fills the inspection cap and
    // first-degree requests wait indefinitely on a busy post.
    const priority = (pid) => {
      const state = ledger.get(pid)?.state;
      if (["dm_send_pending", "dm_sent_unverified"].includes(state)) return 0;
      const request = groups.get(pid)?.find(wantsAsset);
      const degree = request?.author?.specifics?.network_distance ?? request?.author?.network_distance;
      if (FIRST_DEGREE.includes(degree) && (!state || ["new", "waiting_connection"].includes(state))) return 1;
      if (["sent_reply_pending", "connect_reply_pending"].includes(state)) return 2;
      if (state === "delivered") return 3;
      if ((SECOND_DEGREE.includes(degree) || THIRD_DEGREE.includes(degree)) && (!state || state === "new")) return 4;
      return 5;
    };
    const ordered = [...groups.entries()].sort((a, b) => priority(a[0]) - priority(b[0]) || String(ledger.get(a[0])?.last_checked_at ?? "").localeCompare(String(ledger.get(b[0])?.last_checked_at ?? "")));
    const breaker = ledger.get(BREAKER_ID);
    const threadReadsPausedUntil = breaker?.state === "thread_read_started" ? isoMs(breaker.last_checked_at) + THREAD_READ_BACKOFF_MS : -Infinity;
    let threadReads = 0, breakerArmed = false;
    const queue = ordered.map(([pid, personComments]) => ({ pid, personComments, late: false }));
    const queuedLate = /* @__PURE__ */ new Set();
    const replyJobs = [];
    for (let q = 0; q < queue.length; q++) {
      const { pid, personComments, late } = queue[q];
      const previous = ledger.get(pid);
      if (["handled_existing_reply", "complete", "suppressed"].includes(previous?.state)) continue;
      const comment = personComments.find(wantsAsset);
      if (!comment) continue;
      const degree = comment.author?.specifics?.network_distance ?? comment.author?.network_distance;
      const connected = FIRST_DEGREE.includes(degree);
      const second = SECOND_DEGREE.includes(degree) || THIRD_DEGREE.includes(degree);
      const name = comment.author.display_name ?? comment.author.name ?? "";
      const recordedCommentLive = personComments.some((c) => c.id === previous?.comment_id);
      const row = { provider_id: pid, name, first_name: name.trim().split(/\s+/).map((part) => part.replace(/^[^\p{L}\p{N}]+/u, "")).find(Boolean) || "there", profile_url: comment.author.profile_url ?? "", comment_id: recordedCommentLive ? previous.comment_id : comment.id, comment_text: comment.text ?? "", connection_degree: degree ?? "unknown", last_checked_at: now, state: previous?.state ?? "new", enrollment_id: previous?.enrollment_id ?? "", reply_text: previous?.reply_text ?? "", note: previous?.note ?? "", delivery_receipt: previous?.delivery_receipt ?? null, write_intent: previous?.write_intent ?? null };
      const knownDelivered = row.state === "delivered";
      const uncertainDm = ["dm_send_pending", "dm_sent_unverified"].includes(row.state);
      const uncertainReply = ["connect_reply_pending", "sent_reply_pending"].includes(previous?.state);
      let retryingDm = false, retryingReply = false;
      if (!uncertainReply) {
        if (!knownDelivered && !connected && !second) {
          plan.push({ name, action: "skip_unknown_or_third_degree", degree });
          continue;
        }
        if (!knownDelivered && !connected && (previous?.state === "waiting_connection" || backfill)) {
          plan.push({ name, action: backfill ? "backfill_skip_no_verified_delivery" : "await_connection" });
          continue;
        }
        if (previous?.state === "other_campaign" && isoMs(now) - isoMs(previous.last_checked_at) < OTHER_CAMPAIGN_RECHECK_MS) {
          plan.push({ name, action: "skip_other_campaign_or_sender" });
          continue;
        }
        const full = outOfHours || (knownDelivered ? deliveryReplies >= deliveryReplyLimit || commentFull : connected ? dmAttempts >= MAX_DMS_PER_CYCLE || dmFull : connectionReplies >= connectionReplyLimit || commentFull);
        if (full) {
          plan.push({ name, action: "next_cycle" });
          continue;
        }
      }
      const knownOwn = CONNECT_REPLIES.includes(previous?.reply_text) && previous?.state !== "connect_reply_pending" ? 1 : 0;
      const threadTargets = personComments.filter((c) => (Number(c.reply_counter) || 0) > (c.id === row.comment_id ? knownOwn : 0));
      if (threadTargets.length) {
        if (!late) {
          if (!queuedLate.has(pid)) {
            queuedLate.add(pid);
            queue.push({ pid, personComments, late: true });
          }
          continue;
        }
        if (threadReads >= MAX_THREAD_READS_PER_CYCLE || isoMs(now) < threadReadsPausedUntil) {
          plan.push({ name, action: "thread_read_later" });
          continue;
        }
      }
      if (!uncertainReply && !knownDelivered && !uncertainDm) {
        if (inspected >= inspectionLimit) break;
        if (await suppressed(pid, row.profile_url)) {
          row.state = "suppressed";
          row.note = "Workspace do-not-contact match; no further outreach.";
          await save(row, "suppressed");
          plan.push({ name, action: "skip_suppressed" });
          continue;
        }
        if (connected) {
          const history = (await enrollmentHistory()).filter((e) => e.leadProviderId === pid || row.profile_url && profileKey(e.leadProfileUrl) === profileKey(row.profile_url));
          if (history.some((e) => OPEN_ENROLLMENT_STATUSES.includes(e.status) || e.senderAccountId && e.senderAccountId !== SENDER)) {
            row.state = "other_campaign";
            row.note = "Active in another LinkedIn campaign or owned by another sender; rechecked daily.";
            await save(row, "other-campaign");
            plan.push({ name, action: "skip_other_campaign_or_sender" });
            continue;
          }
        }
      }
      if (inspected >= inspectionLimit) break;
      inspected++;
      const ownReplies = [];
      if (threadTargets.length && !breakerArmed) {
        breakerArmed = true;
        await save({ provider_id: BREAKER_ID, state: "thread_read_started", last_checked_at: await ctx.now(), note: "A run that stops inside a comment-reply read pauses these reads for three hours." }, "armed");
      }
      for (const c of threadTargets) {
        let replyCursor;
        for (let p = 0; p < 3; p++) {
          const response = await call("linkedin.posts_comments_list", { account_id: ACCOUNT, post_id: POST, comment_id: c.id, limit: 100, ...replyCursor ? { cursor: replyCursor } : {} }, `replies-${c.id}-${p}`);
          ownReplies.push(...list(response).filter(own));
          replyCursor = next(response);
          if (!replyCursor) break;
        }
        if (replyCursor) throw new Error("Reply scan truncated; refusing delivery without a complete duplicate check.");
      }
      if (threadTargets.length) threadReads++;
      const waitingConnection = ["waiting_connection", "connect_reply_pending"].includes(previous?.state) || CONNECT_REPLIES.includes(previous?.reply_text);
      const repliedSent = ownReplies.some((r) => /\bsent\b|\binbox\b|\bdms?\b/i.test(r.text ?? ""));
      if (ownReplies.length && (!waitingConnection || repliedSent)) {
        row.state = previous?.state === "sent_reply_pending" ? "complete" : "handled_existing_reply";
        row.note = "Already replied by hand; do not send the resource again.";
        await save(row, "existing-reply");
        plan.push({ name, action: "skip_existing_reply" });
        continue;
      }
      if (previous?.state === "connect_reply_pending") {
        if (ownReplies.length) {
          row.state = "waiting_connection";
          await save(row, "connect-confirmed");
        } else if (retryable(previous, "reply")) {
          row.state = "new";
          row.note = "Unconfirmed connection reply absent after 15 minutes; retrying once.";
          retryingReply = true;
        } else {
          plan.push({ name, action: "review_uncertain_public_reply" });
          continue;
        }
      }
      if (previous?.state === "sent_reply_pending") {
        if (!recordedCommentLive) {
          row.state = "complete";
          row.note = "Resource delivered; the requesting comment was deleted, so no public reply.";
          await save(row, "comment-gone");
          plan.push({ name, action: "complete_comment_deleted" });
          continue;
        }
        if (!retryable(previous, "reply")) {
          plan.push({ name, action: "review_uncertain_public_reply" });
          continue;
        }
        row.state = "delivered";
        row.note = "Unconfirmed delivery reply absent after 15 minutes; retrying once.";
        retryingReply = true;
      }
      const chat = (await loadChats()).get(pid) ?? (row.delivery_receipt?.chat_id ? { id: row.delivery_receipt.chat_id } : void 0);
      let delivered = row.state === "delivered" || isDelivery(chat?.last_message);
      if (!connected && !second && !delivered) {
        plan.push({ name, action: "skip_unknown_or_third_degree", degree });
        continue;
      }
      if (!delivered && chat) {
        const messages = await call("linkedin.chats_messages_list", { account_id: ACCOUNT, chat_id: chat.id, limit: 20 }, `messages-${pid}`);
        const confirmed = list(messages).find(isDelivery);
        delivered = Boolean(confirmed);
        if (confirmed && row.delivery_receipt) row.delivery_receipt = { ...row.delivery_receipt, status: "verified", message_id: confirmed.id ?? row.delivery_receipt.message_id, verified_at: now };
      }
      if (backfill && !delivered) {
        plan.push({ name, action: "backfill_skip_no_verified_delivery" });
        continue;
      }
      if (!delivered && uncertainDm) {
        if (row.state === "dm_send_pending" && retryable(previous, "dm")) {
          row.state = "new";
          row.note = "DM intent unconfirmed and absent from the chat after 15 minutes; retrying once.";
          retryingDm = true;
        } else {
          plan.push({ name, action: "review_uncertain_dm" });
          continue;
        }
      }
      if (connected && !delivered) {
        if (dmAttempts >= MAX_DMS_PER_CYCLE || dmFull || outOfHours) {
          plan.push({ name, action: "next_cycle" });
          continue;
        }
        const text2 = `Heyo ${row.first_name}:)

Here is the <resource>:

${ASSET}`;
        if (audit) {
          plan.push({ name, action: "send_resource_dm", comment_id: row.comment_id });
          dmAttempts++;
          continue;
        }
        const gate2 = await beforeWrite("dm", `dm-${pid}`);
        if (gate2 !== "ok") {
          plan.push({ name, action: gate2 });
          continue;
        }
        plan.push({ name, action: "send_resource_dm", comment_id: row.comment_id });
        dmAttempts++;
        row.state = "dm_send_pending";
        row.note = "DM intent saved; do not resend an uncertain provider outcome.";
        await saveIntent(row, "dm", "dm-intent", retryingDm);
        const tool = chat ? "linkedin.chats_messages_send" : "linkedin.chats_create";
        const args = chat ? { account_id: ACCOUNT, chat_id: chat.id, text: text2 } : { account_id: ACCOUNT, attendees_ids: [pid], text: text2 };
        const raw2 = await ctx.tools.run(tool, args, { key: `dm-${pid}`, optional: true, connectionId: CONNECTION });
        if (raw2?.ok === false) {
          const errorText = JSON.stringify(raw2.error ?? {}).toLowerCase();
          if (/rate.limit|sender_spacing|working_hours|outside_working/.test(errorText) && !/unknown|uncertain/.test(errorText)) {
            row.state = "new";
            row.note = "Provider refused before sending; retry within native limits.";
            await save(row, "dm-paced");
          }
          continue;
        }
        const result2 = unpack(raw2);
        const receipt = result2?.response;
        if (!receipt || result2.meta?.ok === false) throw new Error("DM unconfirmed; intent remains pending for reconciliation.");
        const chatId = receipt.chat_id ?? chat?.id ?? (tool === "linkedin.chats_create" ? receipt.id : void 0);
        row.state = "dm_sent_unverified";
        row.delivery_receipt = { status: "accepted", chat_id: chatId ?? null, message_id: receipt.message_id ?? (chat ? receipt.id : null) ?? null, sender_account_id: SENDER, accepted_at: now };
        row.note = "Provider accepted DM; awaiting outgoing message readback before public acknowledgement.";
        await save(row, "dm-receipt");
        sent++;
        if (!chatId) {
          plan.push({ name, action: "review_missing_chat_receipt" });
          continue;
        }
        const messages = await call("linkedin.chats_messages_list", { account_id: ACCOUNT, chat_id: chatId, limit: 20 }, `verify-dm-${pid}`);
        const confirmed = list(messages).find(isDelivery);
        if (!confirmed) {
          plan.push({ name, action: "await_dm_readback" });
          continue;
        }
        row.delivery_receipt = { ...row.delivery_receipt, status: "verified", message_id: confirmed.id ?? row.delivery_receipt.message_id, verified_at: now };
        delivered = true;
      }
      if (!delivered && !connected && row.state === "waiting_connection") {
        plan.push({ name, action: "await_connection" });
        await save(row, "await-connection");
        continue;
      }
      if (delivered && row.state !== "delivered") {
        row.state = "delivered";
        row.note = "Outgoing resource DM verified; public acknowledgement pending.";
        await save(row, "delivery-confirmed");
      }
      // Public replies run after every DM in this cycle: a timed-out comment write stops the run,
      // so it must not hold back the DMs on a busy post.
      replyJobs.push(async () => {
        if (!PUBLIC_REPLIES && !backfill) {
          plan.push({ name, action: "reply_paused" });
          return;
        }
        if (outOfHours || (delivered ? deliveryReplies >= deliveryReplyLimit || commentFull : connectionReplies >= connectionReplyLimit || commentFull)) {
          if (row.state !== previous?.state) await save(row, "reply-deferred");
          plan.push({ name, action: "reply_next_cycle" });
          return;
        }
        const text = pick(delivered ? SENT_REPLIES : CONNECT_REPLIES, pid);
        if (audit) {
          plan.push({ name, action: delivered ? "confirm_delivery_publicly" : "request_connection_publicly", text, comment_id: row.comment_id });
          publicWrites++;
          if (delivered) deliveryReplies++;
          else connectionReplies++;
          return;
        }
        const gate = await beforeWrite("reply", `reply-${pid}`);
        if (gate !== "ok") {
          if (row.state !== previous?.state) await save(row, "reply-deferred");
          plan.push({ name, action: gate });
          return;
        }
        plan.push({ name, action: delivered ? "confirm_delivery_publicly" : "request_connection_publicly", text, comment_id: row.comment_id });
        publicWrites++;
        if (delivered) deliveryReplies++;
        else connectionReplies++;
        row.state = delivered ? "sent_reply_pending" : "connect_reply_pending";
        row.reply_text = text;
        row.note = "Write intent saved before public action; uncertain effects require reconciliation.";
        await saveIntent(row, "reply", "reply-intent", retryingReply);
        const raw = await ctx.tools.run("linkedin.posts_comment_create", { account_id: ACCOUNT, post_id: POST, comment_id: row.comment_id, text }, { key: `reply-${pid}`, optional: true, connectionId: CONNECTION });
        if (raw?.ok === false) {
          const errorText = JSON.stringify(raw.error ?? {}).toLowerCase();
          if (/rate.limit|sender_spacing|working_hours|outside_working/.test(errorText) && !/unknown|uncertain/.test(errorText)) {
            row.state = delivered ? "delivered" : "new";
            row.note = "Pacing refused before send; retry next cycle.";
            await save(row, "paced");
          }
          return;
        }
        const result = unpack(raw);
        if (!result?.response || result.meta?.ok === false) throw new Error("Public reply unconfirmed; intent remains pending for reconciliation.");
        row.state = delivered ? "complete" : "waiting_connection";
        row.note = delivered ? "Resource delivery confirmed, then public reply sent." : "Connection requested publicly; deliver once first-degree.";
        await save(row, "reply-confirmed");
      });
    }
    for (const job of replyJobs) await job();
    if (breakerArmed) await save({ provider_id: BREAKER_ID, state: "thread_read_ok", last_checked_at: now, note: "The last comment-reply reads completed." }, "cleared");
    return { ok: true, audit, backfill, backfill_requests: requestBackfill, thread_reads: threadReads, thread_reads_paused: isoMs(now) < threadReadsPausedUntil, target_count: targets.size, post: POST, comments_seen: comments.length, unique_people: groups.size, inspected, chats_read: Boolean(chats), account_reads: accountReads, dm_cap_reached: dmFull, comment_cap_reached: commentFull, outside_working_hours: outOfHours, resource_dms_sent: sent, dm_attempts: dmAttempts, public_reply_attempts: publicWrites, delivery_reply_attempts: deliveryReplies, connection_reply_attempts: connectionReplies, plan, max_new_dms_per_cycle: backfill ? 0 : MAX_DMS_PER_CYCLE, max_public_replies_per_cycle: backfill ? deliveryReplyLimit : connectionReplyLimit + deliveryReplyLimit, max_delivery_replies_per_cycle: deliveryReplyLimit, max_connection_replies_per_cycle: backfill ? 0 : connectionReplyLimit, max_inspected_per_cycle: inspectionLimit };
  }
});
export {
  blocksRequestedResource,
  recipe_default as default,
  localClock,
  effectiveSendCap,
  isoMs,
  readCampaignHistory,
  wantsAsset,
  withinWorkingHours
};

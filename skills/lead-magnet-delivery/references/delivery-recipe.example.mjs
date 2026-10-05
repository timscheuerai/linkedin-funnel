import { defineRecipe } from "@oxygen/recipe-sdk";

// Comment-to-DM delivery for 1 LinkedIn lead-magnet post, as an OXYGEN durable recipe.
// Fill in every <PLACEHOLDER> below from your own workspace before applying it.
// Per new lead magnet, change only: POST, ASSET, TABLE, wantsAsset(), the DM text
// in run() ("Heyo ..."), the recipe id and name. Keep the rest.
var ACCOUNT = "<YOUR_LINKEDIN_ACCOUNT_ID>"; // oxygen senders list --json
var SENDER = "<YOUR_SENDER_ID>"; // the sender id that owns ACCOUNT
var CONNECTION = "<YOUR_LINKEDIN_CONNECTION_ID>";
var ME = "<YOUR_LINKEDIN_PROVIDER_ID>"; // your own LinkedIn member id, to skip your own comments
var POST = "<COMPOSITE_POST_ID>"; // response.id of linkedin.posts_get
var ASSET = "<RESOURCE_URL>";
var TABLE = "<LEDGER_TABLE_ID>";
var SEQUENCE = "<OPTIONAL_SEQUENCE_ID>";
var SENDER_NAME = "<YOUR NAME AS THE SEQUENCE SENDER>";
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
function pick(list, key) {
  let h = 0;
  for (const ch of String(key)) h = (h * 31 + ch.codePointAt(0)) >>> 0;
  return list[h % list.length];
}
var MAX_INSPECTED_PER_CYCLE = 60;
var MAX_DMS_PER_CYCLE = 20;
var MAX_PUBLIC_REPLIES_PER_CYCLE = 10;
var MAX_DELIVERY_REPLIES_PER_CYCLE = 20;
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
  return /\bKEYWORD\b|\b(send|share)\b.*\b(repo|resource|system|template|kit|it|over)\b/i.test(c.text ?? ""); // replace KEYWORD
}
function profileKey(value) {
  return String(value ?? "").trim().toLowerCase().replace(new RegExp("^https?://(?:[a-z]+\\.)?linkedin\\.com/"), "linkedin.com/").split(/[?#]/)[0].replace(/\/$/, "");
}
async function readCampaignHistory(call) {
  const sequences = /* @__PURE__ */ new Map();
  const collect = async (filters, key, depth) => {
    const result = await call("oxygen_sequences_list", filters, key);
    if (!Array.isArray(result.sequences)) throw new Error("Campaign exclusion check unavailable.");
    const clipped = result.structured_truncation?.dropped_items?.sequences > 0 || result.sequences.length < result.count;
    if (clipped) {
      if (depth === 0) {
        for (const status of ["draft", "active", "paused", "archived"]) await collect({ status }, `${key}-${status}`, 1);
        return;
      }
      if (depth === 1) {
        for (const operational_state of ["empty", "drained", "blocked", "degraded", "flowing", "paced"]) await collect({ ...filters, operational_state }, `${key}-${operational_state}`, 2);
        return;
      }
      throw new Error("Campaign list remains truncated; refusing outreach.");
    }
    for (const s of result.sequences) {
      if (!Array.isArray(s.channels)) throw new Error("Campaign channel metadata unavailable.");
      if (s.channels.includes("linkedin")) sequences.set(s.id, s);
    }
  };
  await collect({}, "campaigns", 0);
  const history = [];
  for (const s of sequences.values()) {
    const result = await call("oxygen_sequences_enrollments", { sequence: s.id, limit: 500 }, `campaign-enrollments-${s.id}`);
    if (!Array.isArray(result.enrollments)) throw new Error("Enrollment history unavailable.");
    if (result.enrollments.length < 500 && result.enrollments.length >= (result.count ?? 0) && !result.structured_truncation?.dropped_items?.enrollments) {
      history.push(...result.enrollments);
      continue;
    }
    if (!s.linkedinUrlColumnKey) throw new Error("Incomplete enrollment history without a paged identity source.");
    let cursor, limit = 20, finished = false;
    for (let p = 0; p < 150; p++) {
      const page2 = await call("oxygen_sequences_contacts", { sequence: s.id, limit, ...cursor ? { cursor } : {} }, `campaign-contacts-${s.id}-${p}`);
      if (page2.orphan_count || !Array.isArray(page2.contacts)) throw new Error("Campaign contains unresolved enrollment identities.");
      if (page2.cursor_safe === false || page2.truncated_for_context) {
        if (!page2.retry_with_limit || page2.retry_with_limit >= limit) throw new Error("Cannot recover truncated campaign page.");
        limit = page2.retry_with_limit;
        continue;
      }
      if (page2.structured_truncation?.dropped_items?.contacts) throw new Error("Contact page incomplete.");
      for (const c of page2.contacts) {
        const status = c.__seq_status;
        if (!status || status === "not_enrolled") continue;
        const url = c[s.linkedinUrlColumnKey];
        if (!url) throw new Error("Enrolled campaign contact lacks LinkedIn identity.");
        history.push({ sequenceId: s.id, leadProfileUrl: url, status, senderAccountId: c.__seq_sender === SENDER_NAME ? SENDER : c.__seq_sender ? "other-sender" : null });
      }
      if (!page2.has_more) {
        finished = true;
        break;
      }
      if (!page2.next_cursor || page2.next_cursor === cursor) throw new Error("Campaign cursor did not advance.");
      cursor = page2.next_cursor;
    }
    if (!finished) throw new Error("Campaign history exceeded bounded pagination.");
  }
  return history;
}
var flow_default = defineRecipe({
  id: "<post-slug>-delivery",
  name: "<Resource name>: Resource Delivery",
  status: "disabled",
  trigger: { type: "cron", cron: "*/10 * * * *", timezone: "<YOUR_TIMEZONE>", status: "disabled", metadata: { catchup: "coalesce" } },
  inputSchema: { type: "object", properties: { audit: { type: "boolean" }, backfill_acknowledgements: { type: "boolean" }, backfill_requests: { type: "boolean" }, target_provider_ids: { type: "array", items: { type: "string", minLength: 1 }, maxItems: 100, uniqueItems: true } }, additionalProperties: false },
  tools: ["linkedin.posts_comments_list", "linkedin.posts_comment_create", "linkedin.chats_list", "linkedin.chats_messages_list", "linkedin.chats_create", "linkedin.chats_messages_send", "oxygen.rows_query", "oxygen.rows_upsert", "oxygen_suppressions_list", "oxygen_sequences_list", "oxygen_sequences_enrollments", "oxygen_sequences_contacts"],
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
    if (input.scheduled_for && Date.parse(now) - Date.parse(input.scheduled_for) > 9 * 60 * 1000) return { skipped: "stale_tick" };
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
    const chats = /* @__PURE__ */ new Map();
    let chatCursor;
    for (let p = 0; p < 2; p++) {
      const response = await call("linkedin.chats_list", { account_id: ACCOUNT, limit: 20, ...chatCursor ? { cursor: chatCursor } : {} }, `chats-${p}`);
      const batch = list(response);
      for (const chat of batch) if (chat.is_1to1 && chat.user_id) chats.set(chat.user_id, chat);
      chatCursor = next(response);
      if (!chatCursor || batch.length < 20) break;
    }
    const groups = /* @__PURE__ */ new Map();
    for (const c of comments) {
      const id = c.author?.id;
      if (id && !own(c) && (!targets.size || targets.has(id))) groups.set(id, [...groups.get(id) ?? [], c]);
    }
    const plan = [];
    let inspected = 0, sent = 0, dmAttempts = 0, publicWrites = 0, deliveryReplies = 0, connectionReplies = 0;
    let externalAttempts = 0;
    const pace = async (key) => {
      if (externalAttempts > 0) await ctx.wait(`pace-${key}`, { seconds: 185 });
      externalAttempts++;
    };
    const save = async (row, suffix) => {
      if (audit) return;
      await call("oxygen.rows_upsert", { table: TABLE, key: "provider_id", rows: [row], return: "summary" }, `save-${row.provider_id}-${suffix}`);
      ledger.set(row.provider_id, row);
    };
    const isDelivery = (m) => (m?.sender_id === ME || m?.sender?.id === ME) && String(m?.text ?? "").includes(ASSET) && m?.is_deleted !== true;
    const suppressed = async (pid, url) => {
      const keys = [pid, ...url ? [profileKey(url).split("/").pop()] : []];
      for (let i = 0; i < keys.length; i++) {
        const data = await call("oxygen_suppressions_list", { search: keys[i], limit: 500 }, `suppression-${pid}-${i}`);
        if (!Array.isArray(data.suppressions) || data.suppressions.length >= 500 || data.structured_truncation?.dropped_items?.suppressions) throw new Error("Incomplete suppression check; refusing outreach.");
        if (data.suppressions.some((s) => s.leadProviderId === pid || url && profileKey(s.leadProviderId) === profileKey(url))) return true;
      }
      return false;
    };
    let otherEnrollments;
    const enrollmentHistory = async () => {
      if (otherEnrollments) return otherEnrollments;
      otherEnrollments = await readCampaignHistory(call);
      return otherEnrollments;
    };
    const priority = (pid) => ["delivered", "enrolled", "dm_send_pending", "dm_sent_unverified", "sent_reply_pending"].includes(ledger.get(pid)?.state) || isDelivery(chats.get(pid)?.last_message) ? 0 : 1;
    const ordered = [...groups.entries()].sort((a, b) => priority(a[0]) - priority(b[0]) || String(ledger.get(a[0])?.last_checked_at ?? "").localeCompare(String(ledger.get(b[0])?.last_checked_at ?? "")));
    for (const [pid, personComments] of ordered) {
      const previous = ledger.get(pid);
      if (["handled_existing_reply", "complete", "suppressed"].includes(previous?.state)) continue;
      const comment = personComments.find(wantsAsset);
      if (!comment) continue;
      if (inspected >= inspectionLimit) break;
      inspected++;
      const degree = comment.author?.specifics?.network_distance ?? comment.author?.network_distance;
      const connected = ["FIRST_DEGREE", "DISTANCE_1"].includes(degree);
      const second = ["SECOND_DEGREE", "DISTANCE_2"].includes(degree);
      const name = comment.author.display_name ?? comment.author.name ?? "";
      const row = { provider_id: pid, name, first_name: name.trim().split(/\s+/)[0].replace(/^[^\p{L}\p{N}]+/u, "") || "there", profile_url: comment.author.profile_url ?? "", comment_id: previous?.comment_id ?? comment.id, comment_text: comment.text ?? "", connection_degree: degree ?? "unknown", last_checked_at: now, state: previous?.state ?? "new", enrollment_id: previous?.enrollment_id ?? "", reply_text: previous?.reply_text ?? "", note: previous?.note ?? "", delivery_receipt: previous?.delivery_receipt ?? null };
      const ownReplies = [];
      for (const c of personComments) {
        if (!c.reply_counter && c.id !== previous?.comment_id) continue;
        let replyCursor;
        for (let p = 0; p < 3; p++) {
          const response = await call("linkedin.posts_comments_list", { account_id: ACCOUNT, post_id: POST, comment_id: c.id, limit: 100, ...replyCursor ? { cursor: replyCursor } : {} }, `replies-${c.id}-${p}`);
          ownReplies.push(...list(response).filter(own));
          replyCursor = next(response);
          if (!replyCursor) break;
        }
        if (replyCursor) throw new Error("Reply scan truncated; refusing delivery without a complete duplicate check.");
      }
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
        if (!ownReplies.length) {
          plan.push({ name, action: "review_uncertain_public_reply" });
          continue;
        }
        row.state = "waiting_connection";
        await save(row, "connect-confirmed");
      }
      if (previous?.state === "sent_reply_pending") {
        plan.push({ name, action: "review_uncertain_public_reply" });
        continue;
      }
      const chat = chats.get(pid) ?? (row.delivery_receipt?.chat_id ? { id: row.delivery_receipt.chat_id } : void 0);
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
      if (!delivered && ["dm_send_pending", "dm_sent_unverified"].includes(row.state)) {
        plan.push({ name, action: "review_uncertain_dm" });
        continue;
      }
      // Only gate new outreach: a reply to the delivered DM auto-suppresses the lead,
      // and the public acknowledgement must still follow.
      if (!delivered && await suppressed(pid, row.profile_url)) {
        row.state = "suppressed";
        row.note = "Workspace do-not-contact match; no further outreach.";
        await save(row, "suppressed");
        plan.push({ name, action: "skip_suppressed" });
        continue;
      }
      if (connected && !delivered) {
        const history = (await enrollmentHistory()).filter((e) => e.leadProviderId === pid || row.profile_url && profileKey(e.leadProfileUrl) === profileKey(row.profile_url));
        if (row.state === "enrolled" || history.some((e) => e.sequenceId === SEQUENCE)) {
          plan.push({ name, action: "review_legacy_delivery" });
          continue;
        }
        if (history.some((e) => ["pending", "active", "waiting_connection", "waiting_signal"].includes(e.status) || e.senderAccountId && e.senderAccountId !== SENDER)) {
          plan.push({ name, action: "skip_other_campaign_or_sender" });
          continue;
        }
        if (dmAttempts >= MAX_DMS_PER_CYCLE || deliveryReplies >= deliveryReplyLimit) continue;
        const text2 = `Heyo ${row.first_name}:)

Here is the repo:

${ASSET}`;
        plan.push({ name, action: "send_resource_dm", comment_id: row.comment_id });
        dmAttempts++;
        if (audit) continue;
        await pace(`dm-${pid}`);
        row.state = "dm_send_pending";
        row.note = "DM intent saved; do not resend an uncertain provider outcome.";
        await save(row, "dm-intent");
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
      if (delivered ? deliveryReplies >= deliveryReplyLimit : connectionReplies >= connectionReplyLimit) {
        await save(row, "reply-deferred");
        plan.push({ name, action: "reply_next_hour" });
        continue;
      }
      const text = pick(delivered ? SENT_REPLIES : CONNECT_REPLIES, pid);
      plan.push({ name, action: delivered ? "confirm_delivery_publicly" : "request_connection_publicly", text, comment_id: row.comment_id });
      publicWrites++;
      if (delivered) deliveryReplies++;
      else connectionReplies++;
      if (audit) continue;
      await pace(`reply-${pid}`);
      row.state = delivered ? "sent_reply_pending" : "connect_reply_pending";
      row.reply_text = text;
      row.note = "Write intent saved before public action; uncertain effects require reconciliation.";
      await save(row, "reply-intent");
      const raw = await ctx.tools.run("linkedin.posts_comment_create", { account_id: ACCOUNT, post_id: POST, comment_id: row.comment_id, text }, { key: `reply-${pid}`, optional: true, connectionId: CONNECTION });
      if (raw?.ok === false) {
        const errorText = JSON.stringify(raw.error ?? {}).toLowerCase();
        if (/rate.limit|sender_spacing|working_hours|outside_working/.test(errorText) && !/unknown|uncertain/.test(errorText)) {
          row.state = delivered ? "delivered" : "new";
          row.note = "Pacing refused before send; retry next hourly cycle.";
          await save(row, "paced");
        }
        continue;
      }
      const result = unpack(raw);
      if (!result?.response || result.meta?.ok === false) throw new Error("Public reply unconfirmed; intent remains pending for reconciliation.");
      row.state = delivered ? "complete" : "waiting_connection";
      row.note = delivered ? "Resource delivery confirmed, then public reply sent." : "Connection requested publicly; deliver once first-degree.";
      await save(row, "reply-confirmed");
    }
    return { ok: true, audit, backfill, backfill_requests: requestBackfill, target_count: targets.size, post: POST, comments_seen: comments.length, unique_people: groups.size, inspected, resource_dms_sent: sent, dm_attempts: dmAttempts, public_reply_attempts: publicWrites, delivery_reply_attempts: deliveryReplies, connection_reply_attempts: connectionReplies, plan, max_new_dms_per_cycle: backfill ? 0 : MAX_DMS_PER_CYCLE, max_public_replies_per_cycle: backfill ? deliveryReplyLimit : connectionReplyLimit + deliveryReplyLimit, max_delivery_replies_per_cycle: deliveryReplyLimit, max_connection_replies_per_cycle: backfill ? 0 : connectionReplyLimit, max_inspected_per_cycle: inspectionLimit };
  }
});
export {
  flow_default as default,
  readCampaignHistory
};

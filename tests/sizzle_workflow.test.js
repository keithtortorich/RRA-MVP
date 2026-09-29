const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const html = fs.readFileSync(path.join(__dirname, "../docs/index.html"), "utf8");
const start = html.indexOf("function actionDescriptor(");
const end = html.indexOf("function focusTask(", start);
assert(start >= 0 && end > start, "the source next-action selector must exist");
const selectorSource = html.slice(start, end);

const checks = [
  ["EXT-001", "After-hours call handling", "PHONE", true, false],
  ["EXT-002", "24/7 promise delivery", "PHONE", true, false],
  ["EXT-003", "Callback response", "PHONE", true, true],
  ["EXT-004", "SMS response", "MESSAGE", true, true],
  ["EXT-005", "Web form function", "FORM", true, false],
  ["EXT-006", "Web lead response", "FORM", true, true],
  ["EXT-007", "Online booking function", "BOOKING", true, false],
  ["EXT-008", "Mobile click to call", "PHONE", true, false],
  ["EXT-009", "Public phone validity", "PHONE", true, false],
  ["EXT-010", "Emergency contact friction", "WEBSITE", false, false],
  ["EXT-011", "Conversion link integrity", "WEBSITE", true, false],
  ["EXT-012", "Hours consistency", "WEBSITE", false, false],
  ["EXT-013", "Service-area conversion path", "WEBSITE", false, false],
  ["EXT-014", "Form friction", "WEBSITE", false, false],
  ["EXT-015", "Submission confirmation", "FORM", false, true],
].map(([id, name, channelFamily, highValue, responseObservation]) => ({
  id, name, channelFamily, highValue, responseObservation,
}));

function selectorFor({ storageFailed = false, corrupted = false } = {}) {
  const sandbox = {
    INSPECT_IDS: ["EXT-010", "EXT-012", "EXT-013", "EXT-011"],
    CHECK_CATALOG: checks,
    storageFailed,
    corrupted,
    siteHref: value => /^https?:\/\//i.test(String(value || "")),
    phoneHref: value => String(value || "").replace(/\D/g, "").length >= 7 ? "tel:" + value : null,
    checkMeta: id => checks.find(check => check.id === id) || null,
    isDeterminateTest: record => ["VERIFIED_FAILURE", "VERIFIED_PASS"].includes(record.status) && !!record.observedResult,
    followupInfo: () => null,
    nextHandoffItem: () => null,
    truthSnapshot: () => ({ complete: false }),
    proposalBlockers: () => ["truth pending"],
    recordedPacket: prospect => !!(prospect && prospect.packet && prospect.packet.sentAt),
  };
  vm.runInNewContext(selectorSource, sandbox);
  return sandbox;
}

function prospect(overrides = {}) {
  return {
    id: "p1", company: "Example HVAC", state: "TARGET", outcome: null,
    website: "https://example.test", phone: "7135550100",
    verify: { business: { done: true }, website: { done: true }, phone: { done: true } },
    externalVerification: { tests: [] }, evidence: [],
    ...overrides,
  };
}

test("identity ambiguity is resolved before public-site preparation", () => {
  const selector = selectorFor();
  const action = selector.getNextAction(prospect({ verify: {} }));
  assert.equal(action.label, "Confirm business identity");
  assert.equal(action.phase, "research");
  assert.equal(action.targetId, "researchList");
});

test("website preparation is the primary action while phone work stays deferred", () => {
  const selector = selectorFor();
  const p = prospect();
  const next = selector.getNextAction(p);
  const deferred = selector.getNextAction(p, { deferred: true });
  assert.equal(next.label, "Inspect Emergency contact friction");
  assert.equal(next.phase, "verify");
  assert.match(deferred.label, /^Deferred — available later:/);
  assert.match(deferred.blockedReason, /after website preparation/);
});

test("an existing planned test is resumed by its ID instead of duplicated", () => {
  const selector = selectorFor();
  const p = prospect({ externalVerification: { tests: [{ id: "test-10", checkId: "EXT-010", status: "PLANNED" }] } });
  const before = JSON.stringify(p);
  const action = selector.getNextAction(p);
  assert.equal(action.existingTestId, "test-10");
  assert.equal(action.label, "Resume Emergency contact friction");
  assert.equal(JSON.stringify(p), before);
});

test("duplicate active records route to review and never suggest a new test", () => {
  const selector = selectorFor();
  const p = prospect({ externalVerification: { tests: [
    { id: "test-a", checkId: "EXT-010", status: "PLANNED" },
    { id: "test-b", checkId: "EXT-010", status: "IN_PROGRESS" },
  ] } });
  const action = selector.getNextAction(p);
  assert.match(action.label, /Review existing/);
  assert.equal(action.targetId, "tpTestList");
  assert.equal(action.existingTestId, null);
  assert.ok(action.blockedReason);
});

test("phone and response-window work remain visible in the deferred queue", () => {
  const selector = selectorFor();
  const p = prospect({ externalVerification: { tests: [
    { id: "test-1", checkId: "EXT-001", status: "VERIFIED_PASS", observedResult: "Answered" },
    { id: "test-2", checkId: "EXT-002", status: "VERIFIED_PASS", observedResult: "Answered" },
  ] } });
  const action = selector.getNextAction(p, { deferred: true });
  assert.match(action.label, /^Deferred — available later: Callback response/);
  assert.match(action.reason, /response window/);
  assert.equal(action.phase, "phone");
});

test("terminal outcomes never fall through to generic research instructions", () => {
  const selector = selectorFor();
  assert.equal(selector.getNextAction(prospect({ outcome: "LOST" })), null);
  assert.equal(selector.getNextAction(prospect({ outcome: "NURTURE", nurtureReengageDate: "2999-01-01" })), null);
  const won = selector.getNextAction(prospect({ outcome: "WON" }));
  assert.equal(won.label, "Review measurement");
  assert.equal(won.phase, "closed");
});

test("conversation status alone never derives the Sent stage", () => {
  const selector = selectorFor();
  const p = prospect({ state: "CONVERSATION" });
  assert.equal(selector.progressStage(p), 1);
  p.packet = { sentAt: "2026-09-29T00:00:00Z" };
  assert.equal(selector.progressStage(p), 4);
});

test("storage failure outranks prospect work", () => {
  const selector = selectorFor({ storageFailed: true });
  const action = selector.getNextAction(null);
  assert.equal(action.phase, "error");
  assert.equal(action.targetId, "retrySave");
});

import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";
import { readFile } from "node:fs/promises";
import { JSDOM } from "jsdom";

const html = await readFile(new URL("../docs/index.html", import.meta.url), "utf8");
let dom;
let api;

function prospect(overrides = {}) {
  return {
    id: "p-1", company: "ACME HVAC", city: "Dallas, TX", website: "https://example.com",
    contact: "Owner", phone: "555-0100", email: "", source: "test", notes: [], state: "WON",
    dateAdded: "2026-09-20T00:00:00.000Z", lastContact: "", sentDate: null, followupsSent: 0,
    outcome: "WON", calc: { mode: "missed" }, evidence: [{ id: "e-1", issue: "Missed calls", leakId: "HVAC-LEAK-001", quality: "KNOWN", observationQuality: "KNOWN", financialQuality: "ESTIMATED", impact: 3000, priority: 1 }],
    topLeakId: "e-1", handoff: { baseline: "10 missed calls", items: {} },
    wonDetails: { tier: "good", amount: 997, paymentStatus: "UNKNOWN", directDeliveryCost: 0, deliveryHours: 0, completedJobs: 0, documentedRecoveredRevenue: 0, revenueEvidence: "", revenueVerified: false, proofComplete: false, intervention: "", nextLeakReview: "" },
    ...overrides,
  };
}

function state(records = [prospect()]) {
  return { version: 4, prospects: records, archived: [], bench: [], processedIds: records.map(p => p.id), activities: [], generalNotes: [], settings: {}, campaign: { id: 1, targetTotal: 25 } };
}

beforeEach(() => {
  dom = new JSDOM(html, { runScripts: "dangerously", url: "https://sizzle.test/", pretendToBeVisual: true });
  dom.window.confirm = () => true;
  api = dom.window.__SIZZLE_TEST__;
});

test("boots with five seeded active prospects", () => assert.equal(api.getState().prospects.length, 5));
test("boots with nine bench records", () => assert.equal(api.getState().bench.length, 9));
test("bench inventory is excluded from processed count", () => assert.equal(api.campaignStats().processed, 5));
test("campaign target remains 25", () => assert.equal(api.campaignStats().targetTotal, 25));
test("default state includes archive and processed IDs", () => { const s=api.defaultState(); assert.equal(s.archived.length,0); assert.equal(s.processedIds.length,0); });
test("migration repairs malformed collection fields", () => { const s=api.migrateState({prospects:[],bench:null,archived:null,processedIds:null,activities:null,generalNotes:null}); assert.ok(Array.isArray(s.archived)&&Array.isArray(s.processedIds)); });
test("migration separates observation and financial certainty", () => { const p=prospect({evidence:[{id:"e",quality:"KNOWN",impact:10}],wonDetails:null,outcome:null}); const s=api.migrateState(state([p])); assert.equal(s.prospects[0].evidence[0].observationQuality,"KNOWN"); assert.equal(s.prospects[0].evidence[0].financialQuality,"ESTIMATED"); });
test("archive releases an active slot", () => { api.setState(state()); assert.equal(api.archiveProspect("p-1"),true); assert.equal(api.getState().prospects.length,0); });
test("archive retains the complete record", () => { api.setState(state()); api.archiveProspect("p-1"); const p=api.getState().archived[0]; assert.equal(p.evidence[0].issue,"Missed calls"); assert.equal(p.wonDetails.amount,997); });
test("restore returns an archived record to active", () => { api.setState(state()); api.archiveProspect("p-1"); api.restoreArchived("p-1"); assert.equal(api.getState().prospects[0].company,"ACME HVAC"); });
test("restore is blocked when five slots are occupied", () => { const active=Array.from({length:5},(_,i)=>prospect({id:`a-${i}`,company:`A${i}`})); const archived=prospect({id:"z"}); const s=state(active); s.archived=[archived]; s.processedIds.push("z"); api.setState(s); api.restoreArchived("z"); assert.equal(api.getState().archived.length,1); });
test("payment defaults to UNKNOWN", () => { const p=prospect({wonDetails:{tier:"good",amount:997}}); assert.equal(api.sprintRecord(p).paymentStatus,"UNKNOWN"); });
test("unpaid Sprint does not count as paid", () => { api.setState(state()); assert.equal(api.preSeedMetrics().paidSprints,0); });
test("explicitly paid $997 Sprint counts", () => { const p=prospect(); p.wonDetails.paymentStatus="PAID"; api.setState(state([p])); assert.equal(api.preSeedMetrics().paidSprints,1); });
test("CAC is unknown when spend is unavailable", () => { const p=prospect(); p.wonDetails.paymentStatus="PAID"; api.setState(state([p])); assert.equal(api.preSeedMetrics().cac,null); });
test("CAC uses actual spend divided by paid Sprints", () => { const a=prospect({id:"a"}),b=prospect({id:"b"}); a.wonDetails.paymentStatus="PAID"; b.wonDetails.paymentStatus="PAID"; const s=state([a,b]); s.settings.acquisitionSpend=400; api.setState(s); assert.equal(api.preSeedMetrics().cac,200); });
test("profit uses fixed $997 price minus direct cost", () => assert.equal(api.sprintProfit({amount:5000,directDeliveryCost:197}),800));
test("founder delivery hours do not change profit", () => assert.equal(api.sprintProfit({directDeliveryCost:100,deliveryHours:100}),897));
test("unverified revenue is excluded", () => assert.equal(api.qualifyingDocumentedRevenue({documentedRecoveredRevenue:5000,completedJobs:1,revenueEvidence:"invoice",revenueVerified:false}),0));
test("revenue requires a completed job", () => assert.equal(api.qualifyingDocumentedRevenue({documentedRecoveredRevenue:5000,completedJobs:0,revenueEvidence:"invoice",revenueVerified:true}),0));
test("revenue requires qualifying transaction evidence", () => assert.equal(api.qualifyingDocumentedRevenue({documentedRecoveredRevenue:5000,completedJobs:1,revenueEvidence:"",revenueVerified:true}),0));
test("verified qualifying revenue is counted", () => assert.equal(api.qualifyingDocumentedRevenue({documentedRecoveredRevenue:5000,completedJobs:1,revenueEvidence:"invoice 123",revenueVerified:true}),5000));
test("proof omits ROI for unverified revenue", () => { const p=prospect(); p.wonDetails.documentedRecoveredRevenue=5000; assert.ok(!api.buildProofRecord(p).includes("Customer ROI")); });
test("proof includes ROI only for verified qualifying revenue", () => { const p=prospect(); Object.assign(p.wonDetails,{documentedRecoveredRevenue:5000,completedJobs:1,revenueEvidence:"invoice 123",revenueVerified:true}); assert.ok(api.buildProofRecord(p).includes("Customer ROI")); });
test("unpaid WON prospect stays at SELL", () => assert.equal(api.prospectStage(prospect()),"SELL"));
test("paid prospect without baseline moves to BASELINE", () => { const p=prospect({handoff:{baseline:"",items:{}}}); p.wonDetails.paymentStatus="PAID"; assert.equal(api.prospectStage(p),"BASELINE"); });
test("UTC date addition remains stable across host timezones", () => assert.equal(api.addDays("2026-09-21",30).toISOString().slice(0,10),"2026-10-21"));

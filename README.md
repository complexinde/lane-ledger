# LaneLedger

LaneLedger is an AI-assisted, MIT-licensed prototype for exact minimum-lane interval partitioning. GenLayer fetches exact commit-pinned synthetic intervals, derives deterministic lanes with an independent maximum-overlap witness, and records an owner-confirmed certificate. It performs no real booking, attendance or external work.

## Current frontend and recorded live demonstration

The application is [https://complexinde.github.io/lane-ledger/](https://complexinde.github.io/lane-ledger/). The existing contract is `0xf074B35AeC1A0636DA0eA64D3e31BC3Fc2Ec2Bf0` on **GenLayer Studio, chain61999**. Current frontend revision**004** is a reviewed display/error/receipt-consistency update. Its local checks are **155 frontend tests**, **25 pinned contract SDK tests**, and TypeScript/Vite exit0. Its fresh [independent peer review](evidence/frontend-revision004/independent-review.json) is **PASS_WITHIN_REVIEWED_SCOPE**, with no outstanding Important/Critical findings in that stated scope. See [FRONTEND_REVISION_004.md](FRONTEND_REVISION_004.md), the [verification report](evidence/frontend-revision004/revision-verification.json) and [LIVE_STATUS.json](LIVE_STATUS.json) for exact source/build/peer hashes and snapshot boundaries.

The genuine Open -> Derive -> Owner confirm demonstration was performed with frontend revision**003**, commit `acecde60d5e2d2eeded280399e6029c3366f6f0f`. Record **LaneH1022A** reached **CONFIRMED, revision2**, certificate `fb160b80a008a5ce5e818fa8ab17109eb4fcde9836d9fbe7edf3f36a1d4a956d`. All three original business transactions were FINALIZED with NORMAL consensus, MAJORITY_AGREE and one successful leader. This existing result remains valid. No new wallet main workflow or duplicate business transaction is claimed for revision004; public asset verification and a read-only check of the existing record are recorded separately.

The exact result uses **two lanes**: lane0 **alpha, delta, epsilon**; lane1 **beta, gamma**. **Inspect earliest maximum overlap** shows tick1 with alpha and beta, providing the matching lower bound2. Intervals are half-open `[start,end)` and use abstract ticks.

| Demonstrated revision003 transition | Original transaction hash |
| --- | --- |
| open_program | `0xfe96a05bbf4f31d3c54ab68ff13f06204c5bd3cda3cdb74a6b23503ad4f94c47` |
| derive_program | `0x790d2e69dd2a2ebb0b8bba44eb622b07521ae2f3c49ece3bd3389381a5212cad` |
| confirm_program | `0xc26719e75cfc844ed3eeee5aa39f45ccd45c0decf5495caa63d0b0d22aa04da2` |

See [LIVE_WALKTHROUGH.md](LIVE_WALKTHROUGH.md) and [the immutable main-workflow evidence](evidence/live/main-workflow.json). Those original evidence files remain dated revision003 snapshots. Their earlier Portal submitted=false fields describe that earlier time and do not override the current submission snapshot below.

## Read the confirmed record

1. Open the public application. A read-only visit needs no wallet connection or signature.
2. Fill **Actual contract address** with `0xf074B35AeC1A0636DA0eA64D3e31BC3Fc2Ec2Bf0`, set **Unique record ID** to `LaneH1022A`, and click **Read record**.
3. Expand **Loaded source, result and certificate**; verify CONFIRMED/revision2 and the certificate above, then inspect the domain result and witness. Compare the original hashes against the immutable evidence. This walkthrough does not ask a reader to repeat a transaction.

## What revision004 changes

The public notice/trail uses a fixed UNVERIFIED diagnostic instead of echoing arbitrary provider/RPC errors. Changing record, address, account or chain clears the prior displayed public receipt; a plain read also clears it, and stale callbacks do not restore it into another context. Explicit SDK leader-receipt lists must contain exactly one successful leader: empty/validator-only lists fail closed. Independently bound raw finality/majority/leader proof remains mandatory, and missing SDK fields are not invented.

Contract source, fixtures, domain algorithms, dictionary ABI, pending storage schema, exact-hash recovery, official genlayer-js1.1.8 serializer/checksum boundary and the one-shot wallet mutation gate are unchanged. Unknown submissions retain their original context/hash and must never be automatically resent. There is no wallet-warning bypass.

One nonblocking presentation limitation remains: **A previous verified receipt for the same record may remain visible if a later action becomes UNVERIFIED/unknown. That receipt is historical evidence only and does not prove the new action succeeded. The pending original context/hash still blocks replay; record/address/account/chain changes and plain reads clear the displayed prior proof.** This is not a claim that all historical proof disappears or that an unresolved new action succeeded.

## Current scope and Portal snapshot

At snapshot **2026-10-21T19:04:48.625558+00:00**, the existing LaneLedger Project submission is **Pending review**, visible ID prefix **f694c1e2**, submitted=true and accepted=false. The observed submission timestamp is `2026-10-21T19:00:29.256Z`. This update did not submit again; Pending review is not acceptance, an award or guaranteed points.

The demonstrated use is synthetic and operated by one wallet user. Revoke is implemented and locally tested, but was not exercised live. No independent adoption, production use, real-world identity/scheduling, funding or award is claimed. The contract source remains SHA256 `48b3a5c678ff2633a10b012f60496653c36061225f93a017e8f5ae539630bca8`; the original constructor transaction remains `0x8a352fbb3fbcda63f64d39dfe9d8384646217a0a51dd0dd0400048d5e42a97f1` and is separate from the business hashes above. [deployment.json](deployment.json) keeps the actual published constructor schema and values.

[HISTORICAL_README_FRONTEND003.md](HISTORICAL_README_FRONTEND003.md) preserves the exact README from verified public commit `64d519ce6d71f21786807f55d8494802f9188450`. It is historical; the current status is the timestamped, scoped metadata above. The original public inputs and existing evidence files are unchanged by this frontend update.

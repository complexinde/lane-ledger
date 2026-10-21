# LaneLedger

LaneLedger is an AI-assisted, MIT-licensed prototype for exact minimum-lane interval partitioning. It combines commit-pinned public snapshots, deterministic lane reuse, an independent maximum-overlap witness and owner-confirmed GenLayer certificates. Inputs are synthetic abstract intervals; no real booking, identity, attendance or external work is performed.

## Current demonstrated state

The public application is [https://complexinde.github.io/lane-ledger/](https://complexinde.github.io/lane-ledger/). The existing Intelligent Contract is `0xf074B35AeC1A0636DA0eA64D3e31BC3Fc2Ec2Bf0` on **GenLayer Studio, chain61999**. The deployed source and revision003 frontend were verified. A recorded demonstration exercised **Open -> Derive -> Owner confirm** through the normal wallet workflow. The demonstrated record **LaneH1022A** reached **CONFIRMED, revision2**, with all three original business transactions **FINALIZED / NORMAL / MAJORITY_AGREE / unique leader SUCCESS**.

The certificate is `fb160b80a008a5ce5e818fa8ab17109eb4fcde9836d9fbe7edf3f36a1d4a956d`. The result uses **two lanes**: lane0 **alpha, delta, epsilon** and lane1 **beta, gamma**. At the earliest maximum-overlap tick **1**, **alpha and beta** are simultaneously active, proving a lower bound of two lanes. This matches the canonical assignment, so the demonstrated result is minimal.

| Transition | Original transaction hash |
| --- | --- |
| Open | `0xfe96a05bbf4f31d3c54ab68ff13f06204c5bd3cda3cdb74a6b23503ad4f94c47` |
| Derive | `0x790d2e69dd2a2ebb0b8bba44eb622b07521ae2f3c49ece3bd3389381a5212cad` |
| Owner confirm | `0xc26719e75cfc844ed3eeee5aa39f45ccd45c0decf5495caa63d0b0d22aa04da2` |

See [LIVE_WALKTHROUGH.md](LIVE_WALKTHROUGH.md) for the three-step read-only demonstration, [LIVE_STATUS.json](LIVE_STATUS.json) for the timestamped scope, [evidence/live/main-workflow.json](evidence/live/main-workflow.json) for the workflow summary and the linked individual transaction proofs. These records contain selected public proof fields, not full node configuration or VM output.

## Read the demonstrated record

1. Open the public application. No wallet is required to read this record.
2. Set **Actual contract address** to `0xf074B35AeC1A0636DA0eA64D3e31BC3Fc2Ec2Bf0`, **Unique record ID** to `LaneH1022A`, and click **Read record**.
3. Expand **Loaded source, result and certificate**, verify CONFIRMED/revision2 and the certificate above, then click **Inspect earliest maximum overlap** to inspect tick1. The two-lane assignment and lower-bound witness should agree.

## Source and deterministic rule

The original public fixture is [https://raw.githubusercontent.com/complexinde/lane-ledger/b86c0378d66885642ed4348c5f42fa25a640817a/profile07/projects/lane-ledger/fixtures/program.json](https://raw.githubusercontent.com/complexinde/lane-ledger/b86c0378d66885642ed4348c5f42fa25a640817a/profile07/projects/lane-ledger/fixtures/program.json) (373 exact bytes, SHA256 `188a307035475165d46506d1e40979d73201d672c69ca79f865125d7b82479d8`). It declares five events with integer abstract ticks. Intervals use `[start,end)`: ending releases a lane before a new interval starts. Events are processed deterministically, the lowest available lane is reused, and an independent overlap sweep produces the earliest maximum-overlap witness. Complete fresh source/result captures are compared by validators; owner confirmation binds the current derived certificate and revision.

The deployed contract source SHA256 remains `48b3a5c678ff2633a10b012f60496653c36061225f93a017e8f5ae539630bca8`. The original constructor transaction is `0x8a352fbb3fbcda63f64d39dfe9d8384646217a0a51dd0dd0400048d5e42a97f1`. It is separate from the three business transactions above. [deployment.json](deployment.json) retains the constructor identity fields and records the later business workflow separately.

The current frontend uses reviewed revision003, official **genlayer-js1.1.8**, checksum RPC addresses, account/chain context checks, strict original-hash receipt proof and a one-shot wallet submission gate. Its published frontend commit before this documentation batch is `acecde60d5e2d2eeded280399e6029c3366f6f0f`. Contract source, fixtures, business algorithms and compiled assets are unchanged by this documentation update.

## Scope and status

This is a **single-operator synthetic prototype demonstration**. Open, Derive and Owner confirm were exercised live. Revoke is implemented and locally tested but was not exercised live; no independent users, production scheduling, adoption, funding or awards are claimed. Portal Project submission was **false at 2026-10-21T18:42:16.819132+00:00**. Portal status is a timestamped snapshot; later submission is recorded separately.

Unknown wallet outcomes must retain their original transaction hash and context and must never be automatically resent. This documentation does not authorize bypassing wallet warnings. [HISTORICAL_README_PRE_LIVE.md](HISTORICAL_README_PRE_LIVE.md) preserves the exact README from the prior published frontend commit as historical evidence; its earlier deployment/live-status descriptions are superseded by the timestamped facts above.

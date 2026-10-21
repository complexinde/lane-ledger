# LaneLedger live read-only walkthrough

AI-assisted synthetic prototype. A recorded demonstration exercised the normal frontend wallet workflow on GenLayer Studio61999. All three business transactions finalized with NORMAL consensus, MAJORITY_AGREE and exactly one successful leader. One operator performed Open -> Derive -> Owner confirm. Revoke and independent adoption were not exercised or claimed.

1. Open [https://complexinde.github.io/lane-ledger/](https://complexinde.github.io/lane-ledger/). Reading the demonstrated record does not require connecting a wallet or signing.
2. Enter `0xf074B35AeC1A0636DA0eA64D3e31BC3Fc2Ec2Bf0` in **Actual contract address**, enter `LaneH1022A` in **Unique record ID**, then click **Read record**. Expect **CONFIRMED**, revision **2**. Expand **Loaded source, result and certificate**.
3. Verify two lanes: lane0 **alpha, delta, epsilon**; lane1 **beta, gamma**. Click **Inspect earliest maximum overlap**. Tick **1** has **alpha, beta**, providing the matching lower bound2. Compare the certificate and original hashes below with [the public workflow evidence](evidence/live/main-workflow.json).

Certificate: `fb160b80a008a5ce5e818fa8ab17109eb4fcde9836d9fbe7edf3f36a1d4a956d`.

| Transition | Original transaction hash | Evidence |
| --- | --- | --- |
| Open | `0xfe96a05bbf4f31d3c54ab68ff13f06204c5bd3cda3cdb74a6b23503ad4f94c47` | [open.json](evidence/live/open.json) |
| Derive | `0x790d2e69dd2a2ebb0b8bba44eb622b07521ae2f3c49ece3bd3389381a5212cad` | [derive.json](evidence/live/derive.json) |
| Owner confirm | `0xc26719e75cfc844ed3eeee5aa39f45ccd45c0decf5495caa63d0b0d22aa04da2` | [confirm.json](evidence/live/confirm.json) |

The exact fixture is [https://raw.githubusercontent.com/complexinde/lane-ledger/b86c0378d66885642ed4348c5f42fa25a640817a/profile07/projects/lane-ledger/fixtures/program.json](https://raw.githubusercontent.com/complexinde/lane-ledger/b86c0378d66885642ed4348c5f42fa25a640817a/profile07/projects/lane-ledger/fixtures/program.json), 373 bytes, SHA256 `188a307035475165d46506d1e40979d73201d672c69ca79f865125d7b82479d8`. Intervals are half-open `[start,end)` and use abstract ticks. Ending releases a lane before another event starts. There is no real booking, attendance, asset allocation or job execution.

This walkthrough observes the existing confirmed record. It does not ask a reader to submit or replay any transaction. An unresolved wallet outcome must retain the original hash and context. Portal submission was false at snapshot `2026-10-21T18:42:16.819132+00:00`; Portal status is a timestamped snapshot; later submission is recorded separately.

# RP-008 Plant Walkthrough Overlays — Index

**Program:** RP-008 Smart Factory  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**Model:** [SMART_FACTORY_SPECIALIZATION_MODEL.md](../SMART_FACTORY_SPECIALIZATION_MODEL.md)  
**Status:** PW-01…02 Synthetic Complete  
**Last Updated:** 2026-07-21

| ID | Path | Focus | Critical gaps |
|----|------|-------|---------------|
| PW-01 | [PW-01-discrete-cell.md](PW-01-discrete-cell.md) | Discrete cell Cap/safety/robot | SF-03/06 before REC-ROBOT |
| PW-02 | [PW-02-line-terminal-ot.md](PW-02-line-terminal-ot.md) | Line-side Terminal + OT island | SF-04/05/07; no open MES write |

All overlays assert `mes_kernelization: never` and `machine_control_from_brain: never`.

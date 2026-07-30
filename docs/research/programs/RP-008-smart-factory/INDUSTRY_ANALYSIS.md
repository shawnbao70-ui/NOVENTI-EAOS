# INDUSTRY-ANALYSIS-RP-008 — Smart Factory

**Research ID:** NRI-RP-008-IND  
**Program:** RP-008 Smart Factory  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Synthesize industry patterns that justify plant overlays without MES Kernel fork or machine-control Brain  
**Scope:** In: safety-before-smart, line UX, OT islands, robot HOLD / Out: MES product design; Const/BP/Kernel edits  
**Author:** NRI  
**Reviewer:** 臻宇（Pass — WP Draft Allowed）  
**Approval:** Pending  
**Dependencies:** [SFSM](SMART_FACTORY_SPECIALIZATION_MODEL.md); PW-01…02; EEM; AIRM ID-07  
**Related Capability:** Industry / Smart Factory  
**Related Blueprint:** Package/Terminal/Event *(candidates)*  
**Related Constitution:** Industry/safety books *(candidates)*  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Thesis

“Smart factory” programs often skip safety cases, force HQ UX on the line, and push robotization without EEM HOLD. SFSM specializes Cap/EEM/AIRM as **overlays** — never MES-in-Kernel, never Brain machine Act.

## 2. Cross-Industry Patterns

| ID | Pattern | Symptom | SFSM Stress | Seen in |
|----|---------|---------|-------------|---------|
| P-SF-01 | Smart without safety | Pilot robot, no SF-03 case | C-SF-02 | PW-01 |
| P-SF-02 | MES kernelization urge | Put scheduling in Core Kernel | C-SF-03 | Industry rhetoric |
| P-SF-03 | Brain machine Act | OEE card drives motion | C-SF-04 | PW-01 |
| P-SF-04 | HQ UX on line | Dense forms; no glance | C-SF-06 | PW-02 |
| P-SF-05 | Historian-as-Knowledge | Raw tags = truth | SF-05 | PW-01/02 |
| P-SF-06 | Robot without PR band | REC-ROBOT skips HOLD | C-SF-05 | PW-01 |
| P-SF-07 | Fail-open offline | Approve when OT down | SF-07 | PW-02 |
| P-SF-08 | Open MES write | Edge agent mutates freely | AIRM ID-07 | PW-02 / GP-02 |
| P-SF-09 | Unsigned plant packs | No OT scope declaration | SF-08 | PW-01 |
| P-SF-10 | Eng urgency | Research → MES schema tickets | Dual-Track | Soft-queue ban |

## 3. Sector Notes

### Discrete cell (PW-01)
Safety case + robot readiness before leaving HOLD; Cap overlay reusable from CFM.

### Line-side + OT (PW-02)
Terminal glanceability and degraded mode before “AI ready”; OT island read-only default.

## 4. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Brain execute / Twin authorize / Role→grant / payment clearing.

## Related Documents

- [SFSM](SMART_FACTORY_SPECIALIZATION_MODEL.md)  
- [walkthroughs/](walkthroughs/)  
- [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  

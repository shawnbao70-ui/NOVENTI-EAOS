# RP-004 Tax / FX / Approval Field Card

**Program:** Organization Neutrality  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) · [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD whether **税票 · FX · 审批** boundaries remain **organization-neutral**—entity/legal/tax identity, multi-currency, and approval principal must not collapse into org-chart shortcuts or site-local aliases. Map **税票主账缺席**, **AR/打印分离**, **FX 不传播 / 无重估**, **Approval Center vs V18**, and **GET 审批** without rewriting org models. Knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`.

## Tax / FX / approval observation points (RP-004 lens)

1. **Legal/tax entity ≠ org unit:** printing or Post AR under a department/site label without a tax-invoice master or filing entity.
2. **AR/print org bleed:** shared “Invoice” screens that imply one org’s AR is another’s tax document.
3. **FX and functional currency ownership:** which org/legal entity owns rate source vs which unit merely displays Quote FX.
4. **Cross-org FX non-propagation:** Convert across org contexts that drop currency/rate without explicit intercompany FX policy.
5. **Approver principal ≠ org title:** V18 Human Confirm or Approval Center decision attributed to role/title rather than named principal + scope.
6. **GET approve across org aliases:** confirm links that mutate under residual org IDs or shared mailboxes.
7. **Org≠Capability for tax/FX:** org structure changes must not be scored as tax-invoice or revaluation capability delivery.
8. **Brain/Twin / org fence:** HOLD AI or Twin suggestions that reassign tax/FX/approval authority by org chart alone.

## Scoring / HOLD

- Score org-neutrality of tax identity, FX ownership, and approval principal; separate display org from legal/tax authority.
- Dossier cross-org contradictions; do not “fix” neutrality by collapsing entities.
- HOLD when org-chart proximity is treated as tax filing, FX revalue, or approval evidence.

## Required live evidence

1. Authorized org/legal/tax-entity map tied to AR, print, and any tax-invoice surface (or attested tax-master absence) with `as_of`.
2. Redacted multi-org or multi-site extracts showing AR≠print≠tax and FX fields present/absent per entity.
3. Approver principal identity evidence (named actor + scope) for V18 vs Approval Center, not title-only.
4. GET vs POST confirm/approve inventory with org-alias / residual-route notes.
5. Custodian corroboration that org redesign did not invent tax-invoice or revaluation authority.
6. Custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-004 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, org model rewrite, Identity, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, tax/FX posting, approve/convert, or org-impersonation.
4. No synthetic org walkthrough relabeled as live tax/FX/approval evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no org change, tax, FX, or approval action.

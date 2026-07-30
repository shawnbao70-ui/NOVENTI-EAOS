"""Boundary port for creating a Finance AR credit note from CRM."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from kernel.shared.context import ExecutionContext
from kernel.shared.results import KernelResult
from noventi.crm.models import ReturnAuthorizationStatus
from noventi.crm.repository import CRMRepository
from noventi.finance.service import RmaCreditNoteLink


class CreditNoteCreatePort(Protocol):
    def create_credit_note(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
    ) -> KernelResult[UUID]: ...


class CRMReturnAuthorizationCreditNoteLinkAdapter:
    """Finance-owned issue rule adapter backed by the tenant-scoped CRM repo."""

    def __init__(self, repository: CRMRepository) -> None:
        self._repository = repository

    def get_return_authorization_by_credit_note_id(
        self, credit_note_id: UUID
    ) -> RmaCreditNoteLink | None:
        authorization = self._repository.get_return_authorization_by_credit_note_id(
            credit_note_id
        )
        if authorization is None:
            return None
        return RmaCreditNoteLink(
            return_authorization_id=authorization.id,
            invoice_id=authorization.invoice_id,
            restocked=authorization.status == ReturnAuthorizationStatus.RESTOCKED,
            version=authorization.version,
        )

    def mark_credit_note_issued(
        self,
        *,
        return_authorization_id: UUID,
        expected_version: int,
        issued_at: datetime,
    ) -> None:
        authorization = self._repository.get_return_authorization(
            return_authorization_id
        )
        if authorization is None:
            raise ValueError("linked return authorization not found")
        self._repository.save_return_authorization(
            replace(
                authorization,
                credit_note_issued_at=issued_at,
                version=authorization.version + 1,
            ),
            expected_version=expected_version,
        )

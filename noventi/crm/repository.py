"""Tenant-bound repository contract for the CRM C1 slice."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from noventi.crm.models import (
    ARInvoice,
    Contact,
    Customer,
    DeliveryOrder,
    DeliveryOrderLine,
    Opportunity,
    Quote,
    QuoteConversion,
    QuoteLine,
    Requirement,
    ReturnAuthorization,
    SalesOrder,
    SalesOrderLine,
    TenantConfirmPolicy,
)


class CRMRepository(Protocol):
    def add_customer(self, customer: Customer) -> None: ...

    def get_customer(self, customer_id: UUID) -> Customer | None: ...

    def list_customers(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Customer]: ...

    def save_customer(self, customer: Customer, *, expected_version: int) -> None: ...

    def add_contact(self, contact: Contact) -> None: ...

    def get_contact(self, customer_id: UUID, contact_id: UUID) -> Contact | None: ...

    def list_contacts(
        self,
        customer_id: UUID,
        *,
        limit: int,
        after: tuple[datetime, UUID] | None = None,
    ) -> list[Contact]: ...

    def save_contact(self, contact: Contact, *, expected_version: int) -> None: ...

    def add_opportunity(self, opportunity: Opportunity) -> None: ...

    def get_opportunity(self, opportunity_id: UUID) -> Opportunity | None: ...

    def list_opportunities(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Opportunity]: ...

    def save_opportunity(
        self, opportunity: Opportunity, *, expected_version: int
    ) -> None: ...

    def add_requirement(self, requirement: Requirement) -> None: ...

    def get_requirement(self, requirement_id: UUID) -> Requirement | None: ...

    def list_requirements(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Requirement]: ...

    def save_requirement(
        self, requirement: Requirement, *, expected_version: int
    ) -> None: ...

    def add_quote(self, quote: Quote) -> None: ...

    def get_quote(self, quote_id: UUID) -> Quote | None: ...

    def list_quotes(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Quote]: ...

    def save_quote(self, quote: Quote, *, expected_version: int) -> None: ...

    def add_conversion(self, conversion: QuoteConversion) -> None: ...

    def get_conversion(self, conversion_id: UUID) -> QuoteConversion | None: ...

    def get_conversion_by_quote(self, quote_id: UUID) -> QuoteConversion | None: ...

    def save_conversion(
        self, conversion: QuoteConversion, *, expected_version: int
    ) -> None: ...

    def add_sales_order(self, sales_order: SalesOrder) -> None: ...

    def get_sales_order(self, sales_order_id: UUID) -> SalesOrder | None: ...

    def list_sales_orders(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[SalesOrder]: ...

    def get_sales_order_by_conversion(
        self, conversion_id: UUID
    ) -> SalesOrder | None: ...

    def save_sales_order(
        self, sales_order: SalesOrder, *, expected_version: int
    ) -> None: ...

    def add_sales_order_lines(
        self, sales_order_lines: list[SalesOrderLine]
    ) -> None: ...

    def list_sales_order_lines(
        self, sales_order_id: UUID
    ) -> list[SalesOrderLine]: ...

    def add_delivery_order(self, delivery_order: DeliveryOrder) -> None: ...

    def add_delivery_order_lines(
        self, delivery_order_lines: list[DeliveryOrderLine]
    ) -> None: ...

    def list_delivery_order_lines(
        self, delivery_order_id: UUID
    ) -> list[DeliveryOrderLine]: ...

    def save_delivery_order_lines(
        self,
        delivery_order_lines: list[DeliveryOrderLine],
    ) -> None: ...

    def save_delivery_order(
        self, delivery_order: DeliveryOrder, *, expected_version: int
    ) -> None: ...

    def get_delivery_order(
        self, delivery_order_id: UUID
    ) -> DeliveryOrder | None: ...

    def get_delivery_order_by_sales_order(
        self, sales_order_id: UUID
    ) -> DeliveryOrder | None: ...

    def get_delivery_order_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> DeliveryOrder | None: ...

    def list_delivery_orders_by_sales_order(
        self, sales_order_id: UUID
    ) -> list[DeliveryOrder]: ...

    def add_ar_invoice(self, invoice: ARInvoice) -> None: ...

    def save_ar_invoice(
        self, invoice: ARInvoice, *, expected_version: int
    ) -> None: ...

    def get_ar_invoice(self, invoice_id: UUID) -> ARInvoice | None: ...

    def get_ar_invoice_by_delivery_order(
        self, delivery_order_id: UUID
    ) -> ARInvoice | None: ...

    def add_return_authorization(
        self, authorization: ReturnAuthorization
    ) -> None: ...

    def get_return_authorization(
        self, return_authorization_id: UUID
    ) -> ReturnAuthorization | None: ...

    def get_return_authorization_by_credit_note_id(
        self, credit_note_id: UUID
    ) -> ReturnAuthorization | None: ...

    def get_return_authorization_by_delivery_order(
        self, delivery_order_id: UUID
    ) -> ReturnAuthorization | None: ...

    def get_return_authorization_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ReturnAuthorization | None: ...

    def save_return_authorization(
        self, authorization: ReturnAuthorization, *, expected_version: int
    ) -> None: ...

    def get_confirm_policy(self) -> TenantConfirmPolicy | None: ...

    def save_confirm_policy(
        self, policy: TenantConfirmPolicy, *, expected_version: int
    ) -> None: ...

    def next_quote_line_number(self, quote_id: UUID) -> int: ...

    def add_quote_line(self, quote_line: QuoteLine) -> None: ...

    def get_quote_line(
        self, quote_id: UUID, quote_line_id: UUID
    ) -> QuoteLine | None: ...

    def list_quote_lines(self, quote_id: UUID) -> list[QuoteLine]: ...

    def save_quote_line(
        self, quote_line: QuoteLine, *, expected_version: int
    ) -> None: ...


class InMemoryCRMRepository:
    """Hermetic tenant-bound adapter used by package contract tests."""

    def __init__(self, *, tenant_id: UUID) -> None:
        self._tenant_id = tenant_id
        self._customers: dict[UUID, Customer] = {}
        self._contacts: dict[UUID, Contact] = {}
        self._opportunities: dict[UUID, Opportunity] = {}
        self._requirements: dict[UUID, Requirement] = {}
        self._quotes: dict[UUID, Quote] = {}
        self._conversions: dict[UUID, QuoteConversion] = {}
        self._sales_orders: dict[UUID, SalesOrder] = {}
        self._quote_lines: dict[UUID, QuoteLine] = {}
        self._sales_order_lines: dict[UUID, SalesOrderLine] = {}
        self._delivery_orders: dict[UUID, DeliveryOrder] = {}
        self._delivery_order_lines: dict[UUID, DeliveryOrderLine] = {}
        self._ar_invoices: dict[UUID, ARInvoice] = {}
        self._return_authorizations: dict[UUID, ReturnAuthorization] = {}
        self._confirm_policy: TenantConfirmPolicy | None = None

    def add_customer(self, customer: Customer) -> None:
        if customer.tenant_id != self._tenant_id:
            raise ValueError("customer is outside repository tenant")
        if any(
            item.code.casefold() == customer.code.casefold()
            for item in self._customers.values()
        ):
            raise ValueError("customer code already exists")
        self._customers[customer.id] = customer

    def get_customer(self, customer_id: UUID) -> Customer | None:
        customer = self._customers.get(customer_id)
        if customer is None or customer.tenant_id != self._tenant_id:
            return None
        return customer

    def list_customers(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Customer]:
        customers = [
            customer
            for customer in self._customers.values()
            if customer.tenant_id == self._tenant_id
            and customer.status.value == "active"
            and (
                after is None
                or (customer.updated_at, customer.id.int) < (after[0], after[1].int)
            )
        ]
        customers.sort(key=lambda item: (item.updated_at, item.id.int), reverse=True)
        return customers[:limit]

    def save_customer(self, customer: Customer, *, expected_version: int) -> None:
        current = self.get_customer(customer.id)
        if current is None or current.version != expected_version:
            raise ValueError("customer version conflict")
        self._customers[customer.id] = customer

    def add_contact(self, contact: Contact) -> None:
        if contact.tenant_id != self._tenant_id:
            raise ValueError("contact is outside repository tenant")
        self._contacts[contact.id] = contact

    def get_contact(self, customer_id: UUID, contact_id: UUID) -> Contact | None:
        contact = self._contacts.get(contact_id)
        if (
            contact is None
            or contact.tenant_id != self._tenant_id
            or contact.customer_id != customer_id
        ):
            return None
        return contact

    def list_contacts(
        self,
        customer_id: UUID,
        *,
        limit: int,
        after: tuple[datetime, UUID] | None = None,
    ) -> list[Contact]:
        contacts = [
            contact
            for contact in self._contacts.values()
            if contact.tenant_id == self._tenant_id
            and contact.customer_id == customer_id
            and contact.status.value == "active"
            and (
                after is None
                or (contact.updated_at, contact.id.int) < (after[0], after[1].int)
            )
        ]
        contacts.sort(key=lambda item: (item.updated_at, item.id.int), reverse=True)
        return contacts[:limit]

    def save_contact(self, contact: Contact, *, expected_version: int) -> None:
        current = self.get_contact(contact.customer_id, contact.id)
        if current is None or current.version != expected_version:
            raise ValueError("contact version conflict")
        self._contacts[contact.id] = contact

    def add_opportunity(self, opportunity: Opportunity) -> None:
        if opportunity.tenant_id != self._tenant_id:
            raise ValueError("opportunity is outside repository tenant")
        if any(
            item.code == opportunity.code for item in self._opportunities.values()
        ):
            raise ValueError("opportunity code already exists")
        self._opportunities[opportunity.id] = opportunity

    def get_opportunity(self, opportunity_id: UUID) -> Opportunity | None:
        opportunity = self._opportunities.get(opportunity_id)
        if opportunity is None or opportunity.tenant_id != self._tenant_id:
            return None
        return opportunity

    def list_opportunities(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Opportunity]:
        opportunities = [
            opportunity
            for opportunity in self._opportunities.values()
            if opportunity.tenant_id == self._tenant_id
            and opportunity.status.value == "active"
            and (
                after is None
                or (opportunity.updated_at, opportunity.id.int)
                < (after[0], after[1].int)
            )
        ]
        opportunities.sort(
            key=lambda item: (item.updated_at, item.id.int), reverse=True
        )
        return opportunities[:limit]

    def save_opportunity(
        self, opportunity: Opportunity, *, expected_version: int
    ) -> None:
        current = self.get_opportunity(opportunity.id)
        if current is None or current.version != expected_version:
            raise ValueError("opportunity version conflict")
        self._opportunities[opportunity.id] = opportunity

    def add_requirement(self, requirement: Requirement) -> None:
        if requirement.tenant_id != self._tenant_id:
            raise ValueError("requirement is outside repository tenant")
        if any(item.code == requirement.code for item in self._requirements.values()):
            raise ValueError("requirement code already exists")
        self._requirements[requirement.id] = requirement

    def get_requirement(self, requirement_id: UUID) -> Requirement | None:
        requirement = self._requirements.get(requirement_id)
        if requirement is None or requirement.tenant_id != self._tenant_id:
            return None
        return requirement

    def list_requirements(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Requirement]:
        requirements = [
            requirement
            for requirement in self._requirements.values()
            if requirement.tenant_id == self._tenant_id
            and requirement.status.value == "active"
            and (
                after is None
                or (requirement.updated_at, requirement.id.int)
                < (after[0], after[1].int)
            )
        ]
        requirements.sort(
            key=lambda item: (item.updated_at, item.id.int), reverse=True
        )
        return requirements[:limit]

    def save_requirement(
        self, requirement: Requirement, *, expected_version: int
    ) -> None:
        current = self.get_requirement(requirement.id)
        if current is None or current.version != expected_version:
            raise ValueError("requirement version conflict")
        self._requirements[requirement.id] = requirement

    def add_quote(self, quote: Quote) -> None:
        if quote.tenant_id != self._tenant_id:
            raise ValueError("quote is outside repository tenant")
        if any(item.code == quote.code for item in self._quotes.values()):
            raise ValueError("quote code already exists")
        self._quotes[quote.id] = quote

    def get_quote(self, quote_id: UUID) -> Quote | None:
        quote = self._quotes.get(quote_id)
        if quote is None or quote.tenant_id != self._tenant_id:
            return None
        return quote

    def list_quotes(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Quote]:
        quotes = [
            quote
            for quote in self._quotes.values()
            if quote.tenant_id == self._tenant_id
            and quote.status.value != "archived"
            and (
                after is None
                or (quote.updated_at, quote.id.int) < (after[0], after[1].int)
            )
        ]
        quotes.sort(key=lambda item: (item.updated_at, item.id.int), reverse=True)
        return quotes[:limit]

    def save_quote(self, quote: Quote, *, expected_version: int) -> None:
        current = self.get_quote(quote.id)
        if current is None or current.version != expected_version:
            raise ValueError("quote version conflict")
        self._quotes[quote.id] = quote

    def add_conversion(self, conversion: QuoteConversion) -> None:
        if conversion.tenant_id != self._tenant_id:
            raise ValueError("conversion is outside repository tenant")
        if self.get_conversion_by_quote(conversion.quote_id) is not None:
            raise ValueError("quote conversion already exists")
        self._conversions[conversion.id] = conversion

    def get_conversion(self, conversion_id: UUID) -> QuoteConversion | None:
        conversion = self._conversions.get(conversion_id)
        if conversion is None or conversion.tenant_id != self._tenant_id:
            return None
        return conversion

    def get_conversion_by_quote(self, quote_id: UUID) -> QuoteConversion | None:
        return next(
            (
                item
                for item in self._conversions.values()
                if item.tenant_id == self._tenant_id and item.quote_id == quote_id
            ),
            None,
        )

    def save_conversion(
        self, conversion: QuoteConversion, *, expected_version: int
    ) -> None:
        current = self.get_conversion(conversion.id)
        if current is None or current.version != expected_version:
            raise ValueError("conversion version conflict")
        self._conversions[conversion.id] = conversion

    def add_sales_order(self, sales_order: SalesOrder) -> None:
        if sales_order.tenant_id != self._tenant_id:
            raise ValueError("sales order is outside repository tenant")
        if self.get_sales_order_by_conversion(sales_order.conversion_id) is not None:
            raise ValueError("sales order already exists")
        self._sales_orders[sales_order.id] = sales_order

    def get_sales_order(self, sales_order_id: UUID) -> SalesOrder | None:
        sales_order = self._sales_orders.get(sales_order_id)
        if sales_order is None or sales_order.tenant_id != self._tenant_id:
            return None
        return sales_order

    def list_sales_orders(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[SalesOrder]:
        orders = [
            order
            for order in self._sales_orders.values()
            if order.tenant_id == self._tenant_id
            and (
                after is None
                or (order.created_at, order.id.int) < (after[0], after[1].int)
            )
        ]
        orders.sort(key=lambda item: (item.created_at, item.id.int), reverse=True)
        return orders[:limit]

    def get_sales_order_by_conversion(
        self, conversion_id: UUID
    ) -> SalesOrder | None:
        return next(
            (
                item
                for item in self._sales_orders.values()
                if item.tenant_id == self._tenant_id
                and item.conversion_id == conversion_id
            ),
            None,
        )

    def save_sales_order(
        self, sales_order: SalesOrder, *, expected_version: int
    ) -> None:
        current = self.get_sales_order(sales_order.id)
        if current is None or current.version != expected_version:
            raise ValueError("sales order version conflict")
        self._sales_orders[sales_order.id] = sales_order

    def add_sales_order_lines(
        self, sales_order_lines: list[SalesOrderLine]
    ) -> None:
        for sales_order_line in sales_order_lines:
            if sales_order_line.tenant_id != self._tenant_id:
                raise ValueError("sales order line is outside repository tenant")
            if any(
                item.sales_order_id == sales_order_line.sales_order_id
                and item.line_number == sales_order_line.line_number
                for item in self._sales_order_lines.values()
            ):
                raise ValueError("sales order line number already exists")
            self._sales_order_lines[sales_order_line.id] = sales_order_line

    def list_sales_order_lines(
        self, sales_order_id: UUID
    ) -> list[SalesOrderLine]:
        return sorted(
            (
                item
                for item in self._sales_order_lines.values()
                if item.tenant_id == self._tenant_id
                and item.sales_order_id == sales_order_id
            ),
            key=lambda item: item.line_number,
        )

    def add_delivery_order(self, delivery_order: DeliveryOrder) -> None:
        if delivery_order.tenant_id != self._tenant_id:
            raise ValueError("delivery order is outside repository tenant")
        self._delivery_orders[delivery_order.id] = delivery_order

    def add_delivery_order_lines(
        self, delivery_order_lines: list[DeliveryOrderLine]
    ) -> None:
        for line in delivery_order_lines:
            if line.tenant_id != self._tenant_id:
                raise ValueError("delivery order line is outside repository tenant")
            self._delivery_order_lines[line.id] = line

    def list_delivery_order_lines(
        self, delivery_order_id: UUID
    ) -> list[DeliveryOrderLine]:
        return sorted(
            (
                line
                for line in self._delivery_order_lines.values()
                if line.tenant_id == self._tenant_id
                and line.delivery_order_id == delivery_order_id
            ),
            key=lambda line: line.sales_order_line_id.hex,
        )

    def save_delivery_order_lines(
        self, delivery_order_lines: list[DeliveryOrderLine]
    ) -> None:
        for line in delivery_order_lines:
            if line.id not in self._delivery_order_lines:
                raise ValueError("delivery order line not found")
            self._delivery_order_lines[line.id] = line

    def save_delivery_order(
        self, delivery_order: DeliveryOrder, *, expected_version: int
    ) -> None:
        current = self.get_delivery_order(delivery_order.id)
        if current is None or current.version != expected_version:
            raise ValueError("delivery order version conflict")
        self._delivery_orders[delivery_order.id] = delivery_order

    def get_delivery_order(
        self, delivery_order_id: UUID
    ) -> DeliveryOrder | None:
        delivery_order = self._delivery_orders.get(delivery_order_id)
        if (
            delivery_order is None
            or delivery_order.tenant_id != self._tenant_id
        ):
            return None
        return delivery_order

    def get_delivery_order_by_sales_order(
        self, sales_order_id: UUID
    ) -> DeliveryOrder | None:
        return next(
            (
                item
                for item in self._delivery_orders.values()
                if item.tenant_id == self._tenant_id
                and item.sales_order_id == sales_order_id
            ),
            None,
        )

    def get_delivery_order_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> DeliveryOrder | None:
        return next(
            (
                item
                for item in self._delivery_orders.values()
                if item.tenant_id == self._tenant_id
                and item.idempotency_key == idempotency_key
            ),
            None,
        )

    def list_delivery_orders_by_sales_order(
        self, sales_order_id: UUID
    ) -> list[DeliveryOrder]:
        return [
            item
            for item in self._delivery_orders.values()
            if item.tenant_id == self._tenant_id
            and item.sales_order_id == sales_order_id
        ]

    def add_ar_invoice(self, invoice: ARInvoice) -> None:
        if invoice.tenant_id != self._tenant_id:
            raise ValueError("AR invoice is outside repository tenant")
        if (
            self.get_ar_invoice_by_delivery_order(invoice.delivery_order_id)
            is not None
        ):
            raise ValueError("AR invoice already exists")
        self._ar_invoices[invoice.id] = invoice

    def save_ar_invoice(
        self, invoice: ARInvoice, *, expected_version: int
    ) -> None:
        current = self.get_ar_invoice(invoice.id)
        if current is None or current.version != expected_version:
            raise ValueError("AR invoice version conflict")
        self._ar_invoices[invoice.id] = invoice

    def get_ar_invoice(self, invoice_id: UUID) -> ARInvoice | None:
        invoice = self._ar_invoices.get(invoice_id)
        if invoice is None or invoice.tenant_id != self._tenant_id:
            return None
        return invoice

    def get_ar_invoice_by_delivery_order(
        self, delivery_order_id: UUID
    ) -> ARInvoice | None:
        return next(
            (
                item
                for item in self._ar_invoices.values()
                if item.tenant_id == self._tenant_id
                and item.delivery_order_id == delivery_order_id
            ),
            None,
        )

    def add_return_authorization(
        self, authorization: ReturnAuthorization
    ) -> None:
        if authorization.tenant_id != self._tenant_id:
            raise ValueError("return authorization is outside repository tenant")
        if (
            self.get_return_authorization_by_delivery_order(
                authorization.delivery_order_id
            )
            is not None
        ):
            raise ValueError("return authorization already exists")
        if (
            self.get_return_authorization_by_idempotency_key(
                authorization.idempotency_key
            )
            is not None
        ):
            raise ValueError("return authorization idempotency key exists")
        self._return_authorizations[authorization.id] = authorization

    def get_return_authorization(
        self, return_authorization_id: UUID
    ) -> ReturnAuthorization | None:
        authorization = self._return_authorizations.get(return_authorization_id)
        if (
            authorization is None
            or authorization.tenant_id != self._tenant_id
        ):
            return None
        return authorization

    def get_return_authorization_by_credit_note_id(
        self, credit_note_id: UUID
    ) -> ReturnAuthorization | None:
        return next(
            (
                item
                for item in self._return_authorizations.values()
                if item.tenant_id == self._tenant_id
                and item.credit_note_id == credit_note_id
            ),
            None,
        )

    def get_return_authorization_by_delivery_order(
        self, delivery_order_id: UUID
    ) -> ReturnAuthorization | None:
        return next(
            (
                item
                for item in self._return_authorizations.values()
                if item.tenant_id == self._tenant_id
                and item.delivery_order_id == delivery_order_id
            ),
            None,
        )

    def get_return_authorization_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ReturnAuthorization | None:
        return next(
            (
                item
                for item in self._return_authorizations.values()
                if item.tenant_id == self._tenant_id
                and item.idempotency_key == idempotency_key
            ),
            None,
        )

    def save_return_authorization(
        self, authorization: ReturnAuthorization, *, expected_version: int
    ) -> None:
        current = self.get_return_authorization(authorization.id)
        if current is None or current.version != expected_version:
            raise ValueError("return authorization version conflict")
        if (
            current.credit_note_id is not None
            and current.credit_note_id != authorization.credit_note_id
        ):
            raise ValueError("return authorization credit note link conflict")
        self._return_authorizations[authorization.id] = authorization

    def get_confirm_policy(self) -> TenantConfirmPolicy | None:
        if (
            self._confirm_policy is None
            or self._confirm_policy.tenant_id != self._tenant_id
        ):
            return None
        return self._confirm_policy

    def save_confirm_policy(
        self, policy: TenantConfirmPolicy, *, expected_version: int
    ) -> None:
        if policy.tenant_id != self._tenant_id:
            raise ValueError("confirm policy is outside repository tenant")
        current = self.get_confirm_policy()
        if current is None:
            if expected_version != 0:
                raise ValueError("confirm policy version conflict")
        elif current.version != expected_version:
            raise ValueError("confirm policy version conflict")
        self._confirm_policy = policy

    def next_quote_line_number(self, quote_id: UUID) -> int:
        numbers = [
            item.line_number
            for item in self._quote_lines.values()
            if item.tenant_id == self._tenant_id and item.quote_id == quote_id
        ]
        return max(numbers, default=0) + 1

    def add_quote_line(self, quote_line: QuoteLine) -> None:
        if quote_line.tenant_id != self._tenant_id:
            raise ValueError("quote line is outside repository tenant")
        if any(
            item.quote_id == quote_line.quote_id
            and item.line_number == quote_line.line_number
            for item in self._quote_lines.values()
        ):
            raise ValueError("quote line number already exists")
        self._quote_lines[quote_line.id] = quote_line

    def get_quote_line(
        self, quote_id: UUID, quote_line_id: UUID
    ) -> QuoteLine | None:
        quote_line = self._quote_lines.get(quote_line_id)
        if (
            quote_line is None
            or quote_line.tenant_id != self._tenant_id
            or quote_line.quote_id != quote_id
        ):
            return None
        return quote_line

    def list_quote_lines(self, quote_id: UUID) -> list[QuoteLine]:
        return sorted(
            (
                item
                for item in self._quote_lines.values()
                if item.tenant_id == self._tenant_id
                and item.quote_id == quote_id
            ),
            key=lambda item: item.line_number,
        )

    def save_quote_line(
        self, quote_line: QuoteLine, *, expected_version: int
    ) -> None:
        current = self.get_quote_line(quote_line.quote_id, quote_line.id)
        if current is None or current.version != expected_version:
            raise ValueError("quote line version conflict")
        self._quote_lines[quote_line.id] = quote_line

    def list_opportunities_for_customer(
        self, customer_id: UUID
    ) -> list[Opportunity]:
        return [
            item
            for item in self._opportunities.values()
            if item.tenant_id == self._tenant_id
            and item.customer_id == customer_id
        ]

    def list_ar_invoices_for_customer(
        self, customer_id: UUID
    ) -> list[ARInvoice]:
        return sorted(
            (
                item
                for item in self._ar_invoices.values()
                if item.tenant_id == self._tenant_id
                and item.customer_id == customer_id
            ),
            key=lambda item: (item.created_at, item.code, item.id),
        )

    def list_sales_orders_for_customer(
        self, customer_id: UUID
    ) -> list[SalesOrder]:
        opportunity_ids = {
            item.id for item in self.list_opportunities_for_customer(customer_id)
        }
        requirement_ids = {
            item.id
            for item in self._requirements.values()
            if item.tenant_id == self._tenant_id
            and item.opportunity_id in opportunity_ids
        }
        return [
            item
            for item in self._sales_orders.values()
            if item.tenant_id == self._tenant_id
            and item.requirement_id in requirement_ids
        ]

    def list_delivery_orders_for_customer(
        self, customer_id: UUID
    ) -> list[DeliveryOrder]:
        sales_order_ids = {
            item.id for item in self.list_sales_orders_for_customer(customer_id)
        }
        return [
            item
            for item in self._delivery_orders.values()
            if item.tenant_id == self._tenant_id
            and item.sales_order_id in sales_order_ids
        ]

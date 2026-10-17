from . import BASIC, COMFORT, EXTENDED, NS_RAM
from .accounting import (
    IncludedTradeTax,
    LineApplicableTradeTax,
    LineBillingSpecifiedPeriod,
    LineTradeAllowanceCharge,
    ReceivableAccountingAccount,
    TradeAllowanceCharge,
)
from .container import Container
from .delivery import DeliveryTerms, SupplyChainEvent
from .elements import Element
from .fields import (
    CurrencyField,
    DecimalField,
    Field,
    MultiField,
    QuantityField,
    StringField,
)
from .note import IncludedNote
from .party import (
    ItemSellerTradeParty,
    LineShipToTradeParty,
    LineUltimateShipToTradeParty,
)
from .product import TradeProduct
from .references import (
    LineAdditionalReferencedDocument,
    LineBuyerOrderReferencedDocument,
    LineContractReferencedDocument,
    LineDeliveryNoteReferencedDocument,
    LineDespatchAdviceReferencedDocument,
    LineInvoiceReferencedDocument,
    LineQuotationReferencedDocument,
    LineReceivingAdviceReferencedDocument,
    LineSettlementAdditionalReferencedDocument,
    LineSellerOrderReferencedDocument,
    LineUltimateCustomerOrderReferencedDocument,
)


class AllowanceCharge(TradeAllowanceCharge):
    sequence_numeric = None
    basis_quantity = None
    trade_tax = None

    class Meta:
        namespace = NS_RAM
        tag = "AppliedTradeAllowanceCharge"


class GrossPrice(Element):
    amount = DecimalField(
        NS_RAM, "ChargeAmount", required=True, profile=COMFORT, _d="Bruttopreis"
    )
    basis_quantity = QuantityField(
        NS_RAM, "BasisQuantity", required=False, profile=COMFORT, _d="Preisbasismenge"
    )
    charge: Container = MultiField(AllowanceCharge, required=False, profile=COMFORT)

    class Meta:
        namespace = NS_RAM
        tag = "GrossPriceProductTradePrice"


class NetPrice(Element):
    amount = DecimalField(NS_RAM, "ChargeAmount", required=True, profile=COMFORT)
    basis_quantity = QuantityField(
        NS_RAM, "BasisQuantity", required=False, profile=COMFORT, _d="Preisbasismenge"
    )
    included_trade_tax: IncludedTradeTax = Field(
        IncludedTradeTax,
        required=False,
        profile=EXTENDED,
        _d="Im Preis enthaltene Steuer (B2C)",
    )

    class Meta:
        namespace = NS_RAM
        tag = "NetPriceProductTradePrice"


class LineDocument(Element):
    line_id = StringField(NS_RAM, "LineID")
    parent_line_id = StringField(
        NS_RAM,
        "ParentLineID",
        required=False,
        profile=EXTENDED,
        _d="Kennung der übergeordneten Position",
    )
    line_status_code = StringField(NS_RAM, "LineStatusCode")
    line_status_reason_code = StringField(NS_RAM, "LineStatusReasonCode")
    notes: Container = MultiField(IncludedNote)

    class Meta:
        namespace = NS_RAM
        tag = "AssociatedDocumentLineDocument"


class LineAgreement(Element):
    delivery_terms: DeliveryTerms = Field(
        DeliveryTerms,
        required=False,
        profile=EXTENDED,
        _d="Lieferbedingungen der Position",
    )
    seller_order: LineSellerOrderReferencedDocument = Field(
        LineSellerOrderReferencedDocument,
        required=False,
        profile=EXTENDED,
        _d="Detailinformationen zum zugehörigen Auftrag",
    )
    buyer_order: LineBuyerOrderReferencedDocument = Field(
        LineBuyerOrderReferencedDocument, required=False, profile=EXTENDED
    )
    quotation: LineQuotationReferencedDocument = Field(
        LineQuotationReferencedDocument,
        required=False,
        profile=EXTENDED,
        _d="Detailinformationen zum zugehörigen Angebot",
    )
    contract: LineContractReferencedDocument = Field(
        LineContractReferencedDocument, required=False, profile=EXTENDED
    )
    additional_references: Container = MultiField(
        LineAdditionalReferencedDocument, required=False, profile=COMFORT
    )
    gross: GrossPrice = Field(GrossPrice, required=False, profile=COMFORT)
    net: NetPrice = Field(NetPrice)
    item_seller: ItemSellerTradeParty = Field(
        ItemSellerTradeParty,
        required=False,
        profile=EXTENDED,
        _d="Abweichender Verkäufer der Position",
    )
    customer_order: LineUltimateCustomerOrderReferencedDocument = Field(
        LineUltimateCustomerOrderReferencedDocument, required=False, profile=EXTENDED
    )
    further_customer_orders: Container = MultiField(
        LineUltimateCustomerOrderReferencedDocument,
        required=False,
        profile=EXTENDED,
        _d="Weitere Aufträge des Endkunden",
    )

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedLineTradeAgreement"


class LineDelivery(Element):
    billed_quantity = QuantityField(
        NS_RAM, "BilledQuantity", required=False, profile=BASIC, _d="Menge, berechnet"
    )
    charge_free_quantity = QuantityField(
        NS_RAM,
        "ChargeFreeQuantity",
        required=False,
        profile=EXTENDED,
        _d="Menge, ohne Berechnung",
    )
    package_quantity = QuantityField(
        NS_RAM,
        "PackageQuantity",
        required=False,
        profile=EXTENDED,
        _d="Anzahl Packstücke",
    )
    per_package_unit_quantity = QuantityField(
        NS_RAM,
        "PerPackageUnitQuantity",
        required=False,
        profile=EXTENDED,
        _d="Menge pro Packstück",
    )
    ship_to: LineShipToTradeParty = Field(
        LineShipToTradeParty, required=False, profile=EXTENDED
    )
    ultimate_ship_to: LineUltimateShipToTradeParty = Field(
        LineUltimateShipToTradeParty, required=False, profile=EXTENDED
    )
    event: SupplyChainEvent = Field(
        SupplyChainEvent,
        required=False,
        profile=EXTENDED,
        _d="Detailinformationen zur tatsächlichen Lieferung",
    )
    despatch_advice: LineDespatchAdviceReferencedDocument = Field(
        LineDespatchAdviceReferencedDocument, required=False, profile=EXTENDED
    )
    receiving_advice: LineReceivingAdviceReferencedDocument = Field(
        LineReceivingAdviceReferencedDocument, required=False, profile=EXTENDED
    )
    delivery_note: LineDeliveryNoteReferencedDocument = Field(
        LineDeliveryNoteReferencedDocument, required=False, profile=EXTENDED
    )

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedLineTradeDelivery"


class LineSummation(Element):
    total_amount = DecimalField(
        NS_RAM,
        "LineTotalAmount",
        required=False,
        profile=COMFORT,
        _d="Nettobetrag der Rechnungsposition",
    )
    charge_total = DecimalField(
        NS_RAM,
        "ChargeTotalAmount",
        required=False,
        profile=EXTENDED,
        _d="Gesamtbetrag der Positionszuschläge",
    )
    allowance_total = DecimalField(
        NS_RAM,
        "AllowanceTotalAmount",
        required=False,
        profile=EXTENDED,
        _d="Gesamtbetrag der Positionsabschläge",
    )
    tax_total = CurrencyField(
        NS_RAM,
        "TaxTotalAmount",
        required=False,
        profile=EXTENDED,
        _d="Gesamtbetrag der Positionssteuern",
    )
    tax_total_other_currency = CurrencyField(
        NS_RAM,
        "TaxTotalAmount",
        required=False,
        profile=EXTENDED,
        _d="Gesamtbetrag der Positionssteuern in Buchungswährung",
    )
    grand_total = DecimalField(
        NS_RAM,
        "GrandTotalAmount",
        required=False,
        profile=EXTENDED,
        _d="Gesamtbruttobetrag der Position",
    )
    total_allowance_charge = DecimalField(
        NS_RAM,
        "TotalAllowanceChargeAmount",
        required=False,
        profile=EXTENDED,
        _d="Gesamtbetrag der Zu- und Abschläge",
    )

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedTradeSettlementLineMonetarySummation"


class LineSettlement(Element):
    trade_tax: LineApplicableTradeTax = Field(LineApplicableTradeTax, required=False)
    further_trade_taxes: Container = MultiField(
        LineApplicableTradeTax,
        required=False,
        profile=EXTENDED,
        _d="Weitere Steuerangaben der Position",
    )
    period: LineBillingSpecifiedPeriod = Field(
        LineBillingSpecifiedPeriod, required=False
    )
    allowance_charge: Container = MultiField(
        LineTradeAllowanceCharge,
        required=False,
        _d="Schalter für Zu-/Abschlag",
    )
    monetary_summation: LineSummation = Field(
        LineSummation, required=False, profile=BASIC
    )
    invoice_referenced_document: LineInvoiceReferencedDocument = Field(
        LineInvoiceReferencedDocument,
        required=False,
        profile=EXTENDED,
        _d="Referenz auf die vorausgegangene Rechnung",
    )
    additional_referenced_document: LineSettlementAdditionalReferencedDocument = Field(
        LineSettlementAdditionalReferencedDocument,
        required=False,
        profile=COMFORT,
    )
    further_additional_referenced_documents: Container = MultiField(
        LineSettlementAdditionalReferencedDocument,
        required=False,
        profile=EXTENDED,
        _d="Weitere Referenzdokumente der Position",
    )
    accounting_account: ReceivableAccountingAccount = Field(
        ReceivableAccountingAccount,
        required=False,
        profile=COMFORT,
        _d="Detailinformationen zur Buchungsreferenz",
    )
    further_accounting_accounts: Container = MultiField(
        ReceivableAccountingAccount,
        required=False,
        profile=EXTENDED,
        _d="Weitere Buchungsreferenzen",
    )

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedLineTradeSettlement"


class LineItem(Element):
    document: LineDocument = Field(LineDocument, required=True)
    product: TradeProduct = Field(TradeProduct)
    agreement: LineAgreement = Field(LineAgreement)
    delivery: LineDelivery = Field(LineDelivery)
    settlement: LineSettlement = Field(LineSettlement, required=True)

    class Meta:
        namespace = NS_RAM
        tag = "IncludedSupplyChainTradeLineItem"

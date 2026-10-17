from . import BASIC, COMFORT, EXTENDED, NS_RAM, NS_RSM, NS_QDT
from .accounting import (
    ApplicableTradeTax,
    AppliedTradeTax,
    BillingSpecifiedPeriod,
    IncludedTradeTax,
    MonetarySummation,
    ReceivableAccountingAccount,
    TradeAllowanceCharge,
)
from .delivery import DeliveryTerms, TradeDelivery
from .container import Container
from .elements import Element
from .fields import DateTimeField, DecimalField, Field, MultiField, StringField
from .party import (
    BuyerAgentTradeParty,
    BuyerTaxRepresentativeTradeParty,
    BuyerTradeParty,
    EndUserTradeParty,
    InvoiceeTradeParty,
    InvoicerTradeParty,
    PayeeTradeParty,
    PayerTradeParty,
    SalesAgentTradeParty,
    SellerTaxRepresentativeTradeParty,
    SellerTradeParty,
)
from .payment import (
    PaymentMeans,
    PaymentTerms,
    TaxApplicableTradeCurrencyExchange,
)
from .references import (
    AdditionalReferencedDocument,
    BuyerOrderReferencedDocument,
    SellerOrderReferencedDocument,
    ContractReferencedDocument,
    InvoiceReferencedDocument,
    InvoiceSpecifiedReferencedDocument,
    ProcuringProjectType,
    QuotationReferencedDocument,
    UltimateCustomerOrderReferencedDocument,
)
from .tradelines import LineItem


class TradeAgreement(Element):
    buyer_reference = StringField(
        NS_RAM,
        "BuyerReference",
        required=False,
        profile=COMFORT,
        _d="Referenz des Käufers",
    )
    seller: SellerTradeParty = Field(
        SellerTradeParty, required=True, _d="Detailinformationen zum Verkäufer"
    )
    buyer: BuyerTradeParty = Field(BuyerTradeParty, required=True)
    sales_agent: SalesAgentTradeParty = Field(
        SalesAgentTradeParty,
        required=False,
        profile=EXTENDED,
        _d="Handelsvertreter",
    )
    buyer_tax_representative_party: BuyerTaxRepresentativeTradeParty = Field(
        BuyerTaxRepresentativeTradeParty,
        required=False,
        profile=EXTENDED,
        _d="Steuervertreter des Käufers",
    )
    seller_tax_representative_party: SellerTaxRepresentativeTradeParty = Field(
        SellerTaxRepresentativeTradeParty, required=False
    )
    end_user: EndUserTradeParty = Field(
        EndUserTradeParty, required=False, _d="Abweichender Endverbraucher"
    )
    delivery_terms: DeliveryTerms = Field(
        DeliveryTerms, required=False, profile=EXTENDED
    )
    seller_order: SellerOrderReferencedDocument = Field(
        SellerOrderReferencedDocument, required=False, profile=COMFORT
    )
    buyer_order: BuyerOrderReferencedDocument = Field(
        BuyerOrderReferencedDocument, required=False
    )
    quotation: QuotationReferencedDocument = Field(
        QuotationReferencedDocument,
        required=False,
        profile=EXTENDED,
        _d="Detailinformationen zum zugehörigen Angebot",
    )
    contract: ContractReferencedDocument = Field(
        ContractReferencedDocument, required=False, profile=COMFORT
    )
    additional_references: Container = MultiField(
        AdditionalReferencedDocument, required=False, profile=COMFORT
    )
    buyer_agent: BuyerAgentTradeParty = Field(
        BuyerAgentTradeParty,
        required=False,
        profile=EXTENDED,
        _d="Einkaufsagent",
    )
    description = StringField(NS_RAM, "Description", required=False, profile=COMFORT)
    procuring_project_type: ProcuringProjectType = Field(
        ProcuringProjectType, required=False
    )
    customer_order: UltimateCustomerOrderReferencedDocument = Field(
        UltimateCustomerOrderReferencedDocument, required=False, profile=COMFORT
    )

    class Meta:
        namespace = NS_RAM
        tag = "ApplicableHeaderTradeAgreement"


class LogisticsServiceCharge(Element):
    description = StringField(
        NS_RAM,
        "Description",
        required=True,
        profile=COMFORT,
        _d="Identifikation der Servicegebühr",
    )
    applied_amount = DecimalField(
        NS_RAM,
        "AppliedAmount",
        required=True,
        profile=COMFORT,
        _d="Betrag der Servicegebühr",
    )
    trade_tax: Container = MultiField(AppliedTradeTax, required=False, profile=COMFORT)

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedLogisticsServiceCharge"


class FinancialAdjustment(Element):
    reason = StringField(
        NS_RAM,
        "Reason",
        required=True,
        profile=EXTENDED,
        _d="Beschreibung der Zahlung im Namen Dritter",
    )
    actual_amount = DecimalField(
        NS_RAM,
        "ActualAmount",
        required=True,
        profile=EXTENDED,
        _d="Betrag der Zahlung im Namen Dritter",
    )

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedFinancialAdjustment"


class AdvancePayment(Element):
    paid_amount = DecimalField(NS_RAM, "PaidAmount")
    received_date = DateTimeField(
        NS_RAM, "FormattedReceivedDateTime", date_time_namespace=NS_QDT
    )
    included_trade_tax: Container = MultiField(IncludedTradeTax)
    referenced_document: InvoiceSpecifiedReferencedDocument = Field(
        InvoiceSpecifiedReferencedDocument, required=False, profile=EXTENDED
    )

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedAdvancePayment"


class TradeSettlement(Element):
    creditor_reference_id = StringField(NS_RAM, "CreditorReferenceID")
    payment_reference = StringField(NS_RAM, "PaymentReference")
    tax_currency_code = StringField(
        NS_RAM, "TaxCurrencyCode", required=False, profile=BASIC
    )
    currency_code = StringField(NS_RAM, "InvoiceCurrencyCode")
    issuer_reference = StringField(NS_RAM, "InvoiceIssuerReference", profile=EXTENDED)
    invoicer: InvoicerTradeParty = Field(
        InvoicerTradeParty, required=False, profile=EXTENDED, _d="Rechnungsaussteller"
    )
    invoicee: InvoiceeTradeParty = Field(
        InvoiceeTradeParty, required=False, profile=EXTENDED, _d="Rechnungsempfänger"
    )
    payee: PayeeTradeParty = Field(
        PayeeTradeParty, required=False, profile=BASIC, _d="Zahlungsempfänger"
    )
    payer: PayerTradeParty = Field(
        PayerTradeParty, required=False, profile=EXTENDED, _d="Zahlungspflichtiger"
    )
    invoice_currency: TaxApplicableTradeCurrencyExchange = Field(
        TaxApplicableTradeCurrencyExchange, profile=EXTENDED
    )
    payment_means: Container = MultiField(
        PaymentMeans, required=False, profile=EXTENDED
    )
    trade_tax: Container = MultiField(ApplicableTradeTax)
    period: BillingSpecifiedPeriod = Field(
        BillingSpecifiedPeriod, required=False, profile=BASIC
    )
    allowance_charge: Container = MultiField(
        TradeAllowanceCharge,
        required=False,
        profile=BASIC,
        _d="Schalter für Zu-/Abschlag",
    )
    service_charge: Container = MultiField(
        LogisticsServiceCharge, required=False, profile=EXTENDED
    )
    terms: Container = MultiField(PaymentTerms, required=False, profile=BASIC)
    monetary_summation: MonetarySummation = Field(
        MonetarySummation,
        required=True,
        profile=BASIC,
        _d="Detailinformation zu Belegsummen",
    )
    financial_adjustment: Container = MultiField(
        FinancialAdjustment,
        required=False,
        profile=EXTENDED,
        _d="Zahlungen im Namen Dritter",
    )
    invoice_referenced_document: InvoiceReferencedDocument = Field(
        InvoiceReferencedDocument, required=False, profile=BASIC
    )
    accounting_account: ReceivableAccountingAccount = Field(
        ReceivableAccountingAccount,
        required=False,
        profile=BASIC,
        _d="Detailinformationen zur Buchungsreferenz",
    )
    advance_payment: Container = MultiField(
        AdvancePayment, required=False, profile=EXTENDED
    )

    class Meta:
        namespace = NS_RAM
        tag = "ApplicableHeaderTradeSettlement"


class TradeTransaction(Element):
    items: Container = MultiField(LineItem, required=True)
    agreement: TradeAgreement = Field(TradeAgreement, required=True)
    delivery: TradeDelivery = Field(TradeDelivery, required=True)
    settlement: TradeSettlement = Field(TradeSettlement, required=True)

    class Meta:
        namespace = NS_RSM
        tag = "SupplyChainTradeTransaction"

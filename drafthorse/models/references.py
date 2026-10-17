from . import BASIC, COMFORT, EXTENDED, NS_RAM, NS_QDT
from .elements import Element
from .fields import BinaryObjectField, DateTimeField, StringField, IDField


class ProcuringProjectType(Element):
    id = StringField(NS_RAM, "ID")
    name = StringField(NS_RAM, "Name")

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedProcuringProject"


class ReferencedDocument(Element):
    # All elements of ram:ReferencedDocumentType in XSD order, subclasses
    # remove the ones not used in their context
    issuer_assigned_id = IDField(
        NS_RAM, "IssuerAssignedID", required=False, profile=BASIC
    )
    uri_id = StringField(NS_RAM, "URIID", required=False, profile=COMFORT)
    line_id = StringField(NS_RAM, "LineID", required=False, profile=EXTENDED)
    type_code = StringField(NS_RAM, "TypeCode", required=False, profile=COMFORT)
    name = StringField(NS_RAM, "Name", required=False, profile=COMFORT)
    attached_object = BinaryObjectField(
        NS_RAM, "AttachmentBinaryObject", required=False, profile=COMFORT
    )
    reference_type_code = StringField(
        NS_RAM, "ReferenceTypeCode", required=False, profile=COMFORT
    )
    issue_date_time = DateTimeField(
        NS_RAM,
        "FormattedIssueDateTime",
        required=True,
        profile=BASIC,
        date_time_namespace=NS_QDT,
    )


class SimpleReferencedDocument(ReferencedDocument):
    # Reference with document number and date only
    uri_id = None
    line_id = None
    type_code = None
    name = None
    attached_object = None
    reference_type_code = None


class LineReferencedDocument(ReferencedDocument):
    # Reference with document number, line and date
    uri_id = None
    type_code = None
    name = None
    attached_object = None
    reference_type_code = None


class SellerOrderReferencedDocument(SimpleReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "SellerOrderReferencedDocument"


class BuyerOrderReferencedDocument(SimpleReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "BuyerOrderReferencedDocument"


class QuotationReferencedDocument(SimpleReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "QuotationReferencedDocument"


class ContractReferencedDocument(ReferencedDocument):
    uri_id = None
    line_id = None
    type_code = None
    name = None
    attached_object = None
    reference_type_code = StringField(
        NS_RAM,
        "ReferenceTypeCode",
        required=False,
        profile=EXTENDED,
        _d="Art des Vertrags (Code)",
    )

    class Meta:
        namespace = NS_RAM
        tag = "ContractReferencedDocument"


class AdditionalReferencedDocument(ReferencedDocument):
    line_id = None
    type_code = StringField(NS_RAM, "TypeCode", profile=COMFORT, required=True)
    reference_type_code = StringField(
        NS_RAM,
        "ReferenceTypeCode",
        required=False,
        profile=COMFORT,
        _d="Kennung des Schemas der referenzierten Objektkennung",
    )

    class Meta:
        namespace = NS_RAM
        tag = "AdditionalReferencedDocument"


class InvoiceReferencedDocument(ReferencedDocument):
    uri_id = None
    line_id = None
    name = None
    attached_object = None
    reference_type_code = None

    class Meta:
        namespace = NS_RAM
        tag = "InvoiceReferencedDocument"


class InvoiceSpecifiedReferencedDocument(ReferencedDocument):
    uri_id = None
    line_id = None
    name = None
    attached_object = None
    reference_type_code = None

    class Meta:
        namespace = NS_RAM
        tag = "InvoiceSpecifiedReferencedDocument"


class UltimateCustomerOrderReferencedDocument(SimpleReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "UltimateCustomerOrderReferencedDocument"


class DespatchAdviceReferencedDocument(SimpleReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "DespatchAdviceReferencedDocument"


class LineUltimateCustomerOrderReferencedDocument(LineReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "UltimateCustomerOrderReferencedDocument"


class LineSellerOrderReferencedDocument(LineReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "SellerOrderReferencedDocument"


class LineBuyerOrderReferencedDocument(LineReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "BuyerOrderReferencedDocument"


class LineQuotationReferencedDocument(LineReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "QuotationReferencedDocument"


class LineContractReferencedDocument(LineReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "ContractReferencedDocument"


class LineDespatchAdviceReferencedDocument(LineReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "DespatchAdviceReferencedDocument"


class ReceivingAdviceReferencedDocument(SimpleReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "ReceivingAdviceReferencedDocument"


class LineInvoiceReferencedDocument(ReferencedDocument):
    uri_id = None
    name = None
    attached_object = None
    reference_type_code = None

    class Meta:
        namespace = NS_RAM
        tag = "InvoiceReferencedDocument"


class LineReceivingAdviceReferencedDocument(LineReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "ReceivingAdviceReferencedDocument"


class LineAdditionalReferencedDocument(ReferencedDocument):
    # Additional reference of the line agreement, all elements are used
    class Meta:
        namespace = NS_RAM
        tag = "AdditionalReferencedDocument"


class LineSettlementAdditionalReferencedDocument(ReferencedDocument):
    # Additional reference of the line settlement, e.g. an object identifier
    uri_id = None
    line_id = None
    name = None
    attached_object = None
    issue_date_time = None

    class Meta:
        namespace = NS_RAM
        tag = "AdditionalReferencedDocument"


class DeliveryNoteReferencedDocument(SimpleReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "DeliveryNoteReferencedDocument"


class LineDeliveryNoteReferencedDocument(LineReferencedDocument):
    class Meta:
        namespace = NS_RAM
        tag = "DeliveryNoteReferencedDocument"

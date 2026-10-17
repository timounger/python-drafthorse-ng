import os
import pytest
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from lxml import etree
from pypdf import PdfReader

from drafthorse.models.accounting import (
    AppliedTradeTax,
    CategoryTradeTax,
    TradeAllowanceCharge,
)
from drafthorse.models import NS_RAM
from drafthorse.models.document import Document
from drafthorse.models.elements import DirectDateTimeElement, IDElement
from drafthorse.models.party import TaxRegistration, TradeContact
from drafthorse.models.payment import PaymentMeans
from drafthorse.models.product import ProductClassification, ReferencedProduct
from drafthorse.models.references import (
    AdditionalReferencedDocument,
    InvoiceReferencedDocument,
    LineAdditionalReferencedDocument,
    LineInvoiceReferencedDocument,
)
from drafthorse.models.trade import (
    FinancialAdjustment,
    LogisticsServiceCharge,
    TradeAgreement,
)
from drafthorse.models.tradelines import LineItem
from drafthorse.pdf import attach_xml


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_readme_construction_example_pdf16(invoice_document, empty_pdf16_bytes):
    """
    Test using a PDF 1.6 version
    """
    xml = invoice_document.serialize(schema="FACTUR-X_EXTENDED")
    output_pdf = attach_xml(empty_pdf16_bytes, xml)

    assert output_pdf


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_readme_construction_example_pdf17(invoice_document, invoice_pdf17_bytes):
    """
    Test using a PDF 1.7 version in order to cover the output intents handling
    """
    xml = invoice_document.serialize(schema="FACTUR-X_EXTENDED")
    output_pdf = attach_xml(invoice_pdf17_bytes, xml)

    assert output_pdf


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_readme_construction_example_pdf17_en16931(
    invoice_document, invoice_pdf17_bytes
):
    """
    Test using a PDF 1.7 version in order to cover the output intents handling
    """
    doc = invoice_document
    doc.context.guideline_parameter.id = "urn:cen.eu:en16931:2017"
    xml = doc.serialize(schema="FACTUR-X_EXTENDED")
    output_pdf = attach_xml(invoice_pdf17_bytes, xml)

    assert output_pdf


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_readme_construction_example_pdf17_xrechnung2(
    invoice_document, invoice_pdf17_bytes
):
    """
    Test using a PDF 1.7 version in order to cover the output intents handling
    """
    doc = invoice_document
    doc.context.guideline_parameter.id = (
        "urn:cen.eu:en16931:2017#compliant#urn:xoev-de:kosit:standard:xrechnung_2.3"
    )
    xml = doc.serialize(schema="FACTUR-X_EXTENDED")
    output_pdf = attach_xml(invoice_pdf17_bytes, xml)

    assert output_pdf


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_readme_construction_example_pdf17_xrechnung3(
    invoice_document, invoice_pdf17_bytes
):
    """
    Test using a PDF 1.7 version in order to cover the output intents handling
    """
    doc = invoice_document
    doc.context.guideline_parameter.id = (
        "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0"
    )
    xml = doc.serialize(schema="FACTUR-X_EXTENDED")
    output_pdf = attach_xml(invoice_pdf17_bytes, xml)

    assert output_pdf


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_invalid_invoice_XML_profile_exceptions(invoice_document, invoice_pdf17_bytes):
    """
    Test using a PDF 1.7 version in order to cover the output intents handling
    """
    doc = invoice_document
    doc.context.guideline_parameter.id = (
        "urn:cen.eu:en16932:2017#conformant#urn:factur-x.eu:1p0:wrong"
    )
    xml = doc.serialize(schema="FACTUR-X_EXTENDED")
    # invalid pdf type
    with pytest.raises(Exception) as exc_info:
        attach_xml(invoice_pdf17_bytes, xml)

    assert str(exc_info.value) == "Invalid XML profile!"


@pytest.mark.parametrize("invoice_document", ["220"], indirect=True)
def test_invalid_invoice_exceptions(invoice_document, invoice_pdf17_bytes):
    """
    Test invalid cases
    """
    xml = invoice_document.serialize(schema="FACTUR-X_EXTENDED")

    # invalid pdf type
    with pytest.raises(Exception) as exc_info:
        attach_xml("invalid_pdf_type", xml)

    assert str(exc_info.value) == "Please supply original PDF as bytes."

    # invalid xml type
    with pytest.raises(Exception) as exc_info:
        attach_xml(invoice_pdf17_bytes, "invalid_xml_type")

    assert str(exc_info.value) == "Please supply XML data as bytes."


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_unused_name_spaces_included(invoice_document):
    doc = invoice_document
    doc.context.guideline_parameter.id = (
        "urn:cen.eu:en16932:2017#conformant#urn:factur-x.eu:1p0:wrong"
    )
    xml = doc.serialize(schema="FACTUR-X_EXTENDED")
    assert (
        'xmlns:qdt="urn:un:unece:uncefact:data:standard:QualifiedDataType:100"'
        in xml.decode()
    )
    assert 'xmlns:xs="http://www.w3.org/2001/XMLSchema"' in xml.decode()
    assert 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' in xml.decode()
    assert "xs:" not in xml.decode()
    assert "xsi:" not in xml.decode()


@pytest.mark.parametrize(
    "class_code",
    [
        ("TST", "19.0", "AB-12"),
        ("TST", "", "AB-12"),
        ("", "", "AB-12"),
    ],
)
def test_product_classification_roundtrip(class_code):
    li = LineItem()
    li.product.name = "Rainbow"
    classification = ProductClassification()
    classification.class_code = class_code
    li.product.classifications.add(classification)
    xml = ET.tostring(li.to_etree())

    parsed = LineItem().from_etree(ET.fromstring(xml))
    parsed_code = list(parsed.product.classifications.children)[0].class_code

    assert parsed_code._list_id == class_code[0]
    assert parsed_code._list_version_id == class_code[1]
    assert parsed_code._text == class_code[2]
    assert ET.tostring(parsed.to_etree()) == xml


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_referenced_documents_follow_xsd_sequence(invoice_document):
    doc = invoice_document
    invoice_ref = doc.trade.settlement.invoice_referenced_document
    invoice_ref.issuer_assigned_id = "RE1000"
    invoice_ref.type_code = "380"
    invoice_ref.issue_date_time = date(2024, 1, 1)
    li = list(doc.trade.items.children)[0]
    li.agreement.buyer_order.issuer_assigned_id = "B1000"
    li.agreement.buyer_order.line_id = "1"
    li.agreement.buyer_order.issue_date_time = date(2024, 1, 1)

    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

    parsed = Document.parse(xml)
    assert parsed.trade.settlement.invoice_referenced_document.type_code._text == "380"
    assert (
        list(parsed.trade.items.children)[0].agreement.buyer_order.line_id._text == "1"
    )


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_line_invoice_referenced_document_line_id(invoice_document):
    doc = invoice_document
    invoice_ref = LineInvoiceReferencedDocument()
    invoice_ref.issuer_assigned_id = "RE1000"
    invoice_ref.line_id = "3"
    invoice_ref.type_code = "380"
    invoice_ref.issue_date_time = date(2024, 1, 1)
    li = list(doc.trade.items.children)[0]
    li.settlement.invoice_referenced_document.add(invoice_ref)

    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

    parsed = Document.parse(xml)
    li = list(parsed.trade.items.children)[0]
    parsed_ref = list(li.settlement.invoice_referenced_document.children)[0]
    assert parsed_ref.line_id._text == "3"
    assert parsed_ref.type_code._text == "380"

    # LineID is marked as not used on header level
    with pytest.raises(AttributeError):
        doc.trade.settlement.invoice_referenced_document.line_id = "3"


def test_parse_fills_fields_sharing_a_tag_in_order():
    samples = os.path.join(os.path.dirname(__file__), "samples")
    with open(
        os.path.join(samples, "zugferd_2p5_EN16931_E05_01_Einfach.xml"), "rb"
    ) as f:
        doc = Document.parse(f.read())
    summation = doc.trade.settlement.monetary_summation
    assert summation.tax_total._amount == Decimal("56.87")
    assert summation.tax_total._currency == "EUR"
    assert summation.tax_total_other_currency.children == []

    with open(
        os.path.join(samples, "zugferd_2p5_EXTENDED_X07_01_Fremdwaehrung.xml"), "rb"
    ) as f:
        doc = Document.parse(f.read())
    summation = doc.trade.settlement.monetary_summation
    assert summation.tax_total._amount == Decimal("163.16")
    assert summation.tax_total._currency == "GBP"
    assert summation.tax_total_other_currency.children == [("183.14", "EUR")]


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_elements_follow_xsd_sequence(invoice_document):
    doc = invoice_document
    agreement = doc.trade.agreement
    agreement.seller_tax_representative_party.name = "Steuervertreter GmbH"
    agreement.seller_tax_representative_party.address.country_id = "DE"
    agreement.seller_tax_representative_party.tax_registrations.add(
        TaxRegistration(id=("VA", "DE987654321"))
    )
    agreement.end_user.name = "Endkunde"
    doc.trade.delivery.receiving_advice.issuer_assigned_id = "WE1000"
    doc.trade.delivery.delivery_note.issuer_assigned_id = "LS1000"
    doc.trade.delivery.delivery_note.issue_date_time = date(2024, 1, 1)
    tax = list(doc.trade.settlement.trade_tax.children)[0]
    tax.tax_point_date = date(2024, 1, 1)

    li = list(doc.trade.items.children)[0]
    li.agreement.customer_order.issuer_assigned_id = "EK1000"
    li.agreement.customer_order.line_id = "1"
    ref = LineAdditionalReferencedDocument()
    ref.issuer_assigned_id = "AB1000"
    ref.type_code = "130"
    ref.attached_object = ("text/csv", "data.csv", "MTsy")
    ref.reference_type_code = "AAA"
    li.agreement.additional_references.add(ref)

    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

    parsed = Document.parse(xml)
    tax = list(parsed.trade.settlement.trade_tax.children)[0]
    assert tax.tax_point_date._value == date(2024, 1, 1)
    li = list(parsed.trade.items.children)[0]
    assert li.agreement.customer_order.issuer_assigned_id._text == "EK1000"
    ref = list(li.agreement.additional_references.children)[0]
    assert ref.reference_type_code._text == "AAA"


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_factur_x_1_09_extended_terms(invoice_document):
    doc = invoice_document
    settlement = doc.trade.settlement
    settlement.tax_currency_code = "USD"

    # BG-X-22 with BT-X-563 / BT-X-564
    doc.trade.agreement.delivery_terms.type_code = "FCA"
    doc.trade.agreement.delivery_terms.location.country_id = "DE"
    doc.trade.agreement.delivery_terms.location.name = "Hamburg"

    # BT-215 / BT-216
    payment = PaymentMeans(type_code="59")
    payment.payer_account.iban = "DE02120300000000202051"
    payment.payer_account.account_name = "Kunde GmbH"
    payment.payer_institution.bic = "BYLADEM1001"
    settlement.payment_means.add(payment)

    # BT-177 / BT-177-1, BT-173 / BT-174
    charge = TradeAllowanceCharge()
    charge.indicator = True
    charge.actual_amount = Decimal("1.00")
    charge.reason_code = ("5153", "AAA")
    charge.reason = "Abgabe"
    tax = CategoryTradeTax()
    tax.type_code = "VAT"
    tax.exemption_reason = "Steuerbefreit"
    tax.category_code = "E"
    tax.exemption_reason_code = "VATEX-EU-132"
    tax.rate_applicable_percent = Decimal("0")
    charge.trade_tax.add(tax)
    settlement.allowance_charge.add(charge)

    # BT-X-591 / BT-X-592
    service = LogisticsServiceCharge()
    service.description = "Versand"
    service.applied_amount = Decimal("1.00")
    tax = AppliedTradeTax()
    tax.type_code = "VAT"
    tax.exemption_reason = "Steuerbefreit"
    tax.category_code = "E"
    tax.exemption_reason_code = "VATEX-EU-132"
    tax.rate_applicable_percent = Decimal("0")
    service.trade_tax.add(tax)
    settlement.service_charge.add(service)

    # BG-34 with BT-179 / BT-180
    adjustment = FinancialAdjustment()
    adjustment.reason = "Porto"
    adjustment.actual_amount = Decimal("2.50")
    settlement.financial_adjustment.add(adjustment)

    li = list(doc.trade.items.children)[0]
    # BT-X-565
    li.agreement.delivery_terms.type_code = "FCA"
    li.agreement.delivery_terms.location.country_id = "DE"
    # BG-X-90
    li.agreement.item_seller.name = "Anderer Verkäufer GmbH"
    li.agreement.item_seller.address.country_id = "DE"
    # BT-X-561
    li.delivery.package_quantity = (Decimal("2"), "XPK")
    li.delivery.per_package_unit_quantity = (Decimal("6"), "H87")
    # BG-X-93
    li.product.manufacturer.name = "Hersteller GmbH"
    li.product.manufacturer.address.country_id = "DE"
    # BT-X-590
    li.settlement.monetary_summation.tax_total = (Decimal("1.90"), "EUR")
    li.settlement.monetary_summation.tax_total_other_currency = (
        Decimal("2.10"),
        "USD",
    )

    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

    parsed = Document.parse(xml)
    agreement = parsed.trade.agreement
    assert agreement.delivery_terms.location.name._text == "Hamburg"
    settlement = parsed.trade.settlement
    payment = list(settlement.payment_means.children)[-1]
    assert payment.payer_account.account_name._text == "Kunde GmbH"
    assert payment.payer_institution.bic._text == "BYLADEM1001"
    charge = list(settlement.allowance_charge.children)[-1]
    assert charge.reason_code._list_id == "5153"
    assert charge.reason_code._text == "AAA"
    tax = list(charge.trade_tax.children)[0]
    assert tax.exemption_reason_code._text == "VATEX-EU-132"
    service = list(settlement.service_charge.children)[0]
    assert list(service.trade_tax.children)[0].exemption_reason._text == "Steuerbefreit"
    adjustment = list(settlement.financial_adjustment.children)[0]
    assert adjustment.actual_amount._value == Decimal("2.50")
    li = list(parsed.trade.items.children)[0]
    assert li.agreement.delivery_terms.location.country_id._text == "DE"
    assert li.agreement.item_seller.name._text == "Anderer Verkäufer GmbH"
    assert li.delivery.per_package_unit_quantity._amount == Decimal("6")
    assert li.product.manufacturer.name._text == "Hersteller GmbH"
    summation = li.settlement.monetary_summation
    assert summation.tax_total._amount == Decimal("1.90")
    assert summation.tax_total._currency == "EUR"
    assert summation.tax_total_other_currency._amount == Decimal("2.10")
    assert summation.tax_total_other_currency._currency == "USD"


def test_sub_invoice_line_without_agreement_and_delivery():
    li = LineItem()
    li.document.line_id = "1.1"
    li.document.parent_line_id = "1"
    li.document.line_status_reason_code = "INFORMATION"
    li.product.name = "Teil eines Sets"
    xml = ET.tostring(li.to_etree()).decode()

    assert "SpecifiedLineTradeAgreement" not in xml
    assert "SpecifiedLineTradeDelivery" not in xml
    parsed = LineItem().from_etree(ET.fromstring(xml))
    assert parsed.document.parent_line_id._text == "1"


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_extended_parties_and_references(invoice_document):
    doc = invoice_document
    agreement = doc.trade.agreement
    agreement.seller.contact.person_name = "Max Mustermann"
    agreement.seller.contact.type_code = "SR"
    for party in (
        agreement.sales_agent,
        agreement.buyer_tax_representative_party,
        agreement.buyer_agent,
    ):
        party.name = "Partei GmbH"
        party.address.country_id = "DE"
    agreement.buyer_tax_representative_party.tax_registrations.add(
        TaxRegistration(id=("VA", "DE123456789"))
    )
    agreement.quotation.issuer_assigned_id = "AN1000"
    agreement.quotation.issue_date_time = date(2024, 1, 1)
    agreement.contract.issuer_assigned_id = "V1000"
    agreement.contract.reference_type_code = "CT"
    ref = AdditionalReferencedDocument()
    ref.issuer_assigned_id = "OBJ1000"
    ref.type_code = "130"
    ref.reference_type_code = "AAA"
    agreement.additional_references.add(ref)

    terms = list(doc.trade.settlement.terms.children)[0]
    terms.payee.name = "Zahlungsempfänger GmbH"

    li = list(doc.trade.items.children)[0]
    li.agreement.seller_order.issuer_assigned_id = "AU1000"
    li.agreement.seller_order.line_id = "1"
    li.agreement.net.included_trade_tax.calculated_amount = Decimal("1.90")
    li.agreement.net.included_trade_tax.type_code = "VAT"
    li.agreement.net.included_trade_tax.category_code = "S"
    li.agreement.net.included_trade_tax.rate_applicable_percent = Decimal("19")
    included = ReferencedProduct()
    included.id = "TEIL-1"
    included.industry_assigned_id = "IND-1"
    included.name = "Teil"
    li.product.included_products.add(included)

    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

    parsed = Document.parse(xml)
    agreement = parsed.trade.agreement
    assert agreement.seller.contact.type_code._text == "SR"
    assert agreement.sales_agent.name._text == "Partei GmbH"
    assert agreement.buyer_tax_representative_party.name._text == "Partei GmbH"
    assert agreement.buyer_agent.name._text == "Partei GmbH"
    assert agreement.quotation.issuer_assigned_id._text == "AN1000"
    assert agreement.contract.reference_type_code._text == "CT"
    ref = list(agreement.additional_references.children)[-1]
    assert ref.reference_type_code._text == "AAA"
    terms = list(parsed.trade.settlement.terms.children)[0]
    assert terms.payee.name._text == "Zahlungsempfänger GmbH"
    li = list(parsed.trade.items.children)[0]
    assert li.agreement.seller_order.line_id._text == "1"
    assert li.agreement.net.included_trade_tax.rate_applicable_percent._value == 19
    included = list(li.product.included_products.children)[0]
    assert included.industry_assigned_id._text == "IND-1"


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_repeatable_elements(invoice_document):
    doc = invoice_document
    seller = doc.trade.agreement.seller
    seller.id = "LIEF-1"
    seller.further_ids.add("LIEF-2")
    seller.contact.person_name = "Erster Kontakt"
    contact = TradeContact()
    contact.person_name = "Zweiter Kontakt"
    seller.further_contacts.add(contact)

    settlement = doc.trade.settlement
    settlement.invoice_referenced_document.issuer_assigned_id = "RE1000"
    settlement.invoice_referenced_document.issue_date_time = date(2024, 1, 1)
    previous = InvoiceReferencedDocument()
    previous.issuer_assigned_id = "RE1001"
    previous.issue_date_time = date(2024, 1, 2)
    settlement.further_invoice_referenced_documents.add(previous)

    li = list(doc.trade.items.children)[0]
    li.product.batch_id = "CH-1"
    li.product.further_batch_ids.add("CH-2")

    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

    parsed = Document.parse(xml)
    seller = parsed.trade.agreement.seller
    assert seller.id._text == "LIEF-1"
    assert seller.further_ids.children == ["LIEF-2"]
    assert seller.contact.person_name._text == "Erster Kontakt"
    assert [c.person_name._text for c in seller.further_contacts.children] == [
        "Zweiter Kontakt"
    ]
    settlement = parsed.trade.settlement
    assert settlement.invoice_referenced_document.issuer_assigned_id._text == "RE1000"
    assert [
        r.issuer_assigned_id._text
        for r in settlement.further_invoice_referenced_documents.children
    ] == ["RE1001"]
    li = list(parsed.trade.items.children)[0]
    assert li.product.batch_id._text == "CH-1"
    assert li.product.further_batch_ids.children == ["CH-2"]


def test_header_agreement_has_no_description():
    with pytest.raises(AttributeError):
        TradeAgreement().description = "Not part of any schema"


def test_parse_xml_with_comments():
    samples = os.path.join(os.path.dirname(__file__), "samples")
    # The official sample contains a comment within a line item
    with open(
        os.path.join(samples, "zugferd_2p5_EN16931_E14_01_Kraftfahrversicherung.xml"),
        "rb",
    ) as f:
        doc = Document.parse(f.read())

    assert doc.header.id._text


def _attachment_info(pdf_bytes):
    reader = PdfReader(BytesIO(pdf_bytes))
    xmp = reader.trailer["/Root"]["/Metadata"].get_object().get_data().decode()
    filespec = reader.trailer["/Root"]["/AF"][0].get_object()

    def xmp_value(name):
        return re.search("<fx:%s>(.*?)<" % name, xmp).group(1)

    return {
        "level": xmp_value("ConformanceLevel"),
        "filename": xmp_value("DocumentFileName"),
        "version": xmp_value("Version"),
        "relationship": filespec["/AFRelationship"],
        "file": filespec["/F"],
        "header": pdf_bytes[:8],
    }


@pytest.mark.parametrize(
    "sample,level,relationship",
    [
        ("zugferd_2p5_MINIMUM_Rechnung.xml", "MINIMUM", "/Data"),
        ("zugferd_2p5_BASIC-WL_Einfach.xml", "BASIC WL", "/Data"),
        ("zugferd_2p5_BASIC_B01_01_Einfach.xml", "BASIC", "/Alternative"),
        ("zugferd_2p5_EN16931_E05_01_Einfach.xml", "EN 16931", "/Alternative"),
        ("zugferd_2p5_EXTENDED_X19_01_Warenrechnung.xml", "EXTENDED", "/Alternative"),
    ],
)
def test_attach_xml_profile_metadata(sample, level, relationship, empty_pdf16_bytes):
    samples = os.path.join(os.path.dirname(__file__), "samples")
    with open(os.path.join(samples, sample), "rb") as f:
        info = _attachment_info(attach_xml(empty_pdf16_bytes, f.read()))

    assert info["level"] == level
    assert info["relationship"] == relationship
    assert info["filename"] == info["file"] == "factur-x.xml"
    assert info["version"] == "1.0"


def test_attach_xml_xrechnung(empty_pdf16_bytes):
    samples = os.path.join(os.path.dirname(__file__), "samples")
    with open(os.path.join(samples, "zugferd_2p5_XRECHNUNG_Einfach.xml"), "rb") as f:
        info = _attachment_info(attach_xml(empty_pdf16_bytes, f.read()))

    assert info["level"] == "XRECHNUNG"
    assert info["relationship"] == "/Alternative"
    assert info["filename"] == info["file"] == "xrechnung.xml"
    assert info["version"] == "3p0"


@pytest.mark.parametrize(
    "level,expected",
    [("BASIC-WL", "BASIC WL"), ("basicwl", "BASIC WL"), ("EN16931", "EN 16931")],
)
def test_attach_xml_level_is_normalized(
    level, expected, invoice_document, empty_pdf16_bytes
):
    xml = invoice_document.serialize(schema="FACTUR-X_EXTENDED")
    info = _attachment_info(attach_xml(empty_pdf16_bytes, xml, level=level))

    assert info["level"] == expected


@pytest.mark.parametrize("guideline", ["urn:factur-x", "invalid"])
def test_attach_xml_invalid_guideline(guideline, invoice_document, empty_pdf16_bytes):
    invoice_document.context.guideline_parameter.id = guideline
    xml = invoice_document.serialize(schema="FACTUR-X_EXTENDED")

    with pytest.raises(ValueError):
        attach_xml(empty_pdf16_bytes, xml)
    with pytest.raises(ValueError):
        attach_xml(empty_pdf16_bytes, xml, level="COMFORT")


def test_attach_xml_keeps_higher_pdf_version(
    invoice_document, empty_pdf16_bytes, invoice_pdf17_bytes
):
    xml = invoice_document.serialize(schema="FACTUR-X_EXTENDED")

    assert _attachment_info(attach_xml(empty_pdf16_bytes, xml))["header"] == b"%PDF-1.6"
    assert (
        _attachment_info(attach_xml(invoice_pdf17_bytes, xml))["header"] == b"%PDF-1.7"
    )


def test_parse_does_not_modify_input():
    root = etree.fromstring(
        b'<ram:ID xmlns:ram="urn:un:unece:uncefact:data:standard:'
        b'ReusableAggregateBusinessInformationEntity:100">1</ram:ID>'
    )
    IDElement(NS_RAM, "ID").from_etree(root)

    assert dict(root.attrib) == {}


def test_direct_date_time_keeps_time():
    node = ET.Element("{x}DateTime")
    node.text = "2024-01-31T12:30:00"
    element = DirectDateTimeElement("x", "DateTime").from_etree(node)

    assert element._value == datetime(2024, 1, 31, 12, 30)
    assert ET.tostring(element.to_etree()) == ET.tostring(node)

    node.text = "31.01.2024"
    with pytest.raises(TypeError):
        DirectDateTimeElement("x", "DateTime").from_etree(node)
    assert (
        DirectDateTimeElement("x", "DateTime").from_etree(node, strict=False)._value
        is None
    )

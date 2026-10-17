import copy
import os
import pytest
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal

from drafthorse.models.document import Document
from drafthorse.models.party import TaxRegistration
from drafthorse.models.product import ProductClassification
from drafthorse.models.references import (
    LineAdditionalReferencedDocument,
    LineInvoiceReferencedDocument,
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
    doc = copy.deepcopy(invoice_document)
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
    doc = copy.deepcopy(invoice_document)
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
    doc = copy.deepcopy(invoice_document)
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

import copy
import pytest
import xml.etree.ElementTree as ET
from datetime import date

from drafthorse.models.document import Document
from drafthorse.models.product import ProductClassification
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

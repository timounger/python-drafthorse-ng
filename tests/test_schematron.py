import os
import pytest

from drafthorse.models.document import Document
from drafthorse.utils import SchematronError, validate_schematron

pytest.importorskip("saxonche")

samples = [
    f
    for f in os.listdir(os.path.join(os.path.dirname(__file__), "samples"))
    if f.startswith("zugferd_2p5_") and "_XRECHNUNG_" not in f
]


@pytest.mark.parametrize("filename", samples)
def test_sample_schematron(filename):
    with open(os.path.join(os.path.dirname(__file__), "samples", filename), "rb") as f:
        doc = Document.parse(f.read())
    schema = "FACTUR-X_" + filename.split("_")[2]

    doc.serialize(schema=schema, schematron=True)


@pytest.mark.parametrize("invoice_document", ["380"], indirect=True)
def test_schematron_finds_errors_the_xsd_does_not(invoice_document):
    doc = invoice_document
    # Valid against the XSD, but EXTENDED requires its own guideline ID
    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

    with pytest.raises(SchematronError) as exc_info:
        validate_schematron(xml, "FACTUR-X_EXTENDED")

    assert "FX-SCH-A-000636" in [e[0] for e in exc_info.value.errors]

    doc.context.guideline_parameter.id = (
        "urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended"
    )
    doc.serialize(schema="FACTUR-X_EXTENDED", schematron=True)


@pytest.mark.parametrize(
    "filename",
    [
        "zugferd_2p5_XRECHNUNG_Einfach.xml",
        "zugferd_2p5_XRECHNUNG_Elektron.xml",
        "zugferd_2p5_XRECHNUNG_Reisekostenabrechnung.xml",
    ],
)
def test_xrechnung_schematron(filename):
    with open(os.path.join(os.path.dirname(__file__), "samples", filename), "rb") as f:
        doc = Document.parse(f.read())

    # Since the KoSIT validator configuration 2026-08-31 the seller contact
    # must not have both a person and a department name (CII-SR-465), the
    # official ZUGFeRD 2.5.2 samples are older
    with pytest.raises(SchematronError) as exc_info:
        doc.serialize(schema="FACTUR-X_XRECHNUNG", schematron=True)
    assert [e[0] for e in exc_info.value.errors] == ["CII-SR-465"]

    del doc.trade.agreement.seller.contact.department_name
    doc.serialize(schema="FACTUR-X_XRECHNUNG", schematron=True)


def test_schematron_unknown_profile():
    with pytest.raises(ValueError):
        validate_schematron(b"<x/>", "FACTUR-X_COMFORT")

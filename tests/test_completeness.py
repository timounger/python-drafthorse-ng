import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from lxml import etree

from drafthorse.models import fields
from drafthorse.models.container import (
    Container,
    CurrencyContainer,
    IDContainer,
    StringContainer,
)
from drafthorse.models.document import Document

VALUES = {
    fields.IndicatorField: True,
    fields.DateTimeField: date(2024, 1, 31),
    fields.DateField: date(2024, 1, 31),
    fields.DecimalField: Decimal("1.00"),
    fields.QuantityField: (Decimal("1"), "C62"),
    fields.CurrencyField: (Decimal("1.00"), "EUR"),
    fields.IDField: ("0088", "ID1"),
    fields.AgencyIDField: ("6", "ID1"),
    fields.ClassificationField: ("TST", "1", "C1"),
    fields.BinaryObjectField: ("text/plain", "a.txt", "QQ=="),
    fields.CodeField: ("5153", "AAA"),
}


def fill(element):
    """Set every field of the element and add one entry to every container"""
    for field in type(element)._fields:
        obj = getattr(element, field.name)
        if isinstance(obj, StringContainer):
            obj.add("X")
        elif isinstance(obj, IDContainer):
            obj.add(("0088", "ID2"))
        elif isinstance(obj, CurrencyContainer):
            obj.add(("1.00", "USD"))
        elif isinstance(obj, Container):
            child = obj.child_type()
            fill(child)
            obj.add(child)
        elif type(field) is fields.Field:
            fill(obj)
        else:
            setattr(element, field.name, VALUES.get(type(field), "X"))


def pretty(xml):
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.tostring(etree.fromstring(xml, parser), pretty_print=True)


def test_every_field_is_valid_against_xsd_and_roundtrips():
    doc = Document()
    fill(doc)

    # Every element of the model at once must follow the XSD sequence
    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

    # Parsing must restore every field
    assert pretty(Document.parse(xml).serialize(schema=None)) == pretty(xml)


def test_fill_covers_all_fields():
    doc = Document()
    fill(doc)
    xml = ET.tostring(doc.to_etree())

    assert len(ET.fromstring(xml).findall(".//*")) > 1000

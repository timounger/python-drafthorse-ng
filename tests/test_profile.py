import os
import pytest
import xml.etree.ElementTree as ET

from drafthorse.models import NS_RAM, NS_RSM
from drafthorse.models import elements
from drafthorse.models.accounting import TradeAllowanceCharge
from drafthorse.models.container import (
    Container,
    CurrencyContainer,
    IDContainer,
)
from drafthorse.models.document import Document
from drafthorse.models.fields import Field
from drafthorse.models.party import ShipToTradeParty, SellerTradeParty
from drafthorse.models.tradelines import LineItem, LineSettlement

PREFIXES = {
    NS_RSM: "rsm",
    NS_RAM: "ram",
    "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100": "udt",
    "urn:un:unece:uncefact:data:standard:QualifiedDataType:100": "qdt",
}
ATTRIBUTES = [
    (elements.IDElement, "schemeID"),
    (elements.CurrencyElement, "currencyID"),
    (elements.QuantityElement, "unitCode"),
    (elements.ClassificationElement, "listID"),
    (elements.ClassificationElement, "listVersionID"),
    (elements.BinaryObjectElement, "mimeCode"),
    (elements.BinaryObjectElement, "filename"),
    (elements.CodeElement, "listID"),
]


def qualified(tag):
    namespace, name = tag[1:].split("}")
    return PREFIXES[namespace] + ":" + name


def model_paths(cls, path, paths):
    """Collect element paths and supported attributes of the model"""
    instance = cls()
    for field in cls._fields:
        obj = getattr(instance, field.name)
        sub_path = path + "/" + qualified(obj.get_tag())
        paths[sub_path] = paths.get(sub_path, set())
        if isinstance(obj, IDContainer):
            paths[sub_path].add("schemeID")
        elif isinstance(obj, CurrencyContainer):
            paths[sub_path].add("currencyID")
        elif isinstance(obj, Container):
            if issubclass(obj.child_type, elements.Element):
                model_paths(obj.child_type, sub_path, paths)
        elif isinstance(obj, elements.DateTimeElement):
            prefix = "udt" if "Unqualified" in obj._date_time_namespace else "qdt"
            paths[sub_path + "/" + prefix + ":" + obj._string_tag] = {"format"}
        elif isinstance(obj, elements.IndicatorElement):
            paths[sub_path + "/udt:Indicator"] = set()
        elif type(field) is Field:
            model_paths(type(obj), sub_path, paths)
        else:
            paths[sub_path].update(
                attr for element, attr in ATTRIBUTES if isinstance(obj, element)
            )
    return paths


@pytest.fixture(scope="module")
def profile():
    with open(
        os.path.join(
            os.path.dirname(__file__),
            "profiles",
            "Factur-X_1.09.2_EXTENDED_xpaths.txt",
        ),
        encoding="utf-8",
    ) as f:
        return [line.strip() for line in f if line.startswith("/")]


@pytest.fixture(scope="module")
def model():
    return model_paths(Document, "/rsm:CrossIndustryInvoice", {})


def test_model_contains_every_element_of_the_profile(profile, model):
    elements_of_profile = {p for p in profile if "/@" not in p}

    assert (
        sorted(elements_of_profile - set(model) - {"/rsm:CrossIndustryInvoice"}) == []
    )


def test_model_contains_no_element_unused_in_the_profile(profile, model):
    elements_of_profile = {p for p in profile if "/@" not in p}

    assert sorted(set(model) - elements_of_profile) == []


def test_model_supports_every_attribute_of_the_profile(profile, model):
    missing = []
    for path in profile:
        if "/@" in path:
            element, attribute = path.rsplit("/@", 1)
            if attribute not in model.get(element, set()):
                missing.append(path)

    assert missing == []


def test_unused_fields_are_removed_in_context():
    # Description is used for the seller, but not for ship to parties
    SellerTradeParty().description = "Text"
    with pytest.raises(AttributeError):
        ShipToTradeParty().description = "Text"
    with pytest.raises(AttributeError):
        LineSettlement().trade_tax.basis_amount = 1


def test_strict_parsing_rejects_unused_elements():
    li = LineItem()
    li.document.line_id = "1"
    li.product.name = "Produkt"
    li.settlement.trade_tax.type_code = "VAT"
    node = li.to_etree()
    tax = node.find(".//{%s}ApplicableTradeTax" % NS_RAM)
    basis = ET.SubElement(tax, "{%s}BasisAmount" % NS_RAM)
    basis.text = "1.00"

    with pytest.raises(TypeError):
        LineItem().from_etree(node)
    parsed = LineItem().from_etree(node, strict=False)
    assert parsed.settlement.trade_tax.type_code._text == "VAT"


def test_line_allowance_charge_requires_line_class():
    with pytest.raises(TypeError):
        LineSettlement().allowance_charge.add(TradeAllowanceCharge())

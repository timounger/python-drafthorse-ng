import logging
import os

logger = logging.getLogger("drafthorse")

# Schematron files per profile, XRECHNUNG uses the rules of EN 16931 and of
# the CIUS XRechnung like the KoSIT validator configuration
SCHEMATRON_FILES = {
    "MINIMUM": ["FACTUR-X_MINIMUM.xslt"],
    "BASIC-WL": ["FACTUR-X_BASIC-WL.xslt"],
    "BASIC": ["FACTUR-X_BASIC.xslt"],
    "EN16931": ["FACTUR-X_EN16931.xslt"],
    "EXTENDED": ["FACTUR-X_EXTENDED.xslt"],
    "XRECHNUNG": [
        "xrechnung/EN16931-CII-validation.xsl",
        "xrechnung/XRechnung-CII-validation.xsl",
    ],
}
# Severity levels overwritten by the KoSIT validator configuration
SCHEMATRON_LEVELS = {
    "XRECHNUNG": {
        "BR-CL-21": "warning",
        "BR-CL-23": "warning",
        "CII-SR-452": "error",
        "CII-SR-453": "error",
        "CII-SR-454": "error",
        "CII-SR-465": "error",
        "CII-SR-466": "error",
        "CII-SR-475": "information",
        "CII-SR-476": "information",
    }
}
SCHEMATRON_PROFILES = tuple(SCHEMATRON_FILES)
NS_SVRL = "http://purl.oclc.org/dsdl/svrl"

_saxon = {}


class SchematronError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(
            "Schematron validation failed:\n"
            + "\n".join("[{}] {}: {}".format(*e) for e in errors)
        )


def validate_xml(xmlout, schema):
    try:
        from lxml import etree
    except ImportError:
        logger.warning("Could not validate output as LXML is not installed.")
        return xmlout
    if schema is not None:
        if schema == "FACTUR-X_XRECHNUNG":
            schema = "Factur-X_1.09.2_XRECHNUNG_CrossIndustryInvoice_100pD16B"
        elif schema.startswith("FACTUR-X_"):
            schema = schema.replace("FACTUR-X_", "Factur-X_1.09.2_")
            schema = schema.replace("BASIC-WL", "BASICWL")
        schema = etree.XMLSchema(
            file=os.path.join(os.path.dirname(__file__), "schema", schema + ".xsd")
        )
    parser = etree.XMLParser(schema=schema)
    xml_root = etree.fromstring(xmlout, parser)

    return etree.tostring(
        xml_root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    )


def _schematron_executable(filename):
    from saxonche import PySaxonProcessor

    if "processor" not in _saxon:
        _saxon["processor"] = PySaxonProcessor(license=False)
    if filename not in _saxon:
        xslt = os.path.join(os.path.dirname(__file__), "schema", "schematron", filename)
        compiler = _saxon["processor"].new_xslt30_processor()
        _saxon[filename] = compiler.compile_stylesheet(stylesheet_file=xslt)
    return _saxon["processor"], _saxon[filename]


def validate_schematron(xmlout, schema):
    """
    Validate XML against the official Factur-X schematron rules
    (business rules and code lists), for XRECHNUNG against the rules of
    EN 16931 and the CIUS XRechnung. Requires the optional dependency
    saxonche, as the rules use XSLT/XPath 2.0.
    :param xmlout: ZUGFeRD XML
    :param schema: XML schema, e.g. ``FACTUR-X_EXTENDED``
    :return: list of warnings as (rule id, location, message)
    :raises SchematronError: if any rule with a level other than warning or
        information failed
    """
    from lxml import etree

    profile = schema.replace("FACTUR-X_", "")
    if profile not in SCHEMATRON_PROFILES:
        raise ValueError("No schematron available for schema {}".format(schema))
    if isinstance(xmlout, bytes):
        xmlout = xmlout.decode("utf-8")
    levels = SCHEMATRON_LEVELS.get(profile, {})

    errors, warnings = [], []
    for filename in SCHEMATRON_FILES[profile]:
        processor, executable = _schematron_executable(filename)
        report = executable.transform_to_string(
            xdm_node=processor.parse_xml(xml_text=xmlout)
        )
        for el in etree.fromstring(report.encode("utf-8")).iter(
            "{%s}failed-assert" % NS_SVRL, "{%s}successful-report" % NS_SVRL
        ):
            finding = (
                el.get("id") or "",
                el.get("location") or "",
                " ".join((el.findtext("{%s}text" % NS_SVRL) or "").split()),
            )
            if levels.get(finding[0], el.get("flag")) in ("warning", "information"):
                warnings.append(finding)
            else:
                errors.append(finding)
    if errors:
        raise SchematronError(errors)
    return warnings

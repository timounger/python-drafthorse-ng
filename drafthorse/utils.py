import logging
import os

logger = logging.getLogger("drafthorse")

SCHEMATRON_PROFILES = ("MINIMUM", "BASIC-WL", "BASIC", "EN16931", "EXTENDED")
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
        if schema.startswith("FACTUR-X_"):
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


def _schematron_executable(profile):
    from saxonche import PySaxonProcessor

    if "processor" not in _saxon:
        _saxon["processor"] = PySaxonProcessor(license=False)
    if profile not in _saxon:
        xslt = os.path.join(
            os.path.dirname(__file__),
            "schema",
            "schematron",
            "FACTUR-X_{}.xslt".format(profile),
        )
        compiler = _saxon["processor"].new_xslt30_processor()
        _saxon[profile] = compiler.compile_stylesheet(stylesheet_file=xslt)
    return _saxon["processor"], _saxon[profile]


def validate_schematron(xmlout, schema):
    """
    Validate XML against the official Factur-X schematron rules
    (business rules and code lists). Requires the optional dependency
    saxonche, as the rules use XSLT/XPath 2.0.
    :param xmlout: ZUGFeRD XML
    :param schema: XML schema, e.g. ``FACTUR-X_EXTENDED``
    :return: list of warnings as (rule id, location, message)
    :raises SchematronError: if any rule with flag other than warning failed
    """
    from lxml import etree

    profile = schema.replace("FACTUR-X_", "")
    if profile not in SCHEMATRON_PROFILES:
        raise ValueError("No schematron available for schema {}".format(schema))
    processor, executable = _schematron_executable(profile)
    if isinstance(xmlout, bytes):
        xmlout = xmlout.decode("utf-8")
    report = executable.transform_to_string(
        xdm_node=processor.parse_xml(xml_text=xmlout)
    )

    errors, warnings = [], []
    for el in etree.fromstring(report.encode("utf-8")).iter(
        "{%s}failed-assert" % NS_SVRL, "{%s}successful-report" % NS_SVRL
    ):
        finding = (
            el.get("id") or "",
            el.get("location") or "",
            " ".join((el.findtext("{%s}text" % NS_SVRL) or "").split()),
        )
        if el.get("flag") == "warning":
            warnings.append(finding)
        else:
            errors.append(finding)
    if errors:
        raise SchematronError(errors)
    return warnings

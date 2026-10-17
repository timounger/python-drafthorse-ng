.. highlight:: python

drafthorse-ng -- Basic ZUGFeRD implementation in Python
=======================================================

.. image:: https://github.com/timounger/python-drafthorse-ng/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/timounger/python-drafthorse-ng/actions/workflows/tests.yml

This is an unofficial, further developed fork of `drafthorse <https://github.com/pretix/python-drafthorse>`_
by pretix with support for ZUGFeRD 2.5.2. It is not affiliated with or endorsed by pretix. The changes
compared to drafthorse 2025.2.0 are listed in the ``CHANGELOG.rst``, some of them are backwards incompatible.

The import name is still ``drafthorse``, so existing code keeps working apart from the changes listed in the
changelog. Do not install ``drafthorse`` and ``drafthorse-ng`` at the same time, they overwrite each other.

Installation
------------

The package is not published on PyPI. Install it directly from GitHub, pinned to a release tag:

.. code-block:: bash

    pip install "drafthorse-ng @ git+https://github.com/timounger/python-drafthorse-ng.git@v1.0.1"

The same line can be used in a ``requirements.txt``.

This is a low-level python implementation of the ZUGFeRD XML format. ZUGFeRD is a German
format for sending digital invoices. ZUGFeRD XML files are to be attached to a PDF
file. This library can be used to generate or parse the contents of this XML file as well as
attach it to a PDF. We do not support parsing PDF files (for now).

By low-level, we mean that this library tries to model the ZUGFeRD data model 1:1 without any
further abstractions or simplifications. You can set and parse most parameters defined in ZUGFeRD
2.5.2 (Factur-X 1.09.2). To see which parameters are defined, please refer to the official ZUGFeRD specification,
there is no documentation for this library that reiterates it.

All output is validated against the official XSDs. Validation against the official schematron
(business rules of the profile levels) is available optionally, see below.

The profile level is detected automatically based on the XML data and added to the PDF metadata.

Usage
-----

Parsing::

    from drafthorse.models.document import Document
    samplexml = open("sample.xml", "rb").read()
    doc = Document.parse(samplexml)
    print(doc.trade.agreement.seller.name)

``Document.parse()`` taskes a boolean parameter ``strict`` which defaults to ``True``. This means that the parser will raise an error if it encounters any unknown element. If you set it to ``False``, the parser will not raise an error and parse whatever it can.

.. [[[cog
    # Re-run this with `cog -r README.rst`

    from pathlib import Path
    from textwrap import indent

    import cog

    cog.outl("Generating::\n")
    cog.outl(indent(Path("example.py").read_text(encoding="UTF-8"), "    "), dedent=False)
.. ]]]
Generating::

    from datetime import date, datetime, timedelta, timezone
    from decimal import Decimal

    from drafthorse.models.accounting import ApplicableTradeTax
    from drafthorse.models.document import Document
    from drafthorse.models.note import IncludedNote
    from drafthorse.models.party import TaxRegistration
    from drafthorse.models.payment import PaymentMeans, PaymentTerms
    from drafthorse.models.trade import AdvancePayment, IncludedTradeTax
    from drafthorse.models.tradelines import LineItem
    from drafthorse.pdf import attach_xml

    # Build data structure
    doc = Document()
    doc.context.guideline_parameter.id = "urn:cen.eu:en16931:2017"
    doc.header.id = "RE1337"
    doc.header.type_code = "380"
    doc.header.issue_date_time = date.today()

    doc.header.notes.add(IncludedNote(content="Test Note 1"))

    doc.trade.agreement.buyer.name = "Kunde GmbH"
    doc.trade.agreement.buyer.address.country_id = "DE"

    doc.trade.settlement.currency_code = "EUR"
    doc.trade.settlement.payment_means.add(PaymentMeans(type_code="ZZZ"))

    doc.trade.agreement.seller.name = "Lieferant GmbH"
    doc.trade.agreement.seller.address.country_id = "DE"
    doc.trade.agreement.seller.address.country_subdivision = "Bayern"
    doc.trade.agreement.seller.tax_registrations.add(
        TaxRegistration(id=("VA", "DE000000000"))
    )

    advance = AdvancePayment(
        received_date=datetime.now(timezone.utc), paid_amount=Decimal(42)
    )
    advance.included_trade_tax.add(
        IncludedTradeTax(
            calculated_amount=Decimal(0),
            type_code="VAT",
            category_code="E",
            rate_applicable_percent=Decimal(0),
        )
    )
    doc.trade.settlement.advance_payment.add(advance)

    li = LineItem()
    li.document.line_id = "1"
    li.product.name = "Rainbow"
    li.agreement.gross.amount = Decimal("1198.8")
    li.agreement.gross.basis_quantity = (Decimal("1.0000"), "C62")  # C62 == unit
    li.agreement.net.amount = Decimal("999")
    li.agreement.net.basis_quantity = (Decimal("1.0000"), "C62")  # C62 == unit
    li.delivery.billed_quantity = (Decimal("1.0000"), "C62")  # C62 == unit
    li.settlement.trade_tax.type_code = "VAT"
    li.settlement.trade_tax.category_code = "S"
    li.settlement.trade_tax.rate_applicable_percent = Decimal("20.00")
    li.settlement.monetary_summation.total_amount = Decimal("999.00")
    doc.trade.items.add(li)

    trade_tax = ApplicableTradeTax()
    trade_tax.calculated_amount = Decimal("199.80")
    trade_tax.basis_amount = Decimal("999.00")
    trade_tax.type_code = "VAT"
    trade_tax.category_code = "S"
    trade_tax.rate_applicable_percent = Decimal("20.00")
    doc.trade.settlement.trade_tax.add(trade_tax)

    doc.trade.settlement.monetary_summation.line_total = Decimal("999.00")
    doc.trade.settlement.monetary_summation.charge_total = Decimal("0.00")
    doc.trade.settlement.monetary_summation.allowance_total = Decimal("0.00")
    doc.trade.settlement.monetary_summation.tax_basis_total = Decimal("999.00")
    doc.trade.settlement.monetary_summation.tax_total = (Decimal("199.80"), "EUR")
    doc.trade.settlement.monetary_summation.grand_total = Decimal("1198.8")
    doc.trade.settlement.monetary_summation.due_amount = Decimal("1198.8")

    terms = PaymentTerms()
    terms.due = datetime.now(timezone.utc) + timedelta(days=30)
    doc.trade.settlement.terms.add(terms)

    # Generate XML file
    xml = doc.serialize(schema="FACTUR-X_EXTENDED")

.. [[[end]]]

    # Attach XML to an existing PDF.
    # Note that the existing PDF should be compliant to PDF/A-3!
    # You can validate this here: https://www.pdf-online.com/osa/validate.aspx
    with open("input.pdf", "rb") as original_file:
        new_pdf_bytes = attach_xml(original_file.read(), xml)

    with open("output.pdf", "wb") as f:
        f.write(new_pdf_bytes)

``Document.serialize()`` will validate the generated XML against the specified schema and raise an error if it is not valid. If you want to avoid validation, you can set the ``schema`` parameter to ``None``.

The XSDs only check the structure. To additionally check the business rules and code lists of the
official Factur-X schematron, install the optional dependency and pass ``schematron=True``:

.. code-block:: bash

    pip install "drafthorse-ng[schematron] @ git+https://github.com/timounger/python-drafthorse-ng.git@v1.0.1"

.. code-block:: python

    from drafthorse.utils import SchematronError

    try:
        xml = doc.serialize(schema="FACTUR-X_EXTENDED", schematron=True)
    except SchematronError as e:
        for rule_id, location, message in e.errors:
            print(rule_id, location, message)

Schematron rules are available for the profiles ``MINIMUM``, ``BASIC-WL``, ``BASIC``, ``EN16931``,
``EXTENDED`` and ``XRECHNUNG``. For ``XRECHNUNG``, the rules of EN 16931 and of the CIUS XRechnung
are applied in the combination of the official KoSIT validator configuration.
``drafthorse.utils.validate_schematron(xml, schema)`` can also be used on existing XML and returns
the list of warnings.

Development
-----------

To run the included tests:

.. code-block:: bash

    pip install -r requirements_dev.txt
    py.test tests

To automatically sort your Imports as required by CI:

.. code-block:: bash

    pip install isort
    isort -rc .

To validate files using mustang:

.. code-block:: bash

    git clone https://github.com/ZUGFeRD/mustangproject.git
    cd mustangproject
    git checkout core-2.9.0
    ./mvnw clean package
    java -jar Mustang-CLI/target/Mustang-CLI-2.7.4-SNAPSHOT.jar --action validate --source invoice.pdf

Security
--------

If you discover a security issue, please report it privately via
`GitHub <https://github.com/timounger/python-drafthorse-ng/security/advisories/new>`_ instead of opening a public issue.

Credits and License
-------------------

Maintainer of drafthorse-ng: Timo Unger

drafthorse was originally developed by Raphael Michel <michel@rami.io> and pretix. The copyright of the original
code remains with its authors.

License of the Python code: Apache License 2.0

The PDF handling (drafthorse/pdf.py) was originally based on the code of factur-x, Copyright 2016-2018, Alexis de Lattre <alexis.delattre@akretion.com>,
released under a BSD license.

The packages includes schemas and samples of the ZUGFeRD specification (.xsd and .xml files) which are owned by the *Forum für elektronische Rechnungen bei der AWV e.V („FeRD“)* and are released under a proprietary license that allows bundling them together with other software for free.
The schema files are renamed to shorter names, only their references to each other are adjusted.

The schematron rules for the profile XRECHNUNG (``drafthorse/schema/schematron/xrechnung``) are included unmodified:
the rules of EN 16931 are licensed under the European Union Public Licence (EUPL) 1.2, the rules of the CIUS XRechnung
by the KoSIT under the Apache License 2.0. See the ``README.txt`` in that directory for sources and versions.

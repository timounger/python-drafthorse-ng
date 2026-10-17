Changelog
=========

Unreleased
----------

Backwards incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``LineSummation.tax_total`` is now a currency field like the header tax total, as the Factur-X
  1.09.2 schematron requires the invoice currency as ``currencyID`` (BT-X-329). Assigning a number
  still works, the value is available as ``._amount`` instead of ``._value``.
* Line items use the new class ``LineInvoiceReferencedDocument`` for
  ``LineSettlement.invoice_referenced_document``. Adding an ``InvoiceReferencedDocument`` there
  raises a ``TypeError``.
* ``TradeAgreement.description`` was removed. ``ram:Description`` does not exist in
  ``ApplicableHeaderTradeAgreement`` in any schema, so setting it always produced invalid XML.
* ``attach_xml`` embeds the XML of the profile XRECHNUNG as ``xrechnung.xml`` with the XRechnung
  version in ``fx:Version``, as required by the specification. Invalid guideline IDs or levels raise
  ``ValueError``.
* When parsing, ``monetary_summation.tax_total`` now holds the first ``TaxTotalAmount`` and
  ``tax_total_other_currency`` only further ones. Previously all of them ended up in
  ``tax_total_other_currency`` and ``tax_total`` was always empty.
* The model only contains the elements of the Factur-X 1.09.2 EXTENDED profile in their context.
  Elements that passed the XSD but are "not used" according to the schematron were removed: setting
  them raises ``AttributeError``, strict parsing raises ``TypeError`` (use ``strict=False`` to skip
  them). Affected are:

  * ``description`` of all parties except seller, buyer, item seller and manufacturer
  * the address of the legal organization of line level parties and the manufacturer
  * ``basis_amount``, ``line_total_basis_amount``, ``allowance_charge_basis_amount`` and
    ``tax_point_date`` of the line level tax
  * ``description`` of the line level billing period
  * ``sequence_numeric``, ``basis_quantity`` and ``trade_tax`` of line level allowances and charges
  * all elements except ``issuer_assigned_id``, ``type_code`` and ``reference_type_code`` of the
    additional referenced document of the line settlement

* New classes for the line level, containers on line level only accept these:
  ``LineTradeAllowanceCharge`` (``LineSettlement.allowance_charge``), ``LineApplicableTradeTax``,
  ``LineBillingSpecifiedPeriod``, ``LineShipToTradeParty``, ``LineUltimateShipToTradeParty``,
  ``LineLegalOrganization`` and ``LineSettlementAdditionalReferencedDocument``.
* Elements the XSD allows only once are single fields instead of containers:
  ``TradeAllowanceCharge.trade_tax``, ``LineSettlement.invoice_referenced_document``,
  ``PaymentMeans.information``, ``PaymentTerms.partial_amount`` and
  ``MonetarySummation.tax_total_other_currency``. Set their values directly instead of using
  ``.add()``.
* A field redeclared in a subclass now replaces the inherited field in place instead of moving to
  the end. ``ReferencedDocument`` contains all elements in XSD order; subclasses remove the ones
  they do not use.
* ``serialize(schema="FACTUR-X_XRECHNUNG")`` validates against the XRechnung XSD (CII D16B).

Features
^^^^^^^^

* Updated the XSDs to ZUGFeRD 2.5.2 / Factur-X 1.09.2 and added the 61 official sample invoices of
  ZUGFeRD 2.5.2 to the tests.
* Optional validation against the official Factur-X schematron (business rules and code lists) for
  MINIMUM, BASIC WL, BASIC, EN16931 and EXTENDED: ``doc.serialize(schema=..., schematron=True)`` or
  ``drafthorse.utils.validate_schematron(xml, schema)``. Requires ``pip install drafthorse[schematron]``.
* Schematron validation for XRECHNUNG with the rules of EN 16931 (CEN 1.3.16, EUPL 1.2) and of the
  CIUS XRechnung 3.0.2 (KoSIT 2.6.0) like the KoSIT validator configuration 2026-08-31.
* ``attach_xml`` adds an sRGB output intent if the input PDF has none, as required for PDF/A.
* Business terms introduced in Factur-X 1.08 and 1.09 (EXTENDED):

  * BT-X-561 number of units per package (``LineDelivery.per_package_unit_quantity``)
  * BG-X-22 / BT-X-563 / BT-X-564 location of the delivery terms (``DeliveryTerms.location``)
  * BT-X-565 delivery terms on line level (``LineAgreement.delivery_terms``)
  * BG-X-90 deviating seller on line level (``LineAgreement.item_seller``)
  * BT-X-590 line tax total in accounting currency (``LineSummation.tax_total_other_currency``)
  * BT-177 / BT-193 non-VAT tax code with list ID (``reason_code = ("5153", "AAA")``)
  * BT-215 / BT-216 debited account (``PaymentMeans.payer_institution``,
    ``PayerFinancialAccount.account_name``)
  * BT-173 to BT-176, BT-X-591 / BT-X-592 VAT exemption reasons of allowances, charges and
    logistics charges
  * BG-34 third party payments (``TradeSettlement.financial_adjustment``)
  * BG-X-93 product manufacturer (``TradeProduct.manufacturer``)

* Further EXTENDED elements, so that every element path of the Factur-X 1.09.2 EXTENDED profile can
  be represented: sub lines (``LineDocument.parent_line_id``), type of contact, sales agent, buyer
  agent, buyer tax representative, quotation references on header and line level, seller order on
  line level, line references of delivery notes and invoices, reference type codes of contracts and
  additional documents, deviating payee per payment terms, included tax of the net price (B2C) and
  IDs of included products.
* Repeatable EXTENDED elements (e.g. several preceding invoices, BG-3) can be represented without
  breaking existing code: the single field is followed by a ``further_*`` container for further
  occurrences, e.g. ``settlement.further_invoice_referenced_documents``.
* New field types ``CodeField`` (code with optional list ID) and ``DateField`` (``udt:DateString``).

Bug fixes
^^^^^^^^^

* Parsing product classification codes converted them to ``Decimal``, so non-numeric codes failed
  and numeric codes lost leading zeros; ``listID`` and ``listVersionID`` are optional now.
* Several elements were serialized in an order not allowed by the XSD, so ``serialize()`` failed:
  fields of referenced documents before ``FormattedIssueDateTime``, the seller tax representative,
  receiving advice and delivery note on header level, the exemption reason code of included taxes,
  the ultimate customer order and the attachment of additional references on line level.
* ``TaxPointDate`` (BT-7) was written as ``udt:DateTimeString`` instead of ``udt:DateString``.
* Parsing failed with ``Unknown element`` for XML containing comments within elements.
* ``attach_xml`` wrote ``BASICWL`` instead of ``BASIC WL`` as conformance level and used the
  relationship ``Alternative`` instead of ``Data`` for BASIC WL.
* ``IDElement`` added an empty ``schemeID`` attribute to the parsed input.
* ``DirectDateTimeElement`` dropped the time when parsing and silently ignored invalid values.

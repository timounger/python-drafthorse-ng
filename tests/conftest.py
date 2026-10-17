import copy
import os
import pytest
from example import doc


@pytest.fixture
def invoice_document(request):
    # Tests modify the document, so each test gets its own copy
    return copy.deepcopy(doc)


@pytest.fixture
def empty_pdf16_bytes():
    pdf_file = open(
        os.path.join(os.path.dirname(__file__), "samples", "empty_pdf16.pdf"), "rb"
    ).read()

    return pdf_file


@pytest.fixture
def invoice_pdf17_bytes():
    pdf_file = open(
        os.path.join(os.path.dirname(__file__), "samples", "invoice_pdf17.pdf"),
        "rb",
    ).read()

    return pdf_file

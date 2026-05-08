import fitz


def extract_text_from_pdf(file_obj):
    """Extract plain text content from a PDF file object."""
    file_bytes = file_obj.read()
    pdf_document = fitz.open(stream=file_bytes, filetype='pdf')
    pages = []

    try:
        for page in pdf_document:
            pages.append(page.get_text('text'))
    finally:
        pdf_document.close()

    return '\n'.join(pages).strip()

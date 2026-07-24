import io
import unittest

from PyPDF2 import PdfWriter

from app import create_app


class UploadCurriculumPdfTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_upload_endpoint_accepts_multipart_form_data(self):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        pdf_buffer = io.BytesIO()
        writer.write(pdf_buffer)
        pdf_buffer.seek(0)

        response = self.client.post(
            "/api/mentor/curriculum/pdf",
            data={
                "mentor_id": "MTR001",
                "full_course_pdf": (pdf_buffer, "curriculum.pdf"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["mentor_id"], "MTR001")


if __name__ == "__main__":
    unittest.main()

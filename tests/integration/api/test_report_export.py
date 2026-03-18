from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestExportEndpoint:
    def test_returns_200_with_valid_file(self) -> None:
        response = client.post(
            "/public/report/export",
            files={"file": ("test.txt", "житель город\n".encode(), "text/plain")},
        )
        assert response.status_code == 200

    def test_response_content_type_is_xlsx(self) -> None:
        response = client.post(
            "/public/report/export",
            files={"file": ("test.txt", "город жители\n".encode(), "text/plain")},
        )
        ct = response.headers["content-type"]
        assert "spreadsheetml" in ct or "octet-stream" in ct

    def test_returns_400_for_non_txt_file(self) -> None:
        response = client.post(
            "/public/report/export",
            files={"file": ("bad.csv", b"some,data", "text/csv")},
        )
        assert response.status_code == 400

    def test_returns_400_for_empty_file(self) -> None:
        response = client.post(
            "/public/report/export",
            files={"file": ("empty.txt", b"", "text/plain")},
        )
        assert response.status_code == 400

    def test_multiline_file_processed(self) -> None:
        content = "жители города\nжителем\n".encode()
        response = client.post(
            "/public/report/export",
            files={"file": ("multi.txt", content, "text/plain")},
        )
        assert response.status_code == 200
        assert len(response.content) > 0

    def test_large_repeated_content(self) -> None:
        """Smoke test: ~500 lines should not crash or timeout."""
        lines = ("слово тест город\n" * 500).encode("utf-8")
        response = client.post(
            "/public/report/export",
            files={"file": ("big.txt", lines, "text/plain")},
        )
        assert response.status_code == 200

    def test_response_body_is_non_empty_binary(self) -> None:
        response = client.post(
            "/public/report/export",
            files={"file": ("test.txt", "тест\n".encode(), "text/plain")},
        )
        assert len(response.content) > 0

    def test_xlsx_binary_signature(self) -> None:
        """XLSX files begin with PK (zip header)."""
        response = client.post(
            "/public/report/export",
            files={"file": ("test.txt", "тест\n".encode(), "text/plain")},
        )
        assert response.content[:2] == b"PK"

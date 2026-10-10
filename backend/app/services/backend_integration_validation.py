
from backend.app.main import app


EXPECTED_ROUTES = {
    ("GET", "/"),
    ("GET", "/health"),

    ("POST", "/api/cases"),
    ("GET", "/api/cases"),
    ("GET", "/api/cases/{case_id}"),
    ("PUT", "/api/cases/{case_id}"),

    ("POST", "/api/cases/{case_id}/evidence"),
    ("GET", "/api/cases/{case_id}/evidence"),
    ("GET", "/api/cases/{case_id}/evidence/{evidence_id}"),

    ("POST", "/api/cases/{case_id}/investigations"),
    ("GET", "/api/cases/{case_id}/investigations"),
    ("GET", "/api/investigations/{investigation_id}"),
    ("POST", "/api/investigations/{investigation_id}/start"),
    ("GET", "/api/investigations/{investigation_id}/status"),
    ("GET", "/api/investigations/{investigation_id}/stages"),

    ("GET", "/api/investigations/{investigation_id}/results"),
    ("GET", "/api/investigations/{investigation_id}/results/{result_type}"),

    ("GET", "/api/investigations/{investigation_id}/graph"),
    ("GET", "/api/investigations/{investigation_id}/timeline"),

    ("GET", "/api/investigations/{investigation_id}/risk"),
    ("GET", "/api/investigations/{investigation_id}/recommendations"),

    ("GET", "/api/investigations/{investigation_id}/report"),
}


def validate_backend_routes():
    schema = app.openapi()
    actual_routes = set()

    for path, operations in schema["paths"].items():
        for method, operation in operations.items():
            if method.lower() in {
                "get", "post", "put", "patch", "delete"
            }:
                actual_routes.add((method.upper(), path))

    missing = EXPECTED_ROUTES - actual_routes

    if missing:
        details = "\n".join(
            f"  {method} {path}"
            for method, path in sorted(missing)
        )
        raise AssertionError(
            "Backend integration validation failed. Missing routes:\n"
            + details
        )

    print("BACKEND ROUTE VALIDATION: PASS")
    print("Expected routes found:", len(EXPECTED_ROUTES))
    print("Registered operations:", len(actual_routes))


if __name__ == "__main__":
    validate_backend_routes()

from forensic_engine.intelligence.enrichment_result import (
    create_enrichment_result,
    validate_enrichment_result,
)


def main():
    enrichment = {
        "provider": "LOCAL",
        "status": "FOUND",
        "data": {
            "verdict": "TEST-NET",
            "confidence": "HIGH",
            "source": "control-dataset",
        },
    }

    result = create_enrichment_result(
        ioc_type="IPV4",
        value="192.0.2.1",
        enrichment=enrichment,
        source_artifact="test_artifact.eml",
        source_location="body",
    )

    print("Result:")
    print(result)

    print("\nValidation:")
    print(validate_enrichment_result(result))


if __name__ == "__main__":
    main()
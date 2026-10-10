from pathlib import Path

import cv2


def decode_qr(image_path):
    """
    TRACEWEAVE Phase 10.2
    Robust QR decoding with multiple decoding attempts.
    """

    image_path = Path(image_path).resolve()

    if not image_path.is_file():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = cv2.imread(str(image_path))

    if image is None:
        return {
            "status": "FAILED",
            "payload": None,
            "method": None,
            "error": "Unable to read image"
        }

    detector = cv2.QRCodeDetector()

    attempts = []

    # ---------------------------------------------------------
    # Attempt 1 — Original image
    # ---------------------------------------------------------

    payload, points, _ = detector.detectAndDecode(image)

    attempts.append("original")

    if payload:
        return {
            "status": "SUCCESS",
            "payload": payload,
            "method": "original",
            "attempts": attempts,
            "error": None
        }

    # ---------------------------------------------------------
    # Attempt 2 — Grayscale
    # ---------------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    payload, points, _ = detector.detectAndDecode(gray)

    attempts.append("grayscale")

    if payload:
        return {
            "status": "SUCCESS",
            "payload": payload,
            "method": "grayscale",
            "attempts": attempts,
            "error": None
        }

    # ---------------------------------------------------------
    # Attempt 3 — Otsu threshold
    # ---------------------------------------------------------

    _, threshold = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    payload, points, _ = detector.detectAndDecode(
        threshold
    )

    attempts.append("otsu_threshold")

    if payload:
        return {
            "status": "SUCCESS",
            "payload": payload,
            "method": "otsu_threshold",
            "attempts": attempts,
            "error": None
        }

    # ---------------------------------------------------------
    # Attempt 4 — Upscaling
    # ---------------------------------------------------------

    enlarged = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    payload, points, _ = detector.detectAndDecode(
        enlarged
    )

    attempts.append("upscaled_grayscale")

    if payload:
        return {
            "status": "SUCCESS",
            "payload": payload,
            "method": "upscaled_grayscale",
            "attempts": attempts,
            "error": None
        }

    # ---------------------------------------------------------
    # All attempts failed
    # ---------------------------------------------------------

    return {
        "status": "FAILED",
        "payload": None,
        "method": None,
        "attempts": attempts,
        "error": "QR detected/processed but payload could not be decoded"
    }


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE Phase 10.2 QR Decoder"
    )

    parser.add_argument(
        "input",
        help="Path to QR/image artifact"
    )

    args = parser.parse_args()

    result = decode_qr(args.input)

    print()
    print("=" * 60)
    print("TRACEWEAVE - PHASE 10.2 QR DECODER")
    print("=" * 60)

    print(f"Artifact : {args.input}")
    print(f"Status   : {result['status']}")
    print(f"Method   : {result['method']}")
    print(f"Payload  : {result['payload']}")
    print(f"Attempts : {', '.join(result['attempts'])}")

    if result["error"]:
        print(f"Error    : {result['error']}")

    print("=" * 60)
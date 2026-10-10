from pathlib import Path

import cv2


def detect_qr(image_path):
    """
    Detect QR codes in an image.

    Returns a structured detection result without
    performing URL or threat-intelligence analysis.
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
            "qr_detected": False,
            "count": 0,
            "detections": [],
            "error": "Unable to read image"
        }

    detector = cv2.QRCodeDetector()

    detections = []

    # ---------------------------------------------------------
    # Multi-QR detection
    # ---------------------------------------------------------

    try:
        success, decoded_info, points, _ = (
            detector.detectAndDecodeMulti(image)
        )

        if success and points is not None:

            for index, payload in enumerate(decoded_info):

                detection = {
                    "index": index + 1,
                    "decoded": bool(payload),
                    "payload": payload if payload else None,
                    "points": (
                        points[index].tolist()
                        if index < len(points)
                        else None
                    )
                }

                detections.append(detection)

    except Exception:
        pass

    # ---------------------------------------------------------
    # Single QR fallback
    # ---------------------------------------------------------

    if not detections:

        try:
            payload, points, _ = detector.detectAndDecode(image)

            if points is not None:

                detections.append({
                    "index": 1,
                    "decoded": bool(payload),
                    "payload": payload if payload else None,
                    "points": points.tolist()
                })

        except Exception as exc:

            return {
                "status": "FAILED",
                "qr_detected": False,
                "count": 0,
                "detections": [],
                "error": str(exc)
            }

    return {
        "status": "SUCCESS",
        "qr_detected": len(detections) > 0,
        "count": len(detections),
        "detections": detections,
        "error": None
    }
if __name__ == "__main__":

    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="TRACEWEAVE Phase 10 QR Detector"
    )

    parser.add_argument(
        "input",
        help="Path to QR/image artifact"
    )

    args = parser.parse_args()

    result = detect_qr(args.input)

    print()
    print("=" * 60)
    print("TRACEWEAVE - PHASE 10 QR DETECTION")
    print("=" * 60)

    print(
        f"Artifact      : {args.input}"
    )

    print(
        f"Status        : {result['status']}"
    )

    print(
        f"QR detected   : {result['qr_detected']}"
    )

    print(
        f"QR count      : {result['count']}"
    )

    if result["detections"]:

        for detection in result["detections"]:

            print()
            print(
                f"QR #{detection['index']}"
            )

            print(
                f"Decoded       : "
                f"{detection['decoded']}"
            )

            print(
                f"Payload       : "
                f"{detection['payload']}"
            )

    if result["error"]:
        print(
            f"Error         : {result['error']}"
        )

    print("=" * 60)
from pathlib import Path
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from urllib.parse import urlparse
import argparse
import hashlib
import json
import re
import sys


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# URL extraction
# ---------------------------------------------------------

URL_PATTERN = re.compile(
    r'https?://[^\s<>"\'\]\[()]+',
    re.IGNORECASE
)


def clean_url(url: str) -> str:
    """
    Remove punctuation that commonly appears immediately
    after a URL in email text.
    """

    return url.rstrip(".,;:!?)]}>")


def extract_urls(text: str) -> list[str]:
    """
    Extract HTTP/HTTPS URLs from text.
    """

    if not text:
        return []

    matches = URL_PATTERN.findall(text)

    cleaned = []

    for url in matches:
        url = clean_url(url)

        if url not in cleaned:
            cleaned.append(url)

    return cleaned


# ---------------------------------------------------------
# Address parsing
# ---------------------------------------------------------

def extract_addresses(header_value: str | None) -> list[dict]:
    """
    Parse email addresses from From/To/CC/BCC headers.
    """

    if not header_value:
        return []

    addresses = getaddresses([header_value])

    result = []

    for name, address in addresses:
        if not address:
            continue

        result.append({
            "name": name,
            "address": address
        })

    return result


# ---------------------------------------------------------
# Date parsing
# ---------------------------------------------------------

def normalize_email_date(date_value: str | None) -> str | None:
    """
    Convert the email Date header into ISO 8601 format.
    """

    if not date_value:
        return None

    try:
        parsed = parsedate_to_datetime(date_value)

        if parsed is None:
            return None

        return parsed.isoformat()

    except (TypeError, ValueError, OverflowError):
        return None


# ---------------------------------------------------------
# Header extraction
# ---------------------------------------------------------

def extract_headers(message) -> list[dict]:
    """
    Preserve all email headers.

    Duplicate headers are intentionally retained because
    duplicate headers can be relevant during forensic analysis.
    """

    headers = []

    for name, value in message.raw_items():
        headers.append({
            "name": name,
            "value": value
        })

    return headers


# ---------------------------------------------------------
# Body extraction
# ---------------------------------------------------------

def extract_bodies(message) -> dict:
    """
    Extract plain-text and HTML email bodies.

    Attachments are not extracted here.
    """

    plain_text_parts = []
    html_parts = []

    if message.is_multipart():

        for part in message.walk():

            content_disposition = (
                part.get_content_disposition()
            )

            # Skip attachment bodies for now.
            if content_disposition == "attachment":
                continue

            content_type = part.get_content_type()

            if content_type == "text/plain":

                try:
                    content = part.get_content()

                except Exception:
                    try:
                        payload = part.get_payload(
                            decode=True
                        )

                        charset = (
                            part.get_content_charset()
                            or "utf-8"
                        )

                        content = payload.decode(
                            charset,
                            errors="replace"
                        ) if payload else ""

                    except Exception:
                        content = ""

                if content:
                    plain_text_parts.append(content)

            elif content_type == "text/html":

                try:
                    content = part.get_content()

                except Exception:
                    try:
                        payload = part.get_payload(
                            decode=True
                        )

                        charset = (
                            part.get_content_charset()
                            or "utf-8"
                        )

                        content = payload.decode(
                            charset,
                            errors="replace"
                        ) if payload else ""

                    except Exception:
                        content = ""

                if content:
                    html_parts.append(content)

    else:

        content_type = message.get_content_type()

        try:
            content = message.get_content()

        except Exception:
            try:
                payload = message.get_payload(
                    decode=True
                )

                charset = (
                    message.get_content_charset()
                    or "utf-8"
                )

                content = payload.decode(
                    charset,
                    errors="replace"
                ) if payload else ""

            except Exception:
                content = ""

        if content_type == "text/plain":
            plain_text_parts.append(content)

        elif content_type == "text/html":
            html_parts.append(content)

    return {
        "plain_text": "\n".join(plain_text_parts),
        "html": "\n".join(html_parts)
    }


# ---------------------------------------------------------
# Attachment metadata
# ---------------------------------------------------------

def calculate_bytes_sha256(data: bytes) -> str:
    """
    Calculate SHA-256 for in-memory attachment data.
    """

    return hashlib.sha256(data).hexdigest()


def extract_attachment_metadata(message) -> list[dict]:
    """
    Identify email attachments and embedded MIME objects.

    This phase records metadata only.
    Actual extraction to disk is handled separately.
    """

    attachments = []

    for index, part in enumerate(message.walk()):

        content_disposition = (
            part.get_content_disposition()
        )

        filename = part.get_filename()

        content_type = part.get_content_type()

        is_attachment = (
            content_disposition == "attachment"
            or filename is not None
        )

        if not is_attachment:
            continue

        try:
            payload = part.get_payload(
                decode=True
            )

            if payload is None:
                payload = b""

        except Exception:
            payload = b""

        attachments.append({
            "attachment_index": index,
            "filename": filename,
            "content_type": content_type,
            "content_disposition": content_disposition,
            "size_bytes": len(payload),
            "sha256": calculate_bytes_sha256(payload),
            "content_id": part.get("Content-ID"),
        })

    return attachments


# ---------------------------------------------------------
# Embedded MIME object detection
# ---------------------------------------------------------

def extract_embedded_objects(message) -> list[dict]:
    """
    Identify inline MIME objects such as inline images.

    The actual files are not extracted at this stage.
    """

    objects = []

    for index, part in enumerate(message.walk()):

        content_disposition = (
            part.get_content_disposition()
        )

        content_id = part.get("Content-ID")

        content_type = part.get_content_type()

        if (
            content_disposition == "inline"
            and (
                content_id
                or content_type.startswith("image/")
            )
        ):

            try:
                payload = part.get_payload(
                    decode=True
                )

                if payload is None:
                    payload = b""

            except Exception:
                payload = b""

            objects.append({
                "object_index": index,
                "content_type": content_type,
                "content_id": content_id,
                "filename": part.get_filename(),
                "size_bytes": len(payload),
                "sha256": calculate_bytes_sha256(payload)
            })

    return objects


# ---------------------------------------------------------
# URL details
# ---------------------------------------------------------

def build_url_records(urls: list[str]) -> list[dict]:
    """
    Convert extracted URLs into structured URL records.
    """

    records = []

    for url in urls:

        try:
            parsed = urlparse(url)

            records.append({
                "url": url,
                "scheme": parsed.scheme,
                "domain": parsed.hostname,
                "port": parsed.port,
                "path": parsed.path,
                "query": parsed.query,
                "fragment": parsed.fragment
            })

        except ValueError:

            records.append({
                "url": url,
                "scheme": None,
                "domain": None,
                "port": None,
                "path": None,
                "query": None,
                "fragment": None
            })

    return records


# ---------------------------------------------------------
# Main parser
# ---------------------------------------------------------

def parse_email(file_path: str | Path) -> dict:
    """
    Parse a complete EML file into structured forensic data.
    """

    path = Path(file_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(
            f"Email file not found: {path}"
        )

    with path.open("rb") as file:
        message = BytesParser(
            policy=policy.default
        ).parse(file)

    headers = extract_headers(message)

    bodies = extract_bodies(message)

    sender = extract_addresses(
        message.get("From")
    )

    recipients = extract_addresses(
        message.get("To")
    )

    cc = extract_addresses(
        message.get("Cc")
    )

    bcc = extract_addresses(
        message.get("Bcc")
    )

    urls = []

    urls.extend(
        extract_urls(
            bodies["plain_text"]
        )
    )

    urls.extend(
        extract_urls(
            bodies["html"]
        )
    )

    # Remove duplicates while preserving order.
    unique_urls = []

    for url in urls:
        if url not in unique_urls:
            unique_urls.append(url)

    attachments = extract_attachment_metadata(
        message
    )

    embedded_objects = extract_embedded_objects(
        message
    )

    return {
        "parser": {
            "name": "TRACEWEAVE EML Parser",
            "version": "1.0"
        },

        "source": {
            "filename": path.name,
            "path": str(path)
        },

        "email": {
            "from": sender,
            "to": recipients,
            "cc": cc,
            "bcc": bcc,
            "subject": message.get("Subject"),
            "date_raw": message.get("Date"),
            "date_normalized": normalize_email_date(
                message.get("Date")
            ),
            "message_id": message.get("Message-ID"),
            "reply_to": message.get("Reply-To"),
            "return_path": message.get("Return-Path"),
        },

        "headers": headers,

        "body": {
            "plain_text": bodies["plain_text"],
            "html": bodies["html"]
        },

        "urls": build_url_records(
            unique_urls
        ),

        "attachments": attachments,

        "embedded_objects": embedded_objects,

        "analysis_summary": {
            "url_count": len(unique_urls),
            "attachment_count": len(attachments),
            "embedded_object_count": len(
                embedded_objects
            )
        }
    }


# ---------------------------------------------------------
# JSON output
# ---------------------------------------------------------

def save_result(
    result: dict,
    output_path: str | Path
) -> None:

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )


# ---------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "TRACEWEAVE Phase 8B - "
            "EML Forensic Analysis"
        )
    )

    parser.add_argument(
        "email",
        help="Path to the .eml evidence file"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Path for JSON analysis output"
    )

    args = parser.parse_args()

    try:

        result = parse_email(
            args.email
        )

        print("\n========================================")
        print(" TRACEWEAVE - EMAIL FORENSIC ANALYSIS")
        print("========================================")

        email = result["email"]

        print(
            f"File           : "
            f"{result['source']['filename']}"
        )

        print(
            f"From           : "
            f"{email['from']}"
        )

        print(
            f"To             : "
            f"{email['to']}"
        )

        print(
            f"Subject        : "
            f"{email['subject']}"
        )

        print(
            f"Date           : "
            f"{email['date_normalized']}"
        )

        print(
            f"Message-ID     : "
            f"{email['message_id']}"
        )

        print(
            f"URLs found     : "
            f"{result['analysis_summary']['url_count']}"
        )

        print(
            f"Attachments    : "
            f"{result['analysis_summary']['attachment_count']}"
        )

        print(
            f"Embedded objs  : "
            f"{result['analysis_summary']['embedded_object_count']}"
        )

        print("========================================")

        if args.output:

            save_result(
                result,
                args.output
            )

            print(
                f"\nJSON result: "
                f"{Path(args.output).resolve()}"
            )

        print()

    except Exception as error:

        print(
            f"\n[ERROR] Email analysis failed: {error}",
            file=sys.stderr
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
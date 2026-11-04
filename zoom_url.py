from urllib.parse import urlsplit


def validate_zoom_meeting_url(value: str) -> str:
    """Accept HTTPS Zoom meeting links without exposing their password in logs."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A Zoom meeting URL is required.")

    url = value.strip()
    try:
        parsed = urlsplit(url)
        hostname = (parsed.hostname or "").lower().rstrip(".")
        # Accessing port validates malformed port values even though Zoom links
        # normally do not specify one.
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("The Zoom meeting URL is malformed.") from exc

    is_zoom_host = hostname == "zoom.us" or hostname.endswith(".zoom.us")
    if parsed.scheme != "https" or not is_zoom_host or parsed.username or parsed.password:
        raise ValueError("Use an HTTPS Zoom meeting link from zoom.us.")
    if not parsed.path or parsed.path == "/":
        raise ValueError("The Zoom URL must include a meeting link path.")

    return url

import argparse
import asyncio
import json
import os
import uuid

from dotenv import load_dotenv
from livekit import api

from zoom_url import validate_zoom_meeting_url

AGENT_NAME = "zoom-bot"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Invite the LemonSlice avatar into a Zoom meeting."
    )
    parser.add_argument("meeting_url", help="HTTPS Zoom meeting link, including its passcode")
    parser.add_argument("--bot-name", default="Lil Spark", help="Name shown in the Zoom participant list")
    parser.add_argument(
        "--no-meeting-chat",
        action="store_true",
        help="Do not send Zoom chat messages to the agent",
    )
    return parser.parse_args()


async def dispatch(meeting_url: str, bot_name: str, listen_to_meeting_chat: bool) -> None:
    load_dotenv()
    missing = [
        name
        for name in ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(f"Set these LiveKit settings in .env: {', '.join(missing)}")

    room_name = f"lemonslice-zoom-{uuid.uuid4().hex[:12]}"
    metadata = json.dumps(
        {
            "meeting_url": meeting_url,
            "bot_name": bot_name,
            "listen_to_meeting_chat": listen_to_meeting_chat,
        },
        separators=(",", ":"),
    )

    async with api.LiveKitAPI() as lkapi:
        result = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=AGENT_NAME,
                room=room_name,
                metadata=metadata,
            )
        )

    print(f"Dispatched {result.agent_name} to LiveKit room {result.room}.")
    print("The LemonSlice avatar will join the Zoom meeting shortly.")


def main() -> None:
    args = parse_args()
    meeting_url = validate_zoom_meeting_url(args.meeting_url)
    bot_name = args.bot_name.strip()
    if not bot_name:
        raise SystemExit("--bot-name cannot be empty.")

    asyncio.run(dispatch(meeting_url, bot_name, not args.no_meeting_chat))


if __name__ == "__main__":
    main()

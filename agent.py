import json
import os

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    TurnHandlingOptions,
    inference,
    utils,
)
from livekit.plugins import fishaudio, lemonslice

from zoom_url import validate_zoom_meeting_url

load_dotenv()

AGENT_NAME = "zoom-bot"
FISH_AUDIO_VOICE_ID = "b3d59ac5857a4506ae99be06205f10fe"
server = AgentServer()


def create_avatar() -> lemonslice.AvatarSession:
    if not os.getenv("LEMONSLICE_API_KEY"):
        raise RuntimeError("Set LEMONSLICE_API_KEY in .env.")

    image_url = os.getenv("LEMONSLICE_IMAGE_URL", "").strip()
    if not image_url:
        raise RuntimeError("Set LEMONSLICE_IMAGE_URL in .env.")

    return lemonslice.AvatarSession(
        agent_image_url=image_url,
        agent_prompt=(
            "Lil Spark speaks with bright, confident energy and a playful, friendly "
            "expression. Use natural speech movement, direct eye contact, and small "
            "expressive gestures. Keep his movements relaxed and clear, never frantic "
            "or exaggerated. When the conversation becomes serious, soften his "
            "expression and gestures while staying warm and attentive."
        ),
        agent_idle_prompt=(
            "Lil Spark rests in a relaxed, attentive pose with a calm, confident "
            "expression. Use subtle natural breathing and occasional blinking. Keep "
            "his posture open and welcoming, with only small, gentle movements."
        ),
    )


def create_tts() -> fishaudio.TTS:
    if not os.getenv("FISH_API_KEY"):
        raise RuntimeError("Set FISH_API_KEY in .env and in the LiveKit Cloud agent secrets.")

    return fishaudio.TTS(
        model="s2.1-pro",
        voice_id=FISH_AUDIO_VOICE_ID,
    )


def read_job_metadata(raw_metadata: str | None) -> dict:
    try:
        metadata = json.loads(raw_metadata) if raw_metadata else {}
    except json.JSONDecodeError as exc:
        raise ValueError("Agent job metadata must be valid JSON.") from exc

    if not isinstance(metadata, dict):
        raise ValueError("Agent job metadata must be a JSON object.")

    meeting_url = validate_zoom_meeting_url(metadata.get("meeting_url", ""))
    metadata["meeting_url"] = meeting_url

    bot_name = metadata.get("bot_name", "Lil Spark")
    if not isinstance(bot_name, str) or not bot_name.strip():
        raise ValueError("bot_name must be a non-empty string.")
    metadata["bot_name"] = bot_name.strip()

    listen_to_meeting_chat = metadata.get("listen_to_meeting_chat", True)
    if not isinstance(listen_to_meeting_chat, bool):
        raise ValueError("listen_to_meeting_chat must be true or false.")
    metadata["listen_to_meeting_chat"] = listen_to_meeting_chat
    return metadata


@server.rtc_session(agent_name=AGENT_NAME)
async def entrypoint(ctx: agents.JobContext) -> None:
    metadata = read_job_metadata(ctx.job.metadata)
    await ctx.connect()

    session = AgentSession(
        stt=inference.STT(
            model="assemblyai/universal-3-6-pro",
            language="en",
        ),
        llm=inference.LLM(model="google/gemma-4-31b-it"),
        tts=create_tts(),
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            interruption={"mode": "adaptive"},
        ),
    )
    avatar = create_avatar()

    await avatar.start(session, room=ctx.room)
    await avatar.join_meeting(
        metadata["meeting_url"],
        bot_name=metadata["bot_name"],
        listen_to_meeting_chat=metadata["listen_to_meeting_chat"],
    )

    agent = Agent(
        instructions=(
            "You are Lil Spark, a bold, playful digital character with a loyal heart "
            "and sharp, kind wit. You bring confidence, laughter, and light while "
            "staying true to yourself. Speak naturally in clear, simple language; use "
            "short conversational turns and clever, gentle humour when it fits. Be "
            "energetic and mischievous in harmless ways, but never cruel, pushy, or "
            "dismissive. When someone is upset or asks for calm, acknowledge their "
            "feelings and soften your tone before responding. Respect boundaries and "
            "individuality. Avoid baby talk, forced jokes, corporate language, and "
            "repeated catchphrases. Don't invent personal memories, relationships, or "
            "real-world actions. If you don't know something, say so honestly."
        ),
    )
    await session.start(
        agent=agent,
        room=ctx.room,
        room_options=avatar.room_options(),
    )

    # Wait for the avatar participant to arrive before it speaks.
    await utils.wait_for_agent(ctx.room)
    await session.generate_reply(
        instructions=(
            "Introduce yourself briefly as Lil Spark and offer to help the meeting."
        ),
    )


if __name__ == "__main__":
    agents.cli.run_app(server)

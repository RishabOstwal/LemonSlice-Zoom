# LemonSlice in Zoom

This starter runs a LemonSlice voice avatar as a participant in a Zoom meeting. It uses LiveKit Agents for the voice agent and LemonSlice's meeting relay to send and receive meeting audio and avatar video.

## You need

- Python 3.10 to 3.12 and [uv](https://docs.astral.sh/uv/)
- The [LiveKit CLI](https://docs.livekit.io/reference/developer-tools/livekit-cli/)
- A LiveKit Cloud project with its URL, API key, and API secret
- A LemonSlice API key; the public Lil Spark image URL is included in `.env.example`
- An ElevenLabs API key for the Lil Spark voice selected in LemonSlice

The agent uses LiveKit Inference for speech recognition and language generation. LemonSlice animates the configured TTS audio; this self-managed integration uses Lil Spark's ElevenLabs voice ID from the LemonSlice dashboard, at the configured 0.94x speed. It requires `ELEVEN_API_KEY` from an ElevenLabs account that can access that voice.

## Set up

In Command Prompt, copy `.env.example` to `.env`, then fill in the LiveKit, LemonSlice, and ElevenLabs credentials. The avatar image URL, voice ID, and Lil Spark's animation/personality prompts are configured from the LemonSlice profile.

```cmd
copy .env.example .env
uv sync
```

## Invite LemonSlice to a Zoom meeting

In one terminal, start the worker with the LiveKit CLI:

```cmd
lk agent dev
```

In another window, pass the Zoom invite link. Keep the link in quotes, especially when it contains a `pwd` query parameter.

```cmd
uv run python dispatch.py "https://us05web.zoom.us/j/12345678901?pwd=your-passcode" --bot-name "Lil Spark"
```

The meeting link is sent to the agent as dispatch metadata and used by LemonSlice to join. Lil Spark listens and responds to the meeting. By default, Zoom chat messages are also sent to the agent; disable that with `--no-meeting-chat`.

If Zoom places the bot in the waiting room, the host needs to admit it. The avatar leaves when its agent session ends; you can also remove it from the Zoom participant list.

## Customize

- Change the default spoken behavior in `agent.py`.
- Change the Zoom participant name with `--bot-name`.
- The agent uses the supplied public image URL and Lil Spark prompts; it does not use the hosted `agent_id` path.

For a deployed agent, add `ELEVEN_API_KEY` to its LiveKit Cloud secrets. Keep it out of source control and do not paste it into chat. The agent keeps LiveKit Inference for STT and the LLM; LemonSlice's self-managed avatar integration receives generated TTS audio and renders the avatar video.

To update an existing LiveKit Cloud deployment, copy `.env.cloud.example` to `.env.cloud`, add the ElevenLabs key, then run:

```cmd
lk agent update-secrets --secrets-file .env.cloud
lk agent deploy
```

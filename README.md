# LemonSlice in Zoom

This starter runs a LemonSlice voice avatar as a participant in a Zoom meeting. It uses LiveKit Agents for the voice agent and LemonSlice's meeting relay to send and receive meeting audio and avatar video.

## You need

- Python 3.10 to 3.12 and [uv](https://docs.astral.sh/uv/)
- The [LiveKit CLI](https://docs.livekit.io/reference/developer-tools/livekit-cli/)
- A LiveKit Cloud project with its URL, API key, and API secret
- A LemonSlice API key; the public Lil Spark image URL is included in `.env.example`
- A Fish Audio API key (`FISH_API_KEY`) for speech generation

The agent uses LiveKit Inference for speech recognition and language generation, Fish Audio (`s2.1-pro`) for speech, and LemonSlice to animate that speech. The Fish Audio voice ID is configured in `agent.py`.

## Set up

In Command Prompt, copy `.env.example` to `.env`, then set the LiveKit, LemonSlice, and Fish Audio credentials. The agent requires `LEMONSLICE_API_KEY`, `LEMONSLICE_IMAGE_URL`, and `FISH_API_KEY`; LiveKit connection values are also required for local development. The avatar image URL and Lil Spark's animation/personality prompts are configured from the LemonSlice profile.

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
- LemonSlice publishes the avatar as portrait video (368×560). A landscape Zoom layout may show blurred side fill around it. This project does not expose a landscape output setting; changing the source image or prompts will not change the video aspect ratio. Removing the side fill requires landscape output or compositing support in the avatar/meeting video path.

For a deployed agent, configure `FISH_API_KEY`, `LEMONSLICE_API_KEY`, and `LEMONSLICE_IMAGE_URL` in the LiveKit Cloud agent secrets. Keep credentials out of source control and chat. LiveKit Inference handles STT and the LLM; LemonSlice receives generated TTS audio and renders the avatar video.

After changing the deployed agent or its secrets, update the LiveKit Cloud agent and deploy a new version from this repository:

```cmd
lk agent deploy
```

# Voice memo to requirements

**My question:** Which transcription errors change the requirements? My next step is to record the fictional script; there isn't a recording or transcript here yet.

## What I need

My own recording, two transcription tools and one text model for extracting requirements. Set `TRANSCRIBER_A_MODEL`, `TRANSCRIBER_B_MODEL` and `LLM_MODEL` to the displayed models. If a model is hidden, use an explicit label such as `unknown-model-in-tool-name` and record the tool version. Read the [scoring guide](scoring.md) first.

## Steps

1. Copy the inputs and blank forms:

```sh
uv run python -m scripts.prepare kit voice-requirements --out runs/voice
```

2. Record `inputs/reading.txt` in my normal voice as `runs/voice/memo.wav`. Note microphone, room conditions and tool settings in the run record. Listen back and correct `runs/voice/reference.txt` to match the words actually spoken. I'll score against that reference, including any departure from the script.

3. Give both transcription tools the same audio in fresh sessions, with `transcription-prompt.txt` where supported. Keep the reading script and reference away from them. Save full, uncorrected transcriptions as `runs/voice/tool-a-answer.txt` and `runs/voice/tool-b-answer.txt`. Record actual time and settings. Import each answer; this example is for tool A:

```sh
uv run python -m scripts.llm --backend manual --model "$TRANSCRIBER_A_MODEL" --prompt runs/voice/transcription-prompt.txt --out runs/voice/tool-a --answer runs/voice/tool-a-answer.txt
```

Repeat for tool B with its model and paths. If a tool doesn't accept an instruction, save its actual settings in a text file and use that as `--prompt`.

4. Extract requirements using the same text model and instructions for both transcripts:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt runs/voice/requirements-prompt.txt --input runs/voice/tool-a/output.txt --out runs/voice/tool-a-requirements
```

Paste the prepared prompt into a fresh chat. Save the real answer as `answer.txt` in that extraction folder and repeat with `--answer runs/voice/tool-a-requirements/answer.txt`. Do the same for tool B. The helper saves text; transcription happens in the chosen audio tools.

## How I'll score it

```sh
uv run python -m scripts.voice_score --reference runs/voice/reference.txt --transcript runs/voice/tool-a/output.txt --output runs/voice/tool-a/measured.csv
```

Repeat for tool B. The script counts word errors, ignoring case and punctuation. I'll use the rubric to check important facts and requirements, separating transcription mistakes from extraction mistakes. One speaker and recording won't establish how a tool handles Australian accents generally.

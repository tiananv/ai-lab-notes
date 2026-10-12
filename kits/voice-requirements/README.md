# Voice memo to requirements

**Question:** How does transcription handle an Australian voice, and which errors change the requirements? Results are pending. No recording or model transcript is supplied.

## Prepare an actual recording

Run `make setup`. Read `inputs/reading.txt` aloud in your own voice and record it as `runs/voice/memo.wav`. The script describes a made-up service. Use your normal accent. Do not simulate another person's voice. Record microphone, room conditions, file format and tool versions in [the run record](../../docs/RUN_RECORD.md).

```sh
mkdir -p runs/voice
cp kits/voice-requirements/scoring.csv docs/RUN_RECORD.md runs/voice/
cp kits/voice-requirements/inputs/reading.txt runs/voice/reference.txt
uv run python -c "from pathlib import Path; from scripts.llm import sha256; print(sha256(Path('runs/voice/memo.wav').read_bytes()))"
```

Run the hash command after making the recording and copy it to the record. Listen once and correct `reference.txt` to match what you actually said, including deviations from the reading script. This human-verified transcript is the ground truth. Do not give the reading script or reference transcript to the transcription tool.

## Transcribe

Choose two transcription tools that accept the same recording. Record their versions, model labels, language settings and any automatic punctuation options. Use the exact `transcription-prompt.txt` instructions where the tool allows them. Start fresh sessions, upload the same audio and export the unedited transcriptions to `runs/voice/tool-a-answer.txt` and `runs/voice/tool-b-answer.txt`. Do not correct names or quantities before scoring. If a tool provides no model identifier, record an explicit user-entered label such as unknown-model-in-tool-name with the tool version.

Set `TRANSCRIBER_A_MODEL` and `TRANSCRIBER_B_MODEL` to the actual tool/model label for each arm. Save prompt and response metadata for both tools:

```sh
uv run python -m scripts.llm --backend manual --model "$TRANSCRIBER_A_MODEL" --prompt kits/voice-requirements/transcription-prompt.txt --out runs/voice/tool-a --answer runs/voice/tool-a-answer.txt
uv run python -m scripts.llm --backend manual --model "$TRANSCRIBER_B_MODEL" --prompt kits/voice-requirements/transcription-prompt.txt --out runs/voice/tool-b --answer runs/voice/tool-b-answer.txt
uv run python -m scripts.voice_score --reference runs/voice/reference.txt --transcript runs/voice/tool-a/output.txt --output runs/voice/tool-a/measured.csv
uv run python -m scripts.voice_score --reference runs/voice/reference.txt --transcript runs/voice/tool-b/output.txt --output runs/voice/tool-b/measured.csv
```

The text harness records the instruction and transcript. Record the audio hash, actual upload time and tool settings in the run record as well. It does not perform speech recognition itself. If the tool cannot take a custom instruction, save the actual settings/instructions used as a text file and pass that file as `--prompt` instead.

## Turn the transcripts into requirements

Set `LLM_MODEL` to one fixed text model. Use the same model and instructions for each transcript so that only the transcription differs. Prepare the first extraction:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt kits/voice-requirements/requirements-prompt.txt --input runs/voice/tool-a/output.txt --out runs/voice/tool-a-requirements
```

Paste the prepared prompt into a fresh chat, save its real answer as `answer.txt` in that extraction folder and repeat the command with `--answer runs/voice/tool-a-requirements/answer.txt`. Repeat for tool-b using its retained transcript. An API backend can replace manual using the [run guide](../../docs/RUNNING.md).

## Score

Read `scoring.md` first. The checker fills word counts, word errors and word error rate. It ignores case and punctuation; it does not treat digits and number words as equivalent. Complete the important-term and requirement checks against the verified reference transcript, keeping errors introduced by transcription separate from errors introduced by extraction. A single speaker and recording cannot support a claim about Australian accents generally. Record that limit in the eventual note.

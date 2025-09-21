#!/usr/bin/env python3
"""Translate SRT subtitle files with offline sequence-to-sequence models.

This script loads a MarianMT model from Hugging Face so you can translate
subtitle files without relying on a network connection after the initial
model download.

Example
-------
    uv run python translate_srt.py original.srt

The CLI exposes flags for choosing the model, language pair, target device,
and batching behaviour. A translated file is written beside the original
using the target language code in the filename suffix.
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

try:
    import torch
except ImportError as exc:
    raise SystemExit(
        "torch is required. Install it with 'pip install torch'."
    ) from exc

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
except ImportError as exc:
    raise SystemExit(
        "transformers is required. Install it with 'pip install transformers sentencepiece'."
    ) from exc

DEFAULT_MODELS: dict[Tuple[str, str], str] = {
    ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
    ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
}


@dataclass
class SubtitleEntry:
    """Simple container for a single subtitle block read from an SRT file."""

    index: str
    timing: str
    lines: List[str] = field(default_factory=list)


class SubtitleTranslator:
    """Translate subtitle batches with a seq2seq model.

    Loads a Hugging Face MarianMT model so we can run translations offline.
    """

    def __init__(
        self,
        model_name: str,
        device: str | None = None,
        max_length: int = 256,
        num_beams: int = 4,
    ) -> None:
        """Initialise the translation model and supporting tokenizer.

        Parameters
        ----------
        model_name : str
            Hugging Face model identifier to load.
        device : str, optional
            Force the execution device. Defaults to auto-detect CUDA.
        max_length : int
            Maximum token length before truncation.
        num_beams : int
            Beam search width passed to ``generate``.
        """

        self.model_name = model_name
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.max_length = max_length
        self.num_beams = num_beams

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

    def translate_batch(self, texts: Sequence[str]) -> List[str]:
        """Translate a batch of subtitle text blocks.

        Parameters
        ----------
        texts : Sequence[str]
            Subtitle lines joined per entry.
        Returns
        -------
        List[str]
            Model outputs decoded to plain text.
        """

        if not texts:
            return []

        inputs = self.tokenizer(
            list(texts),
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.inference_mode():
            generated = self.model.generate(
                **inputs,
                max_length=self.max_length,
                num_beams=self.num_beams,
            )

        outputs = self.tokenizer.batch_decode(
            generated, skip_special_tokens=True
        )
        if len(outputs) != len(texts):
            raise RuntimeError(
                "Unexpected mismatch between inputs and outputs during translation."
            )
        return outputs


def read_srt(path: Path) -> List[SubtitleEntry]:
    """Parse an SRT file into structured subtitle entries.

    Parameters
    ----------
    path : Path
        Location of the subtitle file.

    Returns
    -------
    List[SubtitleEntry]
        Ordered subtitles extracted from the file.
    """

    entries: List[SubtitleEntry] = []
    index: str | None = None
    timing: str | None = None
    text_lines: List[str] = []

    with path.open("r", encoding="utf-8-sig") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\r\n")
            if not line and index is not None and timing is not None:
                entries.append(
                    SubtitleEntry(
                        index=index, timing=timing, lines=list(text_lines)
                    )
                )
                index, timing, text_lines = None, None, []
                continue

            if index is None:
                if line:
                    index = line
                continue

            if timing is None:
                timing = line
                continue

            text_lines.append(line)

    if index is not None and timing is not None:
        entries.append(
            SubtitleEntry(index=index, timing=timing, lines=list(text_lines))
        )

    return entries


def write_srt(path: Path, entries: Sequence[SubtitleEntry]) -> None:
    """Persist subtitle entries to disk using standard SRT formatting.

    Parameters
    ----------
    path : Path
        Destination file path.
    entries : Sequence[SubtitleEntry]
        Subtitles to serialise.
    """

    with path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(f"{entry.index}\n")
            handle.write(f"{entry.timing}\n")
            for text_line in entry.lines:
                handle.write(f"{text_line}\n")
            handle.write("\n")


def chunked(
    items: Sequence[SubtitleEntry], size: int
) -> Iterable[Sequence[SubtitleEntry]]:
    """Yield slices of entries to translate in batches.

    Parameters
    ----------
    items : Sequence[SubtitleEntry]
        Sequence to split.
    size : int
        Number of items per chunk.
    """

    for start in range(0, len(items), size):
        yield items[start : start + size]


def translate_entries(
    entries: List[SubtitleEntry],
    translator: SubtitleTranslator,
    batch_size: int,
    delay: float,
) -> None:
    """Translate subtitle entries and update them in-place.

    Parameters
    ----------
    entries : List[SubtitleEntry]
        Subtitles to modify.
    translator : SubtitleTranslator
        Translator used for inference.
    batch_size : int
        Number of entries translated per batch.
    delay : float
        Optional pause between batches to throttle resource usage.
    """

    for batch in chunked(entries, batch_size):
        payload: List[str] = []
        targets: List[SubtitleEntry] = []

        for entry in batch:
            if not entry.lines:
                continue
            payload.append("\n".join(entry.lines))
            targets.append(entry)

        if not payload:
            continue

        translations = translator.translate_batch(payload)
        for entry, translated_text in zip(targets, translations):
            normalised = translated_text.replace("\r\n", "\n")
            entry.lines = [line for line in normalised.split("\n") if line]

        if delay:
            time.sleep(delay)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Create the argument parser for the translation CLI.

    Parameters
    ----------
    argv : Sequence[str]
        Command-line arguments excluding the program name.

    Returns
    -------
    argparse.Namespace
        Parsed arguments ready for consumption.
    """

    parser = argparse.ArgumentParser(
        description="Translate an SRT file using an offline machine translation model."
    )
    parser.add_argument(
        "input", type=Path, help="Path to the source SRT file."
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Path to write the translated SRT file (default: alongside the input).",
    )
    parser.add_argument(
        "--source", default="en", help="Source language code (default: en)."
    )
    parser.add_argument(
        "--target", default="es", help="Target language code (default: es)."
    )
    parser.add_argument(
        "--model",
        help=(
            "Optional Hugging Face model name. Defaults to Helsinki-NLP opus-mt "
            "model for the requested language pair if available."
        ),
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        help="Execution device override (default: auto-detect).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Number of subtitle entries to translate per batch (default: 16).",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=256,
        help="Maximum token length passed to the model (default: 256).",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=4,
        help="Beam size used during generation (default: 4).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay in seconds between batches (default: 0).",
    )
    return parser.parse_args(argv)


def resolve_model_name(
    src_lang: str, dest_lang: str, explicit_model: str | None
) -> str:
    """Determine which translation model to load for the requested language pair.

    Parameters
    ----------
    src_lang : str
        Source language code.
    dest_lang : str
        Target language code.
    explicit_model : str or None
        Optional override provided via the CLI.

    Returns
    -------
    str
        Hugging Face model identifier.

    Raises
    ------
    SystemExit
        If no default is known for the language pair and no explicit model was supplied.
    """

    if explicit_model:
        return explicit_model

    key = (src_lang.lower(), dest_lang.lower())
    if key in DEFAULT_MODELS:
        return DEFAULT_MODELS[key]

    raise SystemExit(
        "No default model for language pair "
        f"{src_lang}->{dest_lang}. Please provide --model."
    )


def main(argv: Sequence[str]) -> int:
    """Entry point used when invoking the module as a script.

    Parameters
    ----------
    argv : Sequence[str]
        Command-line arguments excluding the program name.

    Returns
    -------
    int
        Process exit code compatible with ``sys.exit``.
    """

    args = parse_args(argv)
    input_path: Path = args.input

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_path: Path
    if args.output is not None:
        output_path = args.output
    else:
        output_path = input_path.with_name(
            f"{input_path.stem}.{args.target}.srt"
        )

    entries = read_srt(input_path)

    if not entries:
        raise SystemExit("No subtitle entries found to translate.")

    model_name = resolve_model_name(args.source, args.target, args.model)

    translator = SubtitleTranslator(
        model_name=model_name,
        device=args.device,
        max_length=args.max_length,
        num_beams=args.beam_size,
    )
    translate_entries(entries, translator, args.batch_size, args.delay)
    write_srt(output_path, entries)

    print(f"Translated subtitles written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

from __future__ import annotations

import argparse
from typing import List, Sequence

from ..runner import WatermarkPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blind_watermark",
        description="Embed or extract invisible watermarks using DWT-DCT-SVD.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--embed", action="store_true", help="Embed watermark into image")
    group.add_argument("--extract", action="store_true", help="Extract watermark from image")
    parser.add_argument("--pwd", dest="password", type=int, default=1, help="Password shared by embed/extract")
    parser.add_argument("--password-img", dest="password_img", type=int, help="Password for image shuffling")
    parser.add_argument("--password-wm", dest="password_wm", type=int, help="Password for watermark scrambling")
    parser.add_argument("--wm-shape", dest="wm_shape", nargs="+", type=int, help="Watermark shape for extraction")
    parser.add_argument("positional", nargs="*", help="Command specific arguments")
    return parser


def _resolve_passwords(args: argparse.Namespace) -> tuple[int, int]:
    pwd_img = args.password_img if args.password_img is not None else args.password
    pwd_wm = args.password_wm if args.password_wm is not None else args.password
    return pwd_img, pwd_wm


def run_embed(pipeline: WatermarkPipeline, positional: Sequence[str]) -> None:
    if len(positional) != 3:
        raise SystemExit("embed mode expects: <cover_image> <watermark_text> <output_image>")
    cover, watermark_text, output_path = positional
    pipeline.read_img(cover)
    pipeline.read_wm(watermark_text, mode="str")
    pipeline.embed(output_path)
    print("Embed succeed! to file", output_path)
    print("Put down watermark size:", pipeline.wm_size)


def run_extract(pipeline: WatermarkPipeline, positional: Sequence[str], wm_shape: Sequence[int] | None) -> None:
    if len(positional) != 1:
        raise SystemExit("extract mode expects: <embedded_image>")
    if wm_shape is None:
        raise SystemExit("--wm-shape is required for extraction")
    embedded_path = positional[0]
    result = pipeline.extract(filename=embedded_path, wm_shape=tuple(wm_shape), mode="str")
    print("Extract succeed! watermark is:")
    print(result)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    password_img, password_wm = _resolve_passwords(args)
    pipeline = WatermarkPipeline(password_img=password_img, password_wm=password_wm)

    if args.embed:
        run_embed(pipeline, args.positional)
    else:
        run_extract(pipeline, args.positional, args.wm_shape)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


from __future__ import annotations

import ast
from pathlib import Path

import cv2
import numpy as np
import pytest

from app.services import WatermarkService


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "examples" / "pic"


def load_bytes(name: str) -> bytes:
    return (FIXTURE_DIR / name).read_bytes()


@pytest.fixture(scope="module")
def service() -> WatermarkService:
    return WatermarkService()


def test_embed_and_extract_string(service: WatermarkService) -> None:
    cover_bytes = load_bytes("ori_img.jpeg")
    embedded_bytes, wm_length, wm_shape = service.embed_watermark(
        image_bytes=cover_bytes,
        mode="str",
        password_img=1,
        password_wm=1,
        watermark_text="hello watermark",
    )

    assert wm_length > 0
    assert wm_shape is None
    extracted_text, _ = service.extract_watermark(
        image_bytes=embedded_bytes,
        mode="str",
        password_img=1,
        password_wm=1,
        watermark_length=wm_length,
    )
    assert extracted_text == "hello watermark"


def test_embed_and_extract_image(service: WatermarkService) -> None:
    cover_bytes = load_bytes("ori_img.jpeg")
    watermark_bytes = load_bytes("watermark.png")

    embedded_bytes, wm_length, wm_shape = service.embed_watermark(
        image_bytes=cover_bytes,
        mode="img",
        password_img=9,
        password_wm=7,
        watermark_image_bytes=watermark_bytes,
    )
    assert wm_length > 0
    assert wm_shape == tuple(
        cv2.imdecode(np.frombuffer(watermark_bytes, np.uint8), cv2.IMREAD_UNCHANGED).shape[:2]
    )

    _, extracted_bytes = service.extract_watermark(
        image_bytes=embedded_bytes,
        mode="img",
        password_img=9,
        password_wm=7,
        watermark_length=wm_length,
        watermark_shape=wm_shape,
    )
    assert extracted_bytes is not None

    original = cv2.imdecode(np.frombuffer(watermark_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    extracted = cv2.imdecode(np.frombuffer(extracted_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    assert extracted.shape == original.shape
    assert np.mean(np.abs(extracted.astype(np.int16) - original.astype(np.int16))) < 30


def test_embed_and_extract_bits(service: WatermarkService) -> None:
    cover_bytes = load_bytes("ori_img.jpeg")
    length = 64

    embedded_bytes, wm_length, wm_shape = service.embed_watermark(
        image_bytes=cover_bytes,
        mode="bit",
        password_img=3,
        password_wm=5,
        watermark_length=length,
    )
    assert wm_length == length
    assert wm_shape is None

    extracted_text, _ = service.extract_watermark(
        image_bytes=embedded_bytes,
        mode="bit",
        password_img=3,
        password_wm=5,
        watermark_length=wm_length,
        watermark_shape=None,
    )
    assert extracted_text is not None
    extracted_bits = ast.literal_eval(extracted_text)
    assert isinstance(extracted_bits, list)
    assert len(extracted_bits) == length


def test_invalid_mode_raises(service: WatermarkService) -> None:
    cover_bytes = load_bytes("ori_img.jpeg")
    with pytest.raises(ValueError):
        service.embed_watermark(
            image_bytes=cover_bytes,
            mode="unknown",
            password_img=1,
            password_wm=1,
        )

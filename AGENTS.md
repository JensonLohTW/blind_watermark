# AGENTS.md

This file provides guidance to coding agents when working with this repository.

## Project Overview

blind_watermark is a Python library for embedding and extracting invisible watermarks in images using DWT-DCT-SVD (Discrete Wavelet Transform, Discrete Cosine Transform, Singular Value Decomposition) algorithms. The library supports robust watermarking that survives rotation, cropping, scaling, brightness adjustments, and other image attacks.

## Development Commands

### Installation
```bash
# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### Testing
Example files are used as functional tests. Run from the `examples/` directory:
```bash
cd examples
python example_str.py        # String watermark embedding/extraction
python example_img.py        # Image watermark embedding/extraction
python example_bit.py        # Bit-array watermark
python example_no_writing.py # In-memory workflow
```

For coverage (as configured in .travis.yml):
```bash
cd examples
coverage run -p example_no_writing.py
coverage run -p example_bit.py
coverage run -p example_str.py
coverage run -p example_img.py
cd ..
coverage combine
```

### CLI Usage
The CLI is exposed through a helper script (recommended) or direct module invocation:
```bash
# Embed watermark (script)
./scripts/watermark_cli.sh --embed --pwd 1234 examples/pic/ori_img.jpeg "watermark text" examples/output/embedded.png

# Extract watermark (script)
./scripts/watermark_cli.sh --extract --pwd 1234 --wm_shape 64 64 examples/output/embedded.png

# Direct module alternative
python -m app.core.watermark.cli.entrypoint --embed --pwd 1234 examples/pic/ori_img.jpeg "watermark text" examples/output/embedded.png
python -m app.core.watermark.cli.entrypoint --extract --pwd 1234 --wm_shape 64 64 examples/output/embedded.png
```

## Architecture

### Core Components (located at `backend/app/core/watermark/`)

**WaterMark (facade.py)** – High-level compatibility API  
- Preserves familiar methods: `read_img()`, `read_wm()`, `embed()`, `extract()`  
- Delegates to `WatermarkPipeline` while exposing `wm_bit` and `wm_size`

**WatermarkPipeline (runner/__init__.py)** – Orchestrates embed/extract workflow  
- Coordinates `WatermarkEmbedder` and `WatermarkExtractor`  
- Builds configuration via `WatermarkConfig` (passwords, block shape, runtime mode)

**WatermarkAlgorithm (operations/algorithm.py)** – Low-level DWT/DCT/SVD implementation  
- Handles 4×4 block transforms and payload averaging  
- Provides K-means helper for bit thresholding

**AutoPool (runtime/pool.py)** – Concurrency abstraction  
- Supports `common`, `multithreading`, and `multiprocessing` execution modes  
- Automatically falls back to multithreading on Windows

**Attack & Recovery (att.py, recover.py)** – Robustness utilities  
- `att.py` keeps legacy helpers (`cut_att3`, `salt_pepper_att`, etc.) backed by `robustness.attacks`  
- `recover.py` exposes `estimate_crop_parameters` and `recover_crop`, with optional `base_img` overlay support

### Data Flow

**Embedding**: BGR image → YUV conversion → DWT per channel → 4×4 block DCT → SVD modification → inverse transforms → watermarked image

**Extraction**: Watermarked image → same transform pipeline → bit extraction and averaging → password-based decryption → decoded watermark

### Password System

Two passwords provide dual-layer security:
- `password_wm`: shuffles watermark bits (payload-level encryption)
- `password_img`: shuffles block embedding order (image-level protection)

### Watermark Capacity

Embeddable bits are constrained by:
```
block_num = (ca_shape[0] // 4) * (ca_shape[1] // 4)
```
where `ca_shape` is half of the original image dimensions after DWT. Payload bits cycle if `wm_size < block_num`.

## Important Notes

- **wm_shape requirement**: Extraction requires the original watermark length or shape. Record `len(bwm.wm_bit)` after embedding string/bit payloads.
- **Password consistency**: `password_img` and `password_wm` must match between embedding and extraction.
- **Attack recovery**: For unknown crop/scale parameters, call `estimate_crop_parameters()` followed by `recover_crop()` before extraction. Supplying `base_img` improves reconstruction fidelity.
- **YUV color space**: All processing happens in YUV to separate luminance/chrominance and improve robustness.
- **Robustness vs quality**: Adjust `AlgorithmTuning` (`d1`, `d2`) in `backend/app/core/watermark/config.py` to balance quality and resilience.

## Related Code Patterns

Example attack recovery workflow:
```python
# 1. Apply attack
att.cut_att3(input_filename='embedded.png', output_file_name='attacked.png', ...)

# 2. Estimate attack parameters (if unknown)
(loc, shape, score, scale) = estimate_crop_parameters(
    original_file='embedded.png', template_file='attacked.png', ...)

# 3. Recover to original dimensions (optionally overlay on base image)
recover_crop(template_file='attacked.png', output_file_name='recovered.png',
             loc=loc, image_o_shape=shape[:2], base_img=cv2.imread('embedded.png'))

# 4. Extract watermark
wm_extract = bwm.extract('recovered.png', wm_shape=len_wm, mode='str')
```

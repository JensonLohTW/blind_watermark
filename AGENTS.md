# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

blind_watermark is a Python library for embedding and extracting invisible watermarks in images using DWT-DCT-SVD (Discrete Wavelet Transform, Discrete Cosine Transform, Singular Value Decomposition) algorithms. The library supports robust watermarking that survives various image attacks including rotation, cropping, scaling, brightness adjustments, and more.

## Development Commands

### Installation
```bash
# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### Testing
The project uses example files as tests. Run from the `examples/` directory:
```bash
cd examples
python example_str.py      # Test string watermark embedding/extraction
python example_img.py      # Test image watermark embedding/extraction
python example_bit.py      # Test bit array watermark
python example_no_writing.py  # Test without writing files
```

For test coverage (as configured in .travis.yml):
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
The package installs a `blind_watermark` command:
```bash
# Embed watermark
blind_watermark --embed --pwd 1234 examples/pic/ori_img.jpeg "watermark text" examples/output/embedded.png

# Extract watermark
blind_watermark --extract --pwd 1234 --wm_shape 111 examples/output/embedded.png
```

## Architecture

### Core Components

**WaterMark (blind_watermark.py)**: High-level user API
- Handles three watermark modes: 'img' (image), 'str' (text string), 'bit' (bit array)
- Manages password-based encryption/decryption of watermarks
- Orchestrates the embedding and extraction workflow
- Key methods: `read_img()`, `read_wm()`, `embed()`, `extract()`

**WaterMarkCore (bwm_core.py)**: Low-level watermarking algorithm
- Implements DWT-DCT-SVD frequency domain operations
- Uses 4x4 block-based processing on YUV color space
- Channel processing: applies watermark to all 3 YUV channels
- Two robustness parameters: `d1=36` (primary), `d2=20` (secondary) - higher values increase robustness but reduce image quality
- Supports multiprocessing via AutoPool for performance
- Key insight: watermark bits are embedded cyclically across all blocks, extracted values are averaged for robustness

**AutoPool (pool.py)**: Concurrency abstraction
- Supports multiple execution modes: 'common' (serial), 'multithreading', 'multiprocessing', 'vectorization', 'cached'
- Automatically falls back to multithreading on Windows (multiprocessing limitations)
- Controlled via `processes` parameter in WaterMark constructor

**Attack & Recovery (att.py, recover.py)**:
- `att.py`: Functions to simulate attacks (crop, resize, rotate, brightness, salt/pepper noise, sheltering)
- `recover.py`: Template matching algorithms to estimate attack parameters and recover original dimensions
- `estimate_crop_parameters()`: Uses cv2.matchTemplate with scale search to infer crop/scale attack parameters
- `recover_crop()`: Reconstructs attacked images to original dimensions for extraction

### Data Flow

**Embedding**: Image (BGR) → YUV conversion → DWT on each channel → 4×4 block partition → DCT → SVD → modify singular values → inverse operations → watermarked image

**Extraction**: Watermarked image → same transformation pipeline → extract bits from singular values → average across blocks and channels → decrypt with password → output watermark

**Key Implementation Details**:
- Images are padded to even dimensions before processing
- Transparent images (4-channel) are supported - alpha channel is preserved separately
- Watermark bits are shuffled using `np.random.RandomState(password)` for encryption
- Block indices are shuffled with a different password for image-level security
- Extraction uses k-means clustering on extracted values to determine bit threshold

### Password System

Two passwords provide dual-layer security:
- `password_wm`: Shuffles watermark bits themselves (encryption at watermark level)
- `password_img`: Shuffles block embedding order (encryption at image level via `random_strategy1`)

### Watermark Capacity

The number of embeddable bits is constrained by:
```
block_num = (ca_shape[0] // 4) * (ca_shape[1] // 4)
```
where `ca_shape` is approximately half the original image dimensions after DWT. The watermark is embedded cyclically if `wm_size < block_num`.

## Important Notes

- **wm_shape requirement**: When extracting, you MUST know the watermark shape/length used during embedding. For string watermarks, save `len(bwm.wm_bit)` after embedding.
- **Password consistency**: Both `password_img` and `password_wm` must match between embedding and extraction.
- **Attack recovery**: For crop/scale attacks where parameters are unknown, use `estimate_crop_parameters()` followed by `recover_crop()` before extraction.
- **YUV color space**: All processing happens in YUV to separate luminance from chrominance - watermark survives better this way.
- **Robustness vs quality tradeoff**: Modify `self.d1` and `self.d2` in WaterMarkCore to adjust this tradeoff.

## Related Code Patterns

When implementing attack recovery workflows, follow this pattern from example_str.py:
```python
# 1. Apply attack
att.cut_att3(input_filename='embedded.png', output_file_name='attacked.png', ...)

# 2. Estimate attack parameters (if unknown)
(x1, y1, x2, y2), shape, score, scale = estimate_crop_parameters(
    original_file='embedded.png', template_file='attacked.png', ...)

# 3. Recover to original dimensions
recover_crop(template_file='attacked.png', output_file_name='recovered.png',
             loc=(x1, y1, x2, y2), image_o_shape=shape)

# 4. Extract watermark
wm_extract = bwm.extract('recovered.png', wm_shape=len_wm, mode='str')
```

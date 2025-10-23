# Algorithm and Implementation Details

## Watermarking Algorithm Flow

### Embedding Process
1. **Image Preparation**:
   - Load image in BGR (OpenCV default)
   - Convert to YUV color space (separates luminance from chrominance)
   - Apply DWT on each YUV channel → get CA (approximation) and HVD (detail) coefficients
   - Pad image to even dimensions if needed

2. **Block Processing**:
   - Partition CA coefficients into 4×4 blocks
   - Shuffle blocks using `password_img` via `random_strategy1()`
   - For each block:
     - Apply DCT (Discrete Cosine Transform)
     - Apply SVD (Singular Value Decomposition) → U, S, V matrices
     - Modify singular values: `S[0] += d1 * wm_bit` and `S[1] += d2 * wm_bit`
     - Reconstruct block via inverse SVD, inverse DCT

3. **Watermark Encryption**:
   - Watermark bits shuffled using `password_wm`
   - Embedded cyclically if `wm_size < block_num`

4. **Image Reconstruction**:
   - Apply inverse DWT on modified CA and original HVD
   - Convert YUV back to BGR
   - Restore alpha channel if present

### Extraction Process
1. **Image Loading**: Same YUV conversion and DWT as embedding
2. **Block Processing**:
   - For each block, extract watermark bits via DCT → SVD
   - Extract from all 3 YUV channels
   - Average extracted values across blocks and channels (robustness strategy)
3. **Bit Decision**:
   - Use k-means clustering (via `one_dim_kmeans`) to find threshold
   - Convert to binary watermark bits
4. **Decryption**: Unshuffle using `password_wm` → recover original watermark

## Key Parameters

### Robustness Control
- **d1 = 36**: Primary strength (affects S[0])
- **d2 = 20**: Secondary strength (affects S[1])
- Higher values → more robust, lower image quality

### Password System
- **password_wm**: Encrypts watermark bit order
- **password_img**: Encrypts block embedding order
- Both must match during extraction

## Capacity Calculation
```python
ca_shape ≈ (img_height // 2, img_width // 2)  # After DWT
block_num = (ca_shape[0] // 4) * (ca_shape[1] // 4)
max_wm_bits = block_num
```

## Attack Recovery Strategy
For unknown crop/scale parameters:
1. Use `estimate_crop_parameters()`: Template matching with scale search
2. Use `recover_crop()`: Reconstruct original dimensions
3. Extract watermark from recovered image

## YUV Color Space Benefit
- Y (luminance): Where watermark is primarily embedded
- U, V (chrominance): Redundant embedding increases robustness
- Human vision less sensitive to YUV frequency changes

#!/usr/bin/env python3
"""
extract_blue_curves.py

Detects blue curves in a plot image and returns dB(A) values for the 7 curves
(at D = 1,2,4,6,8,10,12,14). Uses only Pillow, numpy, pandas, matplotlib.

Usage:
    python extract_blue_curves.py
    python extract_blue_curves.py --image img1.gif
"""

import argparse
from PIL import Image
import numpy as np
import pandas as pd
import sys
import math
import os

# ---------------------------
# Configuration (fixed)
# ---------------------------
TARGET_DS = [1,2,4,6,8,10,12,14]
CURVE_LABELS = ['Cv=15xD^2','Cv=10xD^2','Cv=7xD^2','Cv=5xD^2','Cv=3xD^2','Cv=2xD^2','Cv=1xD^2']

# Data axis ranges
X_MIN, X_MAX = 0.0, 14.0
Y_MIN, Y_MAX = 10.0, 30.0   # dB (bottom -> top)

# Blue HSV range (matplotlib / 0..1 ranges) — from clicks you provided
H_MIN, H_MAX = 0.53, 0.60
S_MIN, S_MAX = 0.10, 1.00
V_MIN, V_MAX = 0.70, 1.00

# pixel search window half-width
SEARCH_W = 4

# ---------------------------
# Helpers
# ---------------------------
def rgb_to_hsv_unit(rgb):
    """rgb array (H,W,3) 0..255 -> hsv 0..1 (using matplotlib-like conversion)"""
    # vectorized conversion using colorsys-like formula
    arr = rgb.astype('float32') / 255.0
    r = arr[...,0]; g = arr[...,1]; b = arr[...,2]
    mx = np.max(arr, axis=2)
    mn = np.min(arr, axis=2)
    diff = mx - mn
    # Hue
    h = np.zeros_like(mx)
    mask = diff != 0
    # avoid div by zero
    idx = (mx == r) & mask
    h[idx] = ((g[idx] - b[idx]) / diff[idx]) % 6
    idx = (mx == g) & mask
    h[idx] = ((b[idx] - r[idx]) / diff[idx]) + 2
    idx = (mx == b) & mask
    h[idx] = ((r[idx] - g[idx]) / diff[idx]) + 4
    h = h / 6.0
    h[h < 0] += 1.0
    # Saturation
    s = np.zeros_like(mx)
    s[mx > 0] = diff[mx > 0] / mx[mx > 0]
    # Value
    v = mx
    hsv = np.stack([h, s, v], axis=2)
    return hsv

def find_plot_bbox(gray):
    """Find bounding box of plot by looking for dark vertical/horizontal gridlines."""
    h, w = gray.shape
    col_dark = (gray < 90).sum(axis=0)
    row_dark = (gray < 90).sum(axis=1)

    # take columns/rows above some percentile as candidates
    try:
        col_thresh = max(1, int(np.percentile(col_dark, 93)))
        row_thresh = max(1, int(np.percentile(row_dark, 93)))
    except Exception:
        col_thresh = row_thresh = 1

    col_candidates = np.where(col_dark >= col_thresh)[0]
    row_candidates = np.where(row_dark >= row_thresh)[0]

    if len(col_candidates) >= 2 and len(row_candidates) >= 2:
        left = int(col_candidates.min())
        right = int(col_candidates.max())
        top = int(row_candidates.min())
        bottom = int(row_candidates.max())
        # small safety margins
        dx = max(2, int(0.01 * w))
        dy = max(2, int(0.01 * h))
        left = max(0, left - dx)
        right = min(w-1, right + dx)
        top = max(0, top - dy)
        bottom = min(h-1, bottom + dy)
        if right - left > 40 and bottom - top > 40:
            return left, right, top, bottom

    # fallback to conservative crop
    return int(0.06*w), int(0.94*w), int(0.06*h), int(0.90*h)

def cluster_runs(sorted_ys, gap_thresh=3):
    """Cluster sorted y indices into runs separated by gaps > gap_thresh. Return list of medians (py)."""
    if len(sorted_ys) == 0:
        return []
    runs = []
    run = [sorted_ys[0]]
    for y in sorted_ys[1:]:
        if y - run[-1] <= gap_thresh:
            run.append(y)
        else:
            runs.append(int(np.median(run)))
            run = [y]
    runs.append(int(np.median(run)))
    return runs

# ---------------------------
# Main extraction
# ---------------------------
def extract(image_path):
    # load
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    H_img, W_img, _ = arr.shape

    gray = arr.mean(axis=2).astype(np.uint8)

    left, right, top, bottom = find_plot_bbox(gray)
    crop = arr[top:bottom+1, left:right+1]
    ch, cw, _ = crop.shape

    # compute hsv 0..1
    hsv = rgb_to_hsv_unit(crop)

    # build mask from given HSV window
    mask = (hsv[...,0] >= H_MIN) & (hsv[...,0] <= H_MAX) & \
           (hsv[...,1] >= S_MIN) & (hsv[...,1] <= S_MAX) & \
           (hsv[...,2] >= V_MIN) & (hsv[...,2] <= V_MAX)

    # small morphological clean (simple): remove tiny isolated pixels by filtering by neighborhood count
    # compute neighborhood sum via convolution-ish using integral image for speed
    pad = 1
    padded = np.pad(mask.astype(np.uint8), pad, mode='constant', constant_values=0)
    kernel_size = 3
    # fast local sum
    from numpy.lib.stride_tricks import sliding_window_view
    sw = sliding_window_view(padded, (kernel_size, kernel_size))
    local_sum = sw.sum(axis=(2,3))
    mask_clean = (local_sum >= 1)  # keep pixels that have at least 1 neighbor (tolerant)
    mask = mask_clean

    # For mapping px->D: linear mapping left->right to X_MIN..X_MAX
    def D_to_px(D):
        return int(round((D - X_MIN) / (X_MAX - X_MIN) * (cw - 1)))

    # For mapping py->dB: top pixel -> Y_MAX (30), bottom pixel -> Y_MIN (10)
    def py_to_db(py_crop):
        # py_crop is y in crop coords (0..ch-1)
        frac = py_crop / float(ch - 1)
        # top->0 => dB = Y_MAX - frac*(Y_MAX-Y_MIN)
        return Y_MAX - frac * (Y_MAX - Y_MIN)

    # Now for each target D, sample
    results = {}
    for D in TARGET_DS:
        px = D_to_px(D)
        # window horizontally around px
        xs = list(range(max(0, px-SEARCH_W), min(cw, px+SEARCH_W+1)))
        ys = []
        for x in xs:
            col_idxs = np.where(mask[:, x])[0]
            if col_idxs.size:
                ys.extend(col_idxs.tolist())
        ys = sorted(set(ys))
        # if too few points, expand to full crop and pick column close to px
        if len(ys) < 3:
            # try expanding to larger horizontal range
            xs2 = list(range(max(0, px-12), min(cw, px+13)))
            ys = []
            for x in xs2:
                col_idxs = np.where(mask[:, x])[0]
                ys.extend(col_idxs.tolist())
            ys = sorted(set(ys))
        if len(ys) == 0:
            results[D] = [None]*len(CURVE_LABELS)
            continue
        # cluster contiguous y runs into curve candidates
        runs = cluster_runs(ys, gap_thresh=4)  # medians of contiguous runs
        # runs are sorted top->bottom? ys sorted ascending (top small). We want top->bottom => small py -> high dB
        runs_sorted = sorted(runs)  # ascending py
        # convert to dB and sort highest dB first
        dbs = [py_to_db(r) for r in runs_sorted]
        # Now we expect up to 7 distinct curves; if there are more clusters than 7, pick 7 best spaced
        if len(dbs) >= len(CURVE_LABELS):
            selected = dbs[:len(CURVE_LABELS)]
        else:
            # If fewer, try to fill by looking for local maxima in each column (rare), otherwise pad with None
            # We will still place the found ones at the top of the result and pad bottom ones
            selected = dbs + [None]*(len(CURVE_LABELS)-len(dbs))
        # ensure length 7
        selected = selected[:len(CURVE_LABELS)]
        results[D] = [round(v,2) if v is not None else None for v in selected]

    # Assemble DataFrame
    df = pd.DataFrame(index=TARGET_DS, columns=CURVE_LABELS)
    for D in TARGET_DS:
        vals = results[D]
        for i,label in enumerate(CURVE_LABELS):
            df.loc[D, label] = vals[i]
    df.index.name = 'D_in'
    return df, (left, right, top, bottom), mask, crop

# ---------------------------
# CLI
# ---------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--image', help='image file path', default=None)
    args = p.parse_args()

    # try image candidates
    candidates = []
    if args.image:
        candidates.append(args.image)
    candidates += ['img1.gif', 'auto-basics-3.gif', '/mnt/data/auto-basics-3.gif']

    img_path = None
    for c in candidates:
        if c and os.path.exists(c):
            img_path = c
            break
    if img_path is None:
        print("No image found. Tried:", candidates, file=sys.stderr)
        sys.exit(2)

    print("Using image:", img_path)
    df, bbox, mask, crop = extract(img_path)
    left, right, top, bottom = bbox
    print("\nDetected plot bbox (px): left={}, right={}, top={}, bottom={}".format(left, right, top, bottom))

    print("\nExtracted table (dB(A) values). Rows are D (inches):\n")
    print(df.to_string())
    df.to_csv("extracted_curves.csv")
    print("\nSaved CSV: extracted_curves.csv")

    # Save mask preview
    try:
        from matplotlib import pyplot as plt
        plt.figure(figsize=(8,5))
        plt.imshow(crop)
        # overlay mask in red (semi-transparent)
        m = np.zeros_like(crop, dtype=np.uint8)
        m[mask] = [255,0,0]
        plt.imshow(np.dstack([m[:,:,0], np.zeros_like(m[:,:,0]), np.zeros_like(m[:,:,0])]), alpha=0.4)
        plt.axis('off')
        plt.title('Crop with detected blue pixels (red overlay)')
        plt.savefig('mask_preview.png', dpi=150, bbox_inches='tight')
        print("Saved mask preview: mask_preview.png")
    except Exception:
        pass

if __name__ == '__main__':
    main()

import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


# Load an image, crop to a square, resize, convert to inverse grayscale
def prepareImage(path: str, size: int) -> np.ndarray:
    img = Image.open(path).convert("L") # grayscale, uint8

    # centre-crop to square
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    img = img.resize((size, size), Image.LANCZOS)

    # f_gray ∈ [0,1]
    f_gray = np.array(img, dtype=np.float32) / 255.0

    # f^(0) = 1 - f_gray
    residual = 1.0 - f_gray

    # zero out pixels outside the inscribed circle
    cy, cx = size / 2, size / 2
    R = size / 2 - 1
    ys, xs = np.ogrid[:size, :size]
    mask = (xs - cx)**2 + (ys - cy)**2 > R**2
    residual[mask] = 0.0

    return residual


# Compute nail positions
# n_i = (R·cos(2πi/N),  R·sin(2πi/N))
def nailPositions(N: int, size: int) -> np.ndarray:
    cx, cy = size / 2, size / 2
    R = size / 2 - 2 # slight inset so nails stay inside canvas

    angles = 2 * np.pi * np.arange(N) / N
    xs = cx + R * np.cos(angles)
    ys = cy + R * np.sin(angles)

    # round to nearest pixel
    nails = np.stack([xs, ys], axis=1).astype(int)
    return nails


# Precompute all chord pixel paths
# L_ij = set of pixels on the line between nail i and nail j. 
# Computed once using Bresenham's algorithm, stored for reuse
# Returns an (M, 2) array of (x, y) pixel coordinates along the
# line from (x0,y0) to (x1,y1), using Bresenham's algorithm.
def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    pts = []
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    cx, cy = x0, y0
    while True:
        pts.append((cx, cy))
        if cx == x1 and cy == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx  += sx
        if e2 < dx:
            err += dx
            cy  += sy

    return np.array(pts, dtype=np.int32)


def precompute_chords(nails: np.ndarray, size: int, min_skip = None) -> dict:
    """
    Precompute the pixel path for every valid nail pair (i, j).

    min_skip: minimum index gap between nails to avoid near-parallel
              short chords at the perimeter. Defaults to N//20.

    Returns a dict:  (i, j) → np.ndarray of shape (M, 2)
    Only stores i < j to avoid redundancy (L_ij == L_ji).
    """
    N = len(nails)
    if min_skip is None:
        min_skip = max(5, N // 20)

    chords = {}
    for i in range(N):
        for j in range(i + 1, N):
            gap = min(j - i, N - (j - i))        # shortest arc distance between nails
            if gap < min_skip:
                continue                           # skip chords between adjacent nails
            x0, y0 = nails[i]
            x1, y1 = nails[j]
            pts = bresenham_line(x0, y0, x1, y1)

            # clip to canvas bounds (safety)
            valid = (pts[:, 0] >= 0) & (pts[:, 0] < size) & \
                    (pts[:, 1] >= 0) & (pts[:, 1] < size)
            chords[(i, j)] = pts[valid]

    return chords


# SECTION 4 — Score a chord (the Radon projection)
#   S^(k)(i,j) = (1 / |L_ij|) · Σ_{(x,y) ∈ L_ij}  f^(k)(x, y)
#
# This IS the discrete Radon Transform of f^(k) along chord (i,j).
# We evaluate it for all chords at each iteration.

def score_chord(residual: np.ndarray, pts: np.ndarray) -> float:
    """
    Compute S^(k)(i,j): the mean residual darkness along the chord.

    residual : 2D float array, shape (H, W)
    pts      : (M, 2) array of (x, y) pixel coords on the chord

    Note: residual is indexed as [row, col] = [y, x].
    """
    xs, ys = pts[:, 0], pts[:, 1]
    total  = residual[ys, xs].sum()              # Σ f^(k)(x,y) along chord
    length = len(pts)                            # |L_ij|
    return total / length                        # normalise by length


# ─────────────────────────────────────────────
# SECTION 5 — The greedy loop
# ─────────────────────────────────────────────
#
# Repeat for k = 0 … K-1:
#   1. Find (i*,j*) = argmax_{i,j}  S^(k)(i,j)          [score all chords]
#   2. Record the winning chord
#   3. f^(k+1)(x,y) = max(0,  f^(k)(x,y) − α · 1_{(x,y)∈L_{i*j*}})

def run_greedy(residual: np.ndarray,
               chords: dict,
               K: int,
               alpha: float = 0.15,
               verbose: bool = True) -> list:
    """
    Run K steps of the greedy Matching-Pursuit algorithm.

    residual : f^(0), modified in-place as strings are added
    chords   : precomputed dict of (i,j) → pixel path
    K        : number of strings to place
    alpha    : opacity — how much residual one string removes per pixel
    verbose  : print progress

    Returns a list of K winning (i, j) pairs in order.
    """
    chosen   = []                                # the K winning chord indices
    energies = []                                # E^(k) = Σ residual, for plotting

    for k in range(K):
        # ── Step 1 & 2: score every chord, find the best ──────────────
        # S^(k)(i,j) = mean residual along chord
        best_score = -np.inf
        best_pair  = None

        for (i, j), pts in chords.items():
            s = score_chord(residual, pts)
            if s > best_score:
                best_score = s
                best_pair  = (i, j)

        if best_pair is None:
            break

        chosen.append(best_pair)
        energies.append(residual.sum())

        # ── Step 3: subtract the winning chord from the residual ───────
        # f^(k+1)(x,y) = max(0,  f^(k)(x,y) − α · 1_{(x,y) ∈ L_{i*j*}})
        pts = chords[best_pair]
        xs, ys = pts[:, 0], pts[:, 1]
        residual[ys, xs] = np.maximum(0.0, residual[ys, xs] - alpha)

        if verbose and (k % 100 == 0 or k == K - 1):
            E = residual.sum()
            print(f"  string {k+1:4d}/{K}  best_score={best_score:.4f}  "
                  f"residual_energy={E:.1f}")

    return chosen, energies


# ─────────────────────────────────────────────
# SECTION 6 — Render the result
# ─────────────────────────────────────────────

def render(nails: np.ndarray, chosen: list, size: int,
           alpha: float = 0.15, dark_on_light: bool = True) -> np.ndarray:
    """
    Draw the chosen strings onto a blank canvas.
    Returns a (size, size) float array in [0,1].
    """
    bg    = 1.0 if dark_on_light else 0.0
    ink   = 0.0 if dark_on_light else 1.0
    canvas = np.full((size, size), bg, dtype=np.float32)

    for (i, j) in chosen:
        x0, y0 = nails[i]
        x1, y1 = nails[j]
        pts = bresenham_line(x0, y0, x1, y1)

        # clip
        valid = (pts[:, 0] >= 0) & (pts[:, 0] < size) & \
                (pts[:, 1] >= 0) & (pts[:, 1] < size)
        pts = pts[valid]
        xs, ys = pts[:, 0], pts[:, 1]

        if dark_on_light:
            canvas[ys, xs] = np.maximum(0.0, canvas[ys, xs] - alpha)
        else:
            canvas[ys, xs] = np.minimum(1.0, canvas[ys, xs] + alpha)

    return canvas


# ─────────────────────────────────────────────
# SECTION 7 — Visualise everything
# ─────────────────────────────────────────────

def visualise(f0_orig: np.ndarray, residual_final: np.ndarray,
              result: np.ndarray, energies: list,
              nails: np.ndarray, size: int):
    """
    4-panel figure:
      1. Original (inverted residual f^(0))
      2. Final residual f^(K) — what's still unexplained
      3. String art render
      4. Residual energy E^(k) over iterations
    """
    fig = plt.figure(figsize=(14, 4))
    gs  = GridSpec(1, 4, figure=fig, wspace=0.3)

    # panel 1 — original
    ax1 = fig.add_subplot(gs[0])
    ax1.imshow(1 - f0_orig, cmap='gray', vmin=0, vmax=1)
    ax1.set_title("f_gray (original)", fontsize=11)
    ax1.axis('off')

    # panel 2 — final residual
    ax2 = fig.add_subplot(gs[1])
    ax2.imshow(residual_final, cmap='hot', vmin=0, vmax=1)
    ax2.set_title("f⁽ᴷ⁾ (residual after K strings)", fontsize=11)
    ax2.axis('off')

    # panel 3 — result
    ax3 = fig.add_subplot(gs[2])
    ax3.imshow(result, cmap='gray', vmin=0, vmax=1)
    # draw nails
    ax3.scatter(nails[:, 0], nails[:, 1], s=2, c='red', zorder=5)
    ax3.set_title("String art render", fontsize=11)
    ax3.axis('off')

    # panel 4 — energy decay
    ax4 = fig.add_subplot(gs[3])
    ax4.plot(energies, color='#7F77DD', linewidth=1.5)
    ax4.set_xlabel("String k", fontsize=10)
    ax4.set_ylabel("Residual energy E⁽ᵏ⁾", fontsize=10)
    ax4.set_title("Energy decay", fontsize=11)
    # mark elbow
    diffs = np.diff(energies)
    if len(diffs) > 1:
        elbow = int(np.argmin(diffs > diffs[0] * 0.1))
        ax4.axvline(elbow, color='#D85A30', linestyle='--', linewidth=1,
                    label=f'elbow ≈ {elbow}')
        ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)

    plt.suptitle("String Art — Greedy Radon Algorithm", fontsize=13, y=1.02)
    plt.savefig("String Art/output.png",
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: string_art_output.png")
    

if __name__ == "__main__":
    SIZE  = 512     # canvas size in pixels
    N     = 300     # number of nails
    K     = 1000     # number of strings
    ALPHA = 0.18    # line opacity

    print("=== String Art Generator ===\n")

    # 1. image
    print("1. Preparing image...")
    img_path = r"String Art/images.jpg"
    f0 = prepareImage(img_path, size=SIZE)
    f0_orig = f0.copy()                          # keep a copy for visualisation

    # 2. nails
    print(f"2. Placing {N} nails...")
    nails = nailPositions(N, SIZE)
    print(f"   Angular resolution Δθ ≈ {180/N:.1f}°")

    # 3. precompute chords
    print("3. Precomputing chord pixel paths...")
    chords = precompute_chords(nails, SIZE)
    print(f"   {len(chords)} valid chords from {N} nails")

    # 4. greedy loop
    print(f"\n4. Running greedy algorithm for K={K} strings, α={ALPHA}...")
    chosen, energies = run_greedy(f0, chords, K=K, alpha=ALPHA, verbose=True)

    # 5. render
    print("\n5. Rendering result...")
    result = render(nails, chosen, SIZE, alpha=ALPHA, dark_on_light=True)

    # 6. visualise
    print("6. Saving visualisation...")
    visualise(f0_orig, f0, result, energies, nails, SIZE)

    print("\nDone.")
    print(f"  Strings placed : {len(chosen)}")
    print(f"  Final residual : {f0.sum():.1f}  (started at {f0_orig.sum():.1f})")
    print(f"  Reduction      : {100*(1 - f0.sum()/f0_orig.sum()):.1f}%")
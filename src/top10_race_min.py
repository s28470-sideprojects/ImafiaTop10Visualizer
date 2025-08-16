# All comments/messages in code are in English only.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import MaxNLocator
from pathlib import Path

# your CSV (tour,nickname,points)
CSV_PATH = Path("data/tournament_results.csv")
FPS = 24                 # frames per second
SEC_PER_TOUR = 4         # seconds per tour (uniform)
CUT_TOUR = 1             # after this tour only top-10 remain on plot

# ---- Load & normalize ----
df = pd.read_csv(CSV_PATH)
df.columns = [c.strip().lower() for c in df.columns]
df["tour"] = pd.to_numeric(df["tour"], errors="coerce")
df["points"] = pd.to_numeric(df["points"], errors="coerce")
df = df.dropna(subset=["tour"]).copy()
df["tour"] = df["tour"].astype(int)
df["points"] = df["points"].fillna(0.0).round(1)

# ---- Add (tour=0, points=0) for each player ----
players = sorted(df["nickname"].unique().tolist())
zero_rows = pd.DataFrame({"tour": 0, "nickname": players, "points": 0.0})
df = pd.concat([zero_rows, df], ignore_index=True)

# ---- Build cumulative table (player x tour) ----
tours = np.arange(df["tour"].min(), df["tour"].max() + 1)
wide = (
    df.pivot_table(index="nickname", columns="tour",
                   values="points", aggfunc="sum")
    .reindex(players)
    .reindex(columns=tours, fill_value=0.0)
)
cum = wide.cumsum(axis=1)

# Top-10 fixed after CUT_TOUR
cut_tour = min(CUT_TOUR, tours.max())
top10_after_cut = cum[cut_tour].sort_values(
    ascending=False).head(10).index.tolist()

# ---- Timing (uniform per tour); feel free to customize ----
frames_per_segment = int(FPS * SEC_PER_TOUR)
segment_starts = np.arange(0, frames_per_segment *
                           len(tours), frames_per_segment)
total_frames = frames_per_segment * len(tours)


def frame_to_frac_tour(gf: int) -> float:
    seg_idx = min(len(tours) - 1, gf // frames_per_segment)
    t0 = tours[seg_idx]
    if seg_idx == len(tours) - 1:
        return float(t0)
    within = gf - segment_starts[seg_idx]
    return t0 + within / max(1, frames_per_segment)


def interp_values(frac_tour: float) -> pd.Series:
    t_floor = int(np.floor(frac_tour))
    t_floor = int(np.clip(t_floor, tours.min(), tours.max()))
    if t_floor >= tours.max():
        return cum[tours.max()]
    w = frac_tour - t_floor
    t_next = t_floor + 1
    v0 = cum[t_floor]
    v1 = cum[t_next]
    return (1 - w) * v0 + w * v1


# ---- Figure ----
fig, ax = plt.subplots(figsize=(11, 6.5))
ax.set_xlabel("Tour")
ax.set_ylabel("Cumulative score")
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_xlim(tours.min(), tours.max())
ax.grid(True, alpha=0.2)

lines = {p: ax.plot([], [], lw=1.2, alpha=0.6)[0] for p in players}
name_labels = {}
standings_box = ax.text(
    1.02, 1.0, "", transform=ax.transAxes, va="top", ha="left",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
)
title_txt = ax.text(0.02, 1.02, "", transform=ax.transAxes,
                    va="bottom", ha="left")


def init():
    for ln in lines.values():
        ln.set_data([], [])
    for lbl in list(name_labels.values()):
        lbl.remove()
    name_labels.clear()
    standings_box.set_text("")
    title_txt.set_text("")
    return list(lines.values()) + [standings_box, title_txt]


def update(frame):
    frac = frame_to_frac_tour(frame)
    y_now = interp_values(frac)
    ax.set_ylim(0, max(1.0, float(y_now.max()) * 1.05))
    ax.set_xlim(max(tours.min(), frac - 1), min(tours.max(), frac + 1))

    current_tour_int = int(np.floor(frac))
    show_only_top10 = current_tour_int >= cut_tour

    # Current dynamic top-10 for styling/box
    current_top10 = y_now.sort_values(ascending=False).index[:10].tolist()
    visible_players = current_top10

    # Clear name labels
    for lbl in list(name_labels.values()):
        lbl.remove()
    name_labels.clear()

    # Draw lines with partial segment interpolation
    for p in players:
        ln = lines[p]
        t_floor = int(np.floor(frac))
        xs = list(tours[tours <= t_floor].astype(float))
        ys = list(cum.loc[p, tours[tours <= t_floor]].values if xs else [])
        if frac > t_floor and t_floor < tours.max():
            xs.append(float(frac))
            ys.append(y_now[p])

        if p in visible_players:
            ln.set_data(xs, ys)
            ln.set_alpha(0.9 if p in current_top10 else 0.35)
            ln.set_linewidth(2.2 if p in current_top10 else 1.2)
            ln.set_visible(True)
        else:
            ln.set_visible(False)

    # Labels above lines for current top-10
    for p in current_top10:
        xd, yd = lines[p].get_data()
        if not xd:
            continue
        name_labels[p] = ax.text(
            xd[-1], yd[-1], f" {p}", va="bottom", ha="left", fontsize=9)

    # Right-side standings box (current top-10 with scores at this moment)
    standings_text = "Top 10 (current)\n" + "\n".join(
        f"{p} — {y_now[p]:.1f}" for p in current_top10
    )
    standings_box.set_text(standings_text)

    title_txt.set_text(f"Tournament progress — tour {frac:.2f}/{tours.max()}")
    return list(lines.values()) + list(name_labels.values()) + [standings_box, title_txt]


ani = animation.FuncAnimation(
    fig, update, frames=total_frames, init_func=init, blit=False, interval=1000.0 / FPS
)

plt.close(fig)  # avoid duplicate static display in notebooks

# To display inline in Jupyter (HTML5 video), uncomment:
# from IPython.display import HTML
# HTML(ani.to_jshtml())  # or HTML(ani.to_html5_video())

# To save to file (MP4 via ffmpeg, else GIF):
out = Path("data/top10_race")
try:
    Writer = animation.writers["ffmpeg"]
    writer = Writer(fps=FPS, metadata=dict(artist="top10_race"), bitrate=2400)
    ani.save(out.with_suffix(".mp4"), writer=writer)
    print(f"Saved -> {out.with_suffix('.mp4')}")
except Exception as e:
    ani.save(out.with_suffix(".gif"), writer="pillow", fps=FPS)
    print(f"Saved -> {out.with_suffix('.gif')}")

# All comments/messages in code are in English only.
from pathlib import Path
# your file with parse_tournament
from fetch_tournament_results import parse_tournament
# your file with render_top10_race
from top10_race_min import render_top10_race


def make_tournament_video(url: str, out_basename: str | Path | None = None) -> Path:
    """Fetch tournament data from URL, save dataset and render animated video.

    Parameters
    ----------
    url : str
        Tournament page URL.
    out_basename : str | Path | None, default None
        Basename for output files. If None, uses og:title (snake_case).

    Returns
    -------
    Path
        Path to the saved video file (MP4 or GIF).
    """
    # Step 1: parse and save dataset
    rows, csv_path = parse_tournament(url, out_basename=out_basename)

    # Step 2: render video from dataset
    video_path = render_top10_race(
        csv_path, out_basename=csv_path.with_suffix(""))

    return video_path


if __name__ == "__main__":
    url = "https://imafia.org/tournament/493#tournament-results"
    saved_video = make_tournament_video(url)
    print(f"Saved video -> {saved_video}")

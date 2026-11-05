"""
Draw the diagrams of the QC item pages and the Getting Started tutorial.

Every flag shown in the item diagrams is computed by the real ``aiqclib`` QC
item class on a small synthetic profile, so the pictures cannot drift from
the implementation. Rerun after changing an item or its defaults:

    uv run python docs/diagrams/make_qc_diagrams.py

The SVG files are written to ``docs/source/_static/diagrams/`` and committed,
so the Read the Docs build needs neither this script nor matplotlib.
"""

from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("svg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

from aiqclib.common.loader.feature_registry import FEATURE_REGISTRY  # noqa: E402
from aiqclib.common.utils.seawater import sigma0  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "source" / "_static" / "diagrams"

PASS = "#2f6db3"
FAIL = "#c8382e"
SUSPECT = "#e0901c"
LINE = "#6b6b6b"
BAND = "#dcebd6"
BAND_EDGE = "#7aa86a"
BAND_2 = "#b5d6a7"
BOX = "#eef2f7"
BOX_EDGE = "#4a5a70"

plt.rcParams.update(
    {
        "svg.fonttype": "none",
        "svg.hashsalt": "nrtqclib",
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "legend.frameon": False,
    }
)


# -- helpers -----------------------------------------------------------------


def profile_frame(pres, profile_no=1, **columns) -> pl.DataFrame:
    """One synthetic profile with the key columns the QC items need."""
    n = len(pres)
    data = {
        "platform_code": ["DEMO"] * n,
        "profile_no": [profile_no] * n,
        "observation_no": list(range(1, n + 1)),
        "pres": [float(p) for p in pres],
    }
    for name, values in columns.items():
        data[name] = values
    return pl.DataFrame(data)


def run_item(item: str, df: pl.DataFrame, params=None) -> pl.DataFrame:
    """Compute an item's flag columns with the real aiqclib class."""
    feature_class = FEATURE_REGISTRY[f"qc_{item}"]
    ds = feature_class(feature_info={"params": params or {}}, filtered_input=df)
    return ds.compute_flags(df)


def flag_colours(flags) -> list:
    return [FAIL if f == 4 else SUSPECT if f == 3 else PASS for f in np.asarray(flags)]


def profile_axes(ax, xlabel, title=None):
    ax.invert_yaxis()
    ax.set_ylabel("Pressure (dbar)")
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)


def plot_profile(ax, values, pres, flags, label=None):
    ax.plot(values, pres, color=LINE, lw=1, zorder=1)
    ax.scatter(
        values,
        pres,
        c=flag_colours(flags),
        s=30,
        zorder=2,
        edgecolors="white",
        linewidths=0.6,
        label=label,
    )


def flag_legend(ax, loc="lower left", suspect=False, extra=(), above=False):
    handles = list(extra) + [
        plt.Line2D([], [], marker="o", ls="", color=PASS, label="pass (1)"),
        plt.Line2D([], [], marker="o", ls="", color=FAIL, label="fail (4)"),
    ]
    if suspect:
        handles.append(
            plt.Line2D([], [], marker="o", ls="", color=SUSPECT, label="flag 3")
        )
    if above:
        ax.legend(
            handles=handles,
            loc="lower center",
            bbox_to_anchor=(0.5, 1.02),
            ncol=len(handles),
            fontsize=9,
        )
    else:
        ax.legend(handles=handles, loc=loc, fontsize=9)


def save(fig, name: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        OUT_DIR / f"{name}.svg",
        bbox_inches="tight",
        metadata={"Date": None, "Creator": None},
    )
    plt.close(fig)
    print(f"wrote {name}.svg")


def box(ax, x, y, w, h, text, face=BOX, edge=BOX_EDGE, size=10, weight="normal"):
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            fc=face,
            ec=edge,
            lw=1.2,
        )
    )
    ax.text(x, y, text, ha="center", va="center", fontsize=size, weight=weight)


def arrow(ax, start, end, text=None, style="-|>", colour=BOX_EDGE, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=14,
            color=colour,
            lw=1.3,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=2,
            shrinkB=2,
        )
    )
    if text:
        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2 + 0.12,
            text,
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=LINE,
        )


def blank_axes(fig_w, fig_h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


# -- pipeline and aggregation ------------------------------------------------


def pipeline():
    fig, ax = blank_axes(9.5, 3.0, (0, 10), (0, 3.2))
    box(ax, 0.9, 2.2, 1.5, 0.8, "input\nParquet", face="#ffffff")
    box(ax, 3.0, 2.2, 1.7, 0.8, "1  input\nread, validate", weight="bold")
    box(ax, 5.2, 2.2, 1.7, 0.8, "2  qc\none column\nper item", weight="bold")
    box(
        ax, 7.4, 2.2, 1.7, 0.8, "3  concat\nfinal NRT flag\nper variable", weight="bold"
    )
    box(ax, 9.3, 2.2, 1.2, 0.8, "output\nParquet", face="#ffffff")
    box(ax, 7.4, 0.6, 1.7, 0.8, "4  compare\n(optional)", weight="bold")
    box(ax, 9.3, 0.6, 1.2, 0.8, "reports\nTSV", face="#ffffff")
    arrow(ax, (1.65, 2.2), (2.15, 2.2))
    arrow(ax, (3.85, 2.2), (4.35, 2.2))
    arrow(ax, (6.05, 2.2), (6.55, 2.2))
    arrow(ax, (8.25, 2.2), (8.7, 2.2))
    arrow(ax, (7.4, 1.8), (7.4, 1.0))
    arrow(ax, (8.25, 0.6), (8.7, 0.6))
    ax.text(5.2, 1.6, "qc/nrt_qc_flags.parquet", ha="center", fontsize=8.5, color=LINE)
    ax.text(
        9.3, 2.75, "nrt_qc/nrt_qc_output.parquet", ha="center", fontsize=8.5, color=LINE
    )
    ax.text(9.3, 0.05, "compare/*.tsv", ha="center", fontsize=8.5, color=LINE)
    ax.text(
        5.2,
        0.6,
        "existing flags\n(temp_qc, psal_qc)\nvs new flags",
        ha="center",
        va="center",
        fontsize=8.5,
        color=LINE,
    )
    arrow(ax, (6.0, 0.6), (6.55, 0.6), colour=LINE)
    save(fig, "pipeline")


def final_flag():
    fig, ax = blank_axes(9.5, 5.2, (0, 10), (0.2, 6.1))
    groups = [
        (
            "temperature items",
            ["temp_qc_global_range", "temp_qc_spike", "temp_qc_..."],
            5.4,
            "#fbe6e4",
        ),
        (
            "profile-level items (shared)",
            ["qc_impossible_date", "qc_pressure_increasing", "qc_..."],
            3.45,
            "#eeeeee",
        ),
        (
            "salinity items",
            ["psal_qc_global_range", "psal_qc_spike", "psal_qc_..."],
            1.5,
            "#e3edf8",
        ),
    ]
    ys = {}
    for title, names, y0, face in groups:
        ax.text(1.4, y0 + 0.35, title, ha="center", weight="bold", fontsize=9)
        ys[title] = []
        for i, name in enumerate(names):
            y = y0 - i * 0.45
            box(ax, 1.4, y, 2.3, 0.36, name, face=face, size=8.5)
            ys[title].append(y)

    temp_y, psal_y = 4.95, 1.05
    box(ax, 4.3, temp_y, 1.2, 0.6, "max", weight="bold")
    box(ax, 4.3, psal_y, 1.2, 0.6, "max", weight="bold")
    for y in ys["temperature items"]:
        arrow(ax, (2.6, y), (3.65, temp_y), colour=LINE)
    for y in ys["profile-level items (shared)"]:
        arrow(ax, (2.6, y), (3.65, temp_y), colour="#a9a9a9")
        arrow(ax, (2.6, y), (3.65, psal_y), colour="#a9a9a9")
    for y in ys["salinity items"]:
        arrow(ax, (2.6, y), (3.65, psal_y), colour=LINE)

    box(ax, 6.4, temp_y, 1.9, 0.6, "temp_nrt_flag", face="#ffffff", weight="bold")
    arrow(ax, (4.95, temp_y), (5.4, temp_y))
    box(ax, 6.4, 3.45, 2.2, 0.75, "temp_to_psal\nflag 3 or 4 copied", face="#fff4e0")
    arrow(ax, (6.4, temp_y - 0.32), (6.4, 3.85))
    box(ax, 6.4, 2.1, 2.2, 0.55, "psal_qc_temp_to_psal", face="#ffffff", size=8.5)
    arrow(ax, (6.4, 3.05), (6.4, 2.4))
    box(ax, 8.9, psal_y, 1.8, 0.6, "psal_nrt_flag", face="#ffffff", weight="bold")
    arrow(ax, (4.95, psal_y), (7.95, psal_y))
    arrow(ax, (7.0, 1.8), (8.4, 1.38))
    ax.text(8.9, 0.55, "max of both", ha="center", fontsize=8.5, color=LINE)
    save(fig, "final_flag")


# -- profile-level items ------------------------------------------------------


def impossible_date():
    now = datetime.now()
    stamps = [
        datetime(1949, 7, 1),
        datetime(1950, 8, 15),
        datetime(1951, 2, 1),
        datetime(1998, 5, 12),
        datetime(now.year - 1, 3, 1),
        datetime(now.year + 2, 1, 1),
        None,
    ]
    labels = ["1949", "1950", "1951", "1998", "last year", "future", "null"]
    df = pl.DataFrame(
        {
            "platform_code": ["DEMO"] * len(stamps),
            "profile_no": list(range(1, len(stamps) + 1)),
            "observation_no": [1] * len(stamps),
            "profile_timestamp": pl.Series(stamps, dtype=pl.Datetime("us")),
        }
    )
    flags = run_item("impossible_date", df)["qc_impossible_date"].to_list()

    # Schematic axis: evenly spaced, not to scale, so 1949 to 1951 stay apart.
    xs = np.arange(len(stamps), dtype=float)
    xs[-1] += 0.6
    fig, ax = plt.subplots(figsize=(8.5, 2.2))
    ax.axvspan(1.5, 4.5, color=BAND, zorder=0)
    ax.text(
        1.6,
        0.82,
        "valid: year > min_year (1950) and not in the future",
        fontsize=8.5,
        color="#3d6b30",
    )
    for x, flag, label in zip(xs, flags, labels):
        ax.scatter([x], [0.4], s=80, color=flag_colours([flag])[0], zorder=3)
        ax.text(x, 0.12, label, ha="center", va="top", fontsize=9)
    ax.axvline(4.5, color=BAND_EDGE, lw=1)
    ax.text(4.55, 0.6, "now", fontsize=8.5, color="#3d6b30")
    ax.set_xlim(-0.6, xs[-1] + 0.6)
    ax.set_ylim(-0.25, 1.0)
    ax.axis("off")
    flag_legend(ax, above=True)
    save(fig, "impossible_date")


def impossible_location():
    points = [
        (19.0, 58.0),
        (-30.0, -45.0),
        (150.0, 10.0),
        (182.0, 20.0),
        (-60.0, 91.0),
        (-170.0, -88.0),
        (-190.0, -60.0),
    ]
    df = pl.DataFrame(
        {
            "platform_code": ["DEMO"] * len(points),
            "profile_no": list(range(1, len(points) + 1)),
            "observation_no": [1] * len(points),
            "longitude": [p[0] for p in points],
            "latitude": [p[1] for p in points],
        }
    )
    flags = run_item("impossible_location", df)["qc_impossible_location"].to_list()
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    ax.add_patch(
        Rectangle((-180, -90), 360, 180, fc=BAND, ec=BAND_EDGE, lw=1.2, zorder=0)
    )
    ax.text(
        0,
        0,
        "lon in [-180, 180]\nlat in [-90, 90]",
        ha="center",
        va="center",
        color="#3d6b30",
    )
    for (lon, lat), flag in zip(points, flags):
        ax.scatter([lon], [lat], s=60, color=flag_colours([flag])[0], zorder=3)
        ax.annotate(
            f"({lon:g}, {lat:g})",
            (lon, lat),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_xlim(-215, 215)
    ax.set_ylim(-110, 110)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    flag_legend(ax, above=True)
    save(fig, "impossible_location")


def position_on_land():
    x = np.linspace(0, 10, 300)
    # Elevation in metres, positive above sea level: land on the left,
    # shoreline near x = 3, a shelf, then a slope into deep water.
    elevation = np.where(
        x < 3,
        40 * (3 - x) / 3,
        -np.clip((x - 3) * 25, 0, 60) - np.clip((x - 6) * 180, 0, 600),
    )
    stations = np.array([1.2, 3.0, 4.5, 8.5])
    station_elev = np.interp(stations, x, elevation).round()
    station_elev[1] = 0.0  # exactly on the shoreline
    bathymetry = -station_elev + 0.0  # positive_depth: True, ocean is > 0
    df = pl.DataFrame(
        {
            "platform_code": ["DEMO"] * 4,
            "profile_no": [1, 2, 3, 4],
            "observation_no": [1] * 4,
            "bathymetry": bathymetry,
        }
    )
    flags = run_item("position_on_land", df)["qc_position_on_land"].to_list()
    fig, ax = plt.subplots(figsize=(8.5, 3.4))
    ax.fill_between(x, elevation, -700, color="#d8c9a8", zorder=1)
    ax.fill_between(x, 0, elevation, where=elevation < 0, color="#d6e7f5", zorder=0)
    ax.axhline(0, color=PASS, lw=0.8, ls="--")
    ax.text(9.9, 8, "sea level", ha="right", fontsize=8.5, color=PASS)
    for sx, se, b, flag in zip(stations, station_elev, bathymetry, flags):
        ax.plot([sx, sx], [max(se, 0), 70], color=LINE, lw=0.8, ls=":")
        ax.scatter([sx], [70], s=70, color=flag_colours([flag])[0], zorder=3)
        ax.text(sx, 85, f"{b:.0f} m", ha="center", fontsize=8)
    ax.set_xlim(0, 10)
    ax.set_ylim(-700, 140)
    ax.set_xticks([])
    ax.set_xlabel(
        "Distance along a section (labels: the bathymetry column, positive_depth: true)"
    )
    ax.set_ylabel("Elevation (m)")
    flag_legend(ax, above=True)
    save(fig, "position_on_land")


def stuck_value():
    pres = np.arange(5, 105, 10)
    normal = 12 - 0.06 * pres + 0.3 * np.sin(pres / 9)
    stuck = np.full(len(pres), 7.3)
    df = pl.concat(
        [
            profile_frame(pres, 1, temp=normal, psal=np.full(len(pres), 7.0)),
            profile_frame(pres, 2, temp=stuck, psal=np.full(len(pres), 7.0)),
        ]
    )
    flags = run_item("stuck_value", df, {"psal": {}})
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.6), sharey=True)
    for ax, profile_no, title in zip(axes, (1, 2), ("varying sensor", "stuck sensor")):
        part = df.filter(pl.col("profile_no") == profile_no)
        f = flags.filter(pl.col("profile_no") == profile_no)["temp_qc_stuck_value"]
        plot_profile(ax, part["temp"], part["pres"], f)
        ax.set_title(title)
        ax.set_xlim(4, 13)
        ax.set_xlabel("Temperature (°C)")
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Pressure (dbar)")
    flag_legend(axes[1], loc="lower right")
    save(fig, "stuck_value")


# -- observation-level items ---------------------------------------------------


def global_and_regional_range():
    pres = np.arange(5, 205, 10)
    temp = 16 - 0.07 * pres
    temp[3] = 42.0
    temp[11] = 27.5
    psal = 6.8 + 0.01 * pres
    psal[7] = 1.2
    df = profile_frame(pres, temp=temp, psal=psal)
    glob = run_item("global_range", df)
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4.0), sharey=True)
    axes[0].axvspan(-2.5, 40, color=BAND, zorder=0)
    plot_profile(axes[0], temp, pres, glob["temp_qc_global_range"])
    axes[0].set_xlim(-6, 45)
    axes[0].set_xlabel("Temperature (°C)")
    axes[0].set_title("temp  [-2.5, 40.0]")
    axes[1].axvspan(2.0, 41, color=BAND, zorder=0)
    plot_profile(axes[1], psal, pres, glob["psal_qc_global_range"])
    axes[1].set_xlim(0, 12)
    axes[1].set_xlabel("Salinity")
    axes[1].set_title("psal  [2.0, 41.0]")
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Pressure (dbar)")
    flag_legend(axes[0], loc="lower right")
    save(fig, "global_range")

    regional_params = {"temp": {"min": -2.0, "max": 24.0}}
    reg = run_item("regional_range", df, regional_params)
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4.0), sharey=True)
    for ax, f, title in zip(
        axes,
        (glob["temp_qc_global_range"], reg["temp_qc_regional_range"]),
        ("global_range", "regional_range"),
    ):
        ax.axvspan(-2.5, 40, color=BAND, zorder=0)
        if title == "regional_range":
            ax.axvspan(-2.0, 24, color=BAND_2, zorder=0)
        plot_profile(ax, temp, pres, f)
        ax.set_xlim(-6, 45)
        ax.set_xlabel("Temperature (°C)")
        ax.set_title(title)
    axes[1].text(
        11, 195, "region\n[-2, 24]", ha="center", fontsize=8.5, color="#3d6b30"
    )
    axes[1].text(
        32, 195, "global\n[-2.5, 40]", ha="center", fontsize=8.5, color="#3d6b30"
    )
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Pressure (dbar)")
    flag_legend(axes[0], loc="lower right")
    axes[0].text(
        19, 195, "global\n[-2.5, 40]", ha="center", fontsize=8.5, color="#3d6b30"
    )
    save(fig, "regional_range")


def pressure_increasing():
    pres = [2, 6, 10, 14, 14, 14, 18, 22, 19, 16, 24, 28, 32]
    df = profile_frame(pres)
    flags = run_item("pressure_increasing", df)["qc_pressure_increasing"].to_numpy()
    obs = np.arange(1, len(pres) + 1)
    running_max = np.maximum.accumulate(pres)
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.step(
        obs,
        running_max,
        where="post",
        color=BAND_EDGE,
        lw=1,
        ls="--",
        label="running maximum of the previous pressures",
    )
    ax.plot(obs, pres, color=LINE, lw=1)
    ax.scatter(obs, pres, c=flag_colours(flags), s=40, zorder=3, edgecolors="white")
    ax.annotate(
        "constant run:\nall but the first fail",
        (5.5, 14),
        xytext=(1.0, 26),
        fontsize=8.5,
        arrowprops={"arrowstyle": "-", "color": LINE},
    )
    ax.annotate(
        "reversal: below the\nrunning maximum",
        (9.5, 17.5),
        xytext=(10.2, 8),
        fontsize=8.5,
        arrowprops={"arrowstyle": "-", "color": LINE},
    )
    ax.invert_yaxis()
    ax.set_xlabel("observation_no (order in the profile)")
    ax.set_ylabel("Pressure (dbar)")
    ax.set_xticks(obs)
    flag_legend(ax, extra=ax.get_legend_handles_labels()[0], above=True)
    save(fig, "pressure_increasing")


def _stencil_inset(ax, v, p, i, label_side=1):
    for k, name in zip((i - 1, i, i + 1), ("V1", "V2", "V3")):
        ax.annotate(
            name,
            (v[k], p[k]),
            xytext=(8 * label_side, 0),
            textcoords="offset points",
            fontsize=8.5,
            va="center",
        )


def spike():
    pres = np.arange(0, 1001, 50, dtype=float)
    temp = 4 + 12 * np.exp(-pres / 600)
    i_shallow, i_mid, i_deep = 3, 6, 15
    temp[i_shallow] += 4.5  # test value 4.5 < 6.0 shallow: passes
    temp[i_mid] += 7.0  # 7.0 > 6.0: fails
    temp[i_deep] += 2.6  # 2.6 > 2.0 deep: fails
    df = profile_frame(pres, temp=temp, psal=np.full(len(pres), 35.0))
    flags = run_item("spike", df)["temp_qc_spike"].to_numpy()
    v1 = np.roll(temp, 1)
    v3 = np.roll(temp, -1)
    test = np.abs(temp - (v3 + v1) / 2) - np.abs((v3 - v1) / 2)
    test[0] = test[-1] = np.nan

    fig, axes = plt.subplots(1, 2, figsize=(8.5, 4.4), sharey=True)
    plot_profile(axes[0], temp, pres, flags)
    _stencil_inset(axes[0], temp, pres, i_mid)
    axes[0].set_title("temperature profile")
    axes[0].set_xlabel("Temperature (°C)")
    axes[1].plot(test, pres, color=LINE, lw=1)
    axes[1].scatter(
        test, pres, c=flag_colours(flags), s=30, zorder=3, edgecolors="white"
    )
    axes[1].step(
        [6, 6, 2, 2], [0, 500, 500, 1000], where="post", color=FAIL, lw=1, ls="--"
    )
    axes[1].plot([6, 6], [0, 500], color=FAIL, lw=1, ls="--", label="threshold")
    axes[1].plot([2, 2], [500, 1000], color=FAIL, lw=1, ls="--")
    axes[1].axhline(500, color=LINE, lw=0.6, ls=":")
    axes[1].text(8.3, 490, "depth_threshold 500", fontsize=8, color=LINE, ha="right")
    axes[1].set_title("|V2 - (V3+V1)/2| - |(V3-V1)/2|")
    axes[1].set_xlabel("Spike test value (°C)")
    axes[1].set_xlim(-0.5, 8.5)
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Pressure (dbar)")
    flag_legend(axes[0], loc="lower right")
    save(fig, "spike")


def gradient():
    # Below depth_threshold, so the deep thresholds apply: 3.0 for gradient,
    # 2.0 for spike.
    pres = np.arange(520, 901, 20, dtype=float)
    temp = np.where(pres < 700, 12.0, 4.6) - 0.002 * pres
    temp[4] += 2.6  # a narrow spike: spike value 2.6, gradient value 2.6
    df = profile_frame(pres, temp=temp, psal=np.full(len(pres), 35.0))
    grad = run_item("gradient", df)["temp_qc_gradient"].to_numpy()
    spk = run_item("spike", df)["temp_qc_spike"].to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4.0), sharey=True)
    plot_profile(axes[0], temp, pres, grad)
    axes[0].set_title("gradient (deep threshold 3.0)")
    plot_profile(axes[1], temp, pres, spk)
    axes[1].set_title("spike (deep threshold 2.0)")
    for ax in axes:
        ax.set_xlabel("Temperature (°C)")
        ax.set_xlim(2, 15)
    axes[0].annotate(
        "sharp step",
        (7.5, 690),
        xytext=(9.5, 780),
        fontsize=8.5,
        arrowprops={"arrowstyle": "-", "color": LINE},
    )
    axes[1].annotate(
        "narrow spike",
        (temp[4], pres[4]),
        xytext=(4.5, 560),
        fontsize=8.5,
        arrowprops={"arrowstyle": "-", "color": LINE},
    )
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Pressure (dbar)")
    flag_legend(axes[1], loc="lower right")
    save(fig, "gradient")


def digit_rollover():
    pres = np.arange(5, 125, 10, dtype=float)
    temp = 14 - 0.05 * pres
    rolled = slice(4, 7)
    temp[rolled] -= 16.0  # stored values wrapped to the low end of the range
    df = profile_frame(pres, temp=temp, psal=np.full(len(pres), 35.0))
    flags = run_item("digit_rollover", df)["temp_qc_digit_rollover"].to_numpy()
    fig, ax = plt.subplots(figsize=(5.5, 4.0))
    plot_profile(ax, temp, pres, flags)
    ax.annotate(
        "jump > 10 °C\nfrom the previous value",
        (temp[4], pres[4]),
        xytext=(1.5, 22),
        fontsize=8.5,
        arrowprops={"arrowstyle": "-", "color": LINE},
    )
    ax.annotate(
        "jump back",
        (temp[7], pres[7]),
        xytext=(1.5, 92),
        fontsize=8.5,
        arrowprops={"arrowstyle": "-", "color": LINE},
    )
    ax.annotate(
        "inside the wrapped run:\nno jump, so it passes",
        (temp[5], pres[5]),
        xytext=(-5.5, 128),
        fontsize=8.5,
        arrowprops={"arrowstyle": "-", "color": LINE},
    )
    profile_axes(ax, "Temperature (°C)")
    ax.set_ylim(135, -5)
    flag_legend(ax, loc="lower right")
    save(fig, "digit_rollover")


def density_inversion():
    pres = np.arange(0, 201, 20, dtype=float)
    temp = 15 - 0.04 * pres
    psal = 34.5 + 0.004 * pres
    temp[5] += 1.5  # a warm, light layer under a colder one
    df = profile_frame(pres, temp=temp, psal=psal)
    flags = run_item("density_inversion", df)["temp_qc_density_inversion"].to_numpy()
    sig = np.asarray(sigma0(df["psal"], df["temp"], df["pres"]))
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4.0), sharey=True)
    plot_profile(axes[0], temp, pres, flags)
    axes[0].set_xlabel("Temperature (°C)")
    axes[0].set_title("temperature")
    plot_profile(axes[1], sig, pres, flags)
    axes[1].set_xlabel("sigma-0 (kg/m³)")
    axes[1].set_title("potential density")
    axes[1].annotate(
        "lighter than the level above:\nboth levels of the pair fail",
        (sig[5], pres[5]),
        xytext=(sig.min() - 0.05, 160),
        fontsize=8.5,
        arrowprops={"arrowstyle": "-", "color": LINE},
    )
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Pressure (dbar)")
    flag_legend(axes[1], loc="upper right")
    save(fig, "density_inversion")


def temp_to_psal():
    temp_nrt = [1, 1, 4, 3, 1]
    df = pl.DataFrame(
        {
            "platform_code": ["DEMO"] * 5,
            "profile_no": [1] * 5,
            "observation_no": [1, 2, 3, 4, 5],
            "temp_nrt_flag": temp_nrt,
        }
    )
    out = run_item("temp_to_psal", df)["psal_qc_temp_to_psal"].to_list()
    fig, ax = blank_axes(6.0, 3.2, (0, 6), (-0.2, 3.4))
    ax.text(1.2, 3.15, "temp_nrt_flag", ha="center", weight="bold", fontsize=9)
    ax.text(4.6, 3.15, "psal_qc_temp_to_psal", ha="center", weight="bold", fontsize=9)
    colours = {1: "#dbe7f5", 3: "#fbe3c2", 4: "#f5c9c5"}
    for i, (src, dst) in enumerate(zip(temp_nrt, out)):
        y = 2.65 - i * 0.6
        box(ax, 1.2, y, 1.0, 0.42, str(src), face=colours[src], size=10, weight="bold")
        box(ax, 4.6, y, 1.0, 0.42, str(dst), face=colours[dst], size=10, weight="bold")
        label = "copied" if src in (3, 4) else "1 (no propagation)"
        arrow(ax, (1.75, y), (4.05, y), colour=FAIL if src in (3, 4) else LINE)
        ax.text(2.9, y + 0.07, label, ha="center", va="bottom", fontsize=8, color=LINE)
    save(fig, "temp_to_psal")


def main():
    pipeline()
    final_flag()
    impossible_date()
    impossible_location()
    position_on_land()
    stuck_value()
    global_and_regional_range()
    pressure_increasing()
    spike()
    gradient()
    digit_rollover()
    density_inversion()
    temp_to_psal()


if __name__ == "__main__":
    main()

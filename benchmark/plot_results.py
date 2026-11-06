# ------------------------------------------------------------------------------
# rpi-object-detection
# ------------------------------------------------------------------------------
# Draws the processing FPS results as a grouped bar chart: one group per
# example, one bar per board, on a log scale (the results span 0.5 to 2,000+
# FPS).
#
# The results are read from a CSV file (default: benchmark/results.csv), with
# one row per example and one column per board. A cell is a number (FPS), the
# number followed by "gpu" when it ran on the GPU, "oom" when the example ran
# out of memory, or empty when it was not measured.
#
# Usage (from the repository root, with the venv activated):
#   python3 benchmark/plot_results.py                     # light and dark PNGs
#   python3 benchmark/plot_results.py --theme light --out chart.png
#   python3 benchmark/plot_results.py --csv my_results.csv
# ------------------------------------------------------------------------------
# automaticdai
# YF Robotics Laboratory
# Instagram: yfrobotics
# Twitter: @yfrobotics
# Website: https://yfrobotics.github.io/
# ------------------------------------------------------------------------------

import argparse
import csv
import os
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CSV = os.path.join(ROOT_DIR, 'benchmark', 'results.csv')
DEFAULT_OUT = os.path.join(ROOT_DIR, 'images', 'benchmark_fps.png')

# Colors per theme. The board colors are a fixed categorical order (a board
# keeps its color whatever the other columns are), checked for color-blind
# separation on each theme's background.
THEMES = {
    'light': {
        'surface': '#fcfcfb', 'text': '#0b0b0b', 'muted': '#52514e', 'grid': '#e4e3df',
        'series': ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4'],
    },
    'dark': {
        'surface': '#1a1a19', 'text': '#f0efec', 'muted': '#c3c2b7', 'grid': '#33332f',
        'series': ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181'],
    },
}

BASELINE = 0.3   # bars grow from here on the log axis (just below the slowest result)


def read_results(path):
    """Return (boards, rows), where rows are (example, [(fps or None, note), ...])."""
    with open(path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        boards = header[1:]
        rows = []
        for line in reader:
            if not line or not line[0].strip():
                continue
            cells = []
            for cell in line[1:]:
                cell = cell.strip().lower()
                if not cell:
                    cells.append((None, ''))
                elif cell == 'oom':
                    cells.append((None, 'oom'))
                elif cell.endswith('gpu'):
                    cells.append((float(cell[:-3]), 'gpu'))
                else:
                    cells.append((float(cell), ''))
            rows.append((line[0].strip(), cells))
    if len(boards) > len(THEMES['light']['series']):
        raise SystemExit('At most {} boards are supported'.format(len(THEMES['light']['series'])))
    return boards, rows


def fps_label(value, _pos=None):
    if value >= 1:
        return '{:,.0f}'.format(value)
    return '{:g}'.format(value)


def draw(boards, rows, theme, out_path):
    t = THEMES[theme]
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Inter', 'Helvetica', 'Arial', 'DejaVu Sans'],
        'font.size': 10,
        'text.color': t['text'],
        'axes.labelcolor': t['muted'],
        'xtick.color': t['muted'],
        'ytick.color': t['muted'],
    })

    n_boards = len(boards)
    group_width = 0.8
    slot = group_width / n_boards
    bar_width = slot * 0.84           # leaves a gap of background between bars

    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=150)
    fig.patch.set_facecolor(t['surface'])
    ax.set_facecolor(t['surface'])

    for b, board in enumerate(boards):
        color = t['series'][b]
        for g, (_example, cells) in enumerate(rows):
            fps, note = cells[b]
            x = g - group_width / 2 + slot * (b + 0.5)
            if fps is not None:
                ax.bar(x, fps - BASELINE, bottom=BASELINE, width=bar_width, color=color,
                       linewidth=0, zorder=3, label=board if g == 0 else None)
                if note == 'gpu':
                    ax.annotate('{:g} FPS\nGPU'.format(fps), (x, fps), xytext=(0, 4),
                                textcoords='offset points', ha='center', va='bottom',
                                fontsize=8, color=t['text'], fontweight='bold')
            elif note == 'oom':
                ax.annotate('out of\nmemory', (x, BASELINE), xytext=(0, 4),
                            textcoords='offset points', ha='center', va='bottom',
                            fontsize=7, color=t['muted'], rotation=90)
        # Keep the legend entry even if the first example has no result
        if all(cells[b][0] is None for _e, cells in rows[:1]):
            ax.bar(0, 0, width=0, color=color, label=board)

    ax.set_yscale('log')
    top = max(c[0] for _e, cells in rows for c in cells if c[0] is not None)
    ax.set_ylim(BASELINE, top * 2.2)
    ticks = [v for v in (0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000)
             if BASELINE <= v <= top * 2.2]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(fps_label))
    ax.set_ylabel('Processing FPS (log scale, higher is better)')

    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([textwrap.fill(e, 16, break_on_hyphens=False, break_long_words=False) for e, _c in rows], fontsize=9)
    ax.set_xlim(-0.55, len(rows) - 0.45)

    ax.grid(axis='y', color=t['grid'], linewidth=0.8, zorder=0)
    ax.tick_params(axis='both', length=0)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color(t['grid'])

    ax.set_title('Processing FPS per example, same 640x480 clip on every board',
                 loc='left', fontsize=12, fontweight='bold', color=t['text'], pad=34)
    legend = ax.legend(loc='lower left', bbox_to_anchor=(0, 1.0), ncol=n_boards, frameon=False,
                       handlelength=1.0, handleheight=1.0, columnspacing=1.6, fontsize=9)
    for text in legend.get_texts():
        text.set_color(t['text'])

    fig.tight_layout()
    fig.savefig(out_path, facecolor=t['surface'])
    plt.close(fig)
    print('Saved', out_path)


def main():
    parser = argparse.ArgumentParser(description='Draw the benchmark results as a grouped bar chart.')
    parser.add_argument('--csv', default=DEFAULT_CSV, help='results file (default: %(default)s)')
    parser.add_argument('--out', default=DEFAULT_OUT,
                        help='output PNG; with --theme both, "_dark" is added for the dark one '
                             '(default: %(default)s)')
    parser.add_argument('--theme', choices=['light', 'dark', 'both'], default='both',
                        help='color theme (default: %(default)s)')
    args = parser.parse_args()

    boards, rows = read_results(args.csv)
    themes = ['light', 'dark'] if args.theme == 'both' else [args.theme]
    for theme in themes:
        out = args.out
        if args.theme == 'both' and theme == 'dark':
            root, ext = os.path.splitext(args.out)
            out = root + '_dark' + ext
        draw(boards, rows, theme, out)


if __name__ == '__main__':
    main()

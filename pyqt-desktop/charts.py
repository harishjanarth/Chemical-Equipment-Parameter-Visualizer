
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setMinimumHeight(240)

    def clear(self):
        self.figure.clf()
        self.ax = self.figure.add_subplot(111)
        self.draw()


def _autopct_counts(sizes):
    total = sum(sizes)
    def inner(pct):
        val = int(round(pct * total / 100.0))
        return str(val)
    return inner


def plot_type_distribution(canvas: MplCanvas, dist: dict):
    canvas.clear()
    ax = canvas.ax

    
    ax.set_title("Equipment Type Distribution", fontsize=14, fontweight="bold")

    if not dist:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        canvas.draw()
        return

    labels = list(dist.keys())
    sizes = list(dist.values())

    palette = ["#ffb300", "#42a5f5", "#ef5350", "#8e24aa",
               "#ffa726", "#8d6e63", "#26a69a", "#5c6bc0"]
    colors = [palette[i % len(palette)] for i in range(len(labels))]

    ax.pie(
        sizes,
        labels=labels,
        autopct=_autopct_counts(sizes),
        pctdistance=0.75,
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor="white")
    )

    ax.axis("equal")
    canvas.draw()


def plot_correlation_heatmap(canvas: MplCanvas, corr: dict):
    canvas.clear()
    ax = canvas.ax

    ax.set_title("Correlation Heatmap", fontsize=14, fontweight="bold")

    if not corr:
        ax.text(0.5, 0.5, "No correlation data", ha="center", va="center")
        canvas.draw()
        return

    keys = ["Flowrate", "Pressure", "Temperature"]
    N = len(keys)
    M = np.zeros((N, N))

    for i, r in enumerate(keys):
        for j, c in enumerate(keys):
            try:
                M[i, j] = float(corr.get(r, {}).get(c, 0))
            except:
                M[i, j] = 0.0

    im = ax.imshow(M, cmap="RdYlBu_r", vmin=-1, vmax=1)

    for i in range(N):
        for j in range(N):
            ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center", color="black", fontsize=9)

    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    ax.set_xticklabels(keys, rotation=30)
    ax.set_yticklabels(keys)

    canvas.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    canvas.draw()

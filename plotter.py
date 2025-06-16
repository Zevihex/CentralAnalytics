import io
import base64
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib
import numpy as np
import pandas as pd
matplotlib.use('Agg')


def truncate_colormap(cmap, minval=0.2, maxval=0.85, n=256):
  """Trim a colormap to remove overly light or dark extremes."""
  new_cmap = LinearSegmentedColormap.from_list(
      f'trunc({cmap.name},{minval:.2f},{maxval:.2f})',
      cmap(np.linspace(minval, maxval, n))
  )
  return new_cmap

def generate_ARR_plot(df):

  df = df.dropna(subset=["game", "rank_weight"])
  x_labels = df["game"].tolist()
  y_values = (65 - df["rank_weight"]).tolist()

  fig, ax = plt.subplots(figsize=(20, 5))
  bar_width = 0.8
  spacing = 1.0
  gradient = np.linspace(0, 1, 256).reshape(256, 1)
  cmap = truncate_colormap(plt.get_cmap("Blues"), 0.2, 0.85)
  for i, height in enumerate(y_values):
    bar_x = i * spacing
    bar_y = 0
    bar_height = height

    ax.imshow(
        gradient,
        extent=[bar_x, bar_x + bar_width, bar_y, bar_y + bar_height],
        aspect='auto',
        cmap=cmap,
        origin='lower'
      )

  ax.set_xlim(0, len(x_labels))
  ax.set_ylim(0, max(y_values) + 5)
  ax.set_xticks([i * spacing + bar_width / 2 for i in range(len(x_labels))])
  ax.set_xticklabels(x_labels, rotation=45, ha="right")
  ax.set_ylabel("Average Rank Rating")
  ax.set_title("Average Rank Per Game")

  buf = io.BytesIO()
  fig.tight_layout()
  fig.savefig(buf, format='png')
  buf.seek(0)
  encoded = base64.b64encode(buf.read()).decode('utf-8')
  buf.close()
  plt.close(fig)

  return encoded

def generate_pie(labels, sizes, title="Achievements By Platform", threshold_pct=5):
  total = sum(sizes)

  fig, ax = plt.subplots()
  colors = ["#08306b", "#08519c", "#2171b5", "#6baed6", "#c6dbef"]

  if total == 0:
    ax.pie(
      [1],
      labels=["No Achievements"],
      startangle=90,
      colors=["#d3d3d3"]
    )
  else:
    display_labels = [
      label if (size / total) * 100 >= threshold_pct else ''
      for label, size in zip(labels, sizes)
    ]

    def filtered_autopct(pct):
      return f"{int(round(pct * total / 100))} ({pct:.1f}%)" if pct >= threshold_pct else ""

    wedges, texts, autotexts = ax.pie(
      sizes,
      labels=display_labels,
      startangle=90,
      autopct=filtered_autopct,
      colors=colors[:len(sizes)],
    )

    for autotext in autotexts:
      autotext.set_color("white")
      autotext.set_fontweight("bold")

    for text in texts + autotexts:
      text.set_fontsize(9)

  ax.axis("equal")
  ax.set_title(title)

  buf = io.BytesIO()
  fig.savefig(buf, format="png", bbox_inches="tight")
  buf.seek(0)
  encoded = base64.b64encode(buf.read()).decode("utf-8")
  buf.close()
  plt.close(fig)

  return encoded


def generate_plot(df):
  if df.empty or "date" not in df or "date_count" not in df:
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=14)
    ax.axis("off")
  else:
    df = df.dropna(subset=["date", "date_count"]).copy()
    df["date"] = pd.to_datetime(df["date"], errors='coerce')
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")

    x = df["date"]
    y = df["date_count"]

    fig, ax = plt.subplots(figsize=(20, 5))
    ax.plot(x, y, marker='o', linestyle='-', color='midnightblue')

    ax.set_xlabel("Date")
    ax.set_ylabel("# of Records Per Week")
    ax.set_title("Total Activity Per Week")
    ax.set_ylim(bottom=0)
    ax.grid(True)

    ax.set_xticks(x)
    ax.set_xticklabels(["Week: " + date.strftime("%Y-%m-%d") for date in x], rotation=45, ha='right')

  fig.tight_layout()
  buf = io.BytesIO()
  fig.savefig(buf, format="png", bbox_inches="tight")
  buf.seek(0)
  encoded = base64.b64encode(buf.read()).decode("utf-8")
  buf.close()
  plt.close(fig)
  return encoded

def generate_heatmap(df, row_col="game", col_col="category", value_col="position", title="Position Heatmap"):

  pivot = df.pivot(index=row_col, columns=col_col, values=value_col)
  fig, ax = plt.subplots(figsize=(20, 5))
  cmap = plt.get_cmap("hot_r")
  cax = ax.imshow(pivot.values, cmap=cmap, aspect="auto", origin="lower", vmin=0, vmax=1500)

  ax.set_xticks(np.arange(len(pivot.columns)))
  ax.set_yticks(np.arange(len(pivot.index)))
  ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
  ax.set_yticklabels(pivot.index)

  cbar = fig.colorbar(cax, ax=ax)
  cbar.set_label(value_col)
  cbar.ax.invert_yaxis()
  ax.set_title(title)

  fig.tight_layout()
  buf = io.BytesIO()
  fig.savefig(buf, format="png", bbox_inches="tight")
  buf.seek(0)
  encoded = base64.b64encode(buf.read()).decode("utf-8")
  buf.close()
  plt.close(fig)

  return encoded

def generate_hexbin(df):

  df["rank_weight"] = pd.to_numeric(df["rank_weight"], errors="coerce")
  df = df.dropna(subset=["track", "rank_weight"])

  if df.empty:
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.text(0.5, 0.5, "No Rank Weight Data Available For This Game", fontsize=14, ha='center', va='center')
    ax.axis("off")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return encoded

  track_to_int = {track: i for i, track in enumerate(df["track"].unique())}
  x = df["track"].map(track_to_int)
  y = df["rank_weight"]

  fig, ax = plt.subplots(figsize=(30, 15))
    
  hb = ax.hexbin(x, y, gridsize=(len(track_to_int), 10), cmap="plasma", 
    extent=(0, len(track_to_int), 0, 65), mincnt=1)

  ax.set_xlabel("Track")
  ax.set_ylabel("Rank Weight")
  ax.set_title("Hexbin of Rank Weights by Track")
    
  ax.set_xticks(list(track_to_int.values()))
  ax.tick_params(axis='x', labelsize=10)
  ax.set_xticklabels(list(track_to_int.keys()), rotation=90, fontsize=8)
  ax.set_ylim(0, 65)

  cbar = fig.colorbar(hb, ax=ax)
  cbar.set_label("Count")

  fig.tight_layout()
  buf = io.BytesIO()
  fig.savefig(buf, format="png", bbox_inches="tight")
  buf.seek(0)
  encoded = base64.b64encode(buf.read()).decode("utf-8")
  buf.close()
  plt.close(fig)

  return encoded




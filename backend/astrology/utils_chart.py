import io
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# South-Indian fixed sign layout: (row, col) in a 4x4 grid
SIGN_TO_CELL = {
    1:(0,0), 2:(0,1), 3:(0,2), 4:(0,3),
    5:(1,3), 6:(2,3), 7:(3,3), 8:(3,2),
    9:(3,1), 10:(3,0), 11:(2,0), 12:(1,0)
}

def _cell_xy(row:int, col:int, cell:float)->Tuple[float,float]:
    return col*cell, (3-row)*cell  # y from bottom

def render_south_indian_chart(
    houses: Dict[int, List[str]],
    title: str = "RASI",
    tamil: bool = False,
    figsize: Tuple[float,float]=(5.5,5.5),
    cell_size: float = 1.0,
    facecolor: str = "#FFFBEA",   # pale background (optional)
    bordercolor: str = "#333333"
) -> bytes:
    """
    Returns PNG bytes. 'houses' keys are 1..12 (signs). Values are list of labels (e.g., ['Asc','Sun','Moon']).
    """
    fig = plt.figure(figsize=figsize, dpi=200)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.axis('off')
    total = cell_size*4

    # outer border
    ax.add_patch(Rectangle((0,0), total, total, fill=True, facecolor=facecolor, edgecolor=bordercolor, lw=1.5))

    # draw 4x4 grid, leaving 2x2 center visually empty
    for r in range(4):
        for c in range(4):
            # skip center squares? we still draw thin borders so it matches the style
            x,y = _cell_xy(r,c,cell_size)
            ax.add_patch(Rectangle((x,y), cell_size, cell_size, fill=False, edgecolor=bordercolor, lw=1.0))

    # Title in center 2x2
    ax.text(total/2, total/2, title.upper(), ha='center', va='center', fontsize=13, fontweight='bold')

    # write planets per fixed sign cell
    for sign in range(1,13):
        row, col = SIGN_TO_CELL[sign]
        x,y = _cell_xy(row,col,cell_size)
        labels = houses.get(sign, [])
        if not labels: 
            continue

        # Make 'Asc' stand out and put it in a corner as a diagonal cue
        asc = [t for t in labels if t.lower() in ("asc","lagna","லக்")]
        planets = [t for t in labels if t not in asc]

        # Planets stacked
        txt = "\n".join(planets)
        ax.text(x+cell_size*0.07, y+cell_size*0.1, txt, ha='left', va='bottom', fontsize=9, wrap=True)

        # Lagna marker (diagonal)
        if asc:
            ax.text(x+cell_size*0.82, y+cell_size*0.15, asc[0], ha='center', va='center', rotation=330, fontsize=8, fontstyle='italic')

        # (optional) sign number watermark
        ax.text(x+cell_size*0.92, y+cell_size*0.88, str(sign), ha='center', va='center', fontsize=7, alpha=0.55)

    # export
    buf = io.BytesIO()
    plt.tight_layout(pad=0.3)
    fig.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    return buf.getvalue()

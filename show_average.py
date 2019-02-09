import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.patches as patches
import mpl_toolkits.axes_grid1

# 押した時
def Press(event):
    global T
    # 値がNoneなら終了
    if (event.xdata is None) or (event.ydata is None):
        return 

    reset()
    # 丸める
    cx = int(round(event.xdata))
    cy = int(round(event.ydata))

    store['xy1'] = (cx, cy)
    xy1 = store['xy1']

    execute(T, xy1, xy1)

    # x1 = cx
    # y1 = cy

    # フラグをたてる
    store['drag_flag'] = True

# ドラッグした時
def Drag(event):
    global T

    # ドラッグしていなければ終了
    if store['drag_flag'] == False:
        return

    # 値がNoneなら終了
    if (event.xdata is None) or (event.ydata is None):
        return 

    # 丸める
    cx = int(round(event.xdata))
    cy = int(round(event.ydata))

    store['xy2'] = (cx, cy)
    xy1 = store['xy1']
    xy2 = store['xy2']
    x1, y1 = xy1
    x2, y2 = xy2

    # ソート
    ix1, ix2 = sorted([x1,x2])
    iy1, iy2 = sorted([y1,y2])

    execute(T, (ix1, iy1), (ix2, iy2))

# 離した時
def Release(event):
    # フラグをたおす
    store['drag_flag'] = False

# 実行
def execute(T, xy1, xy2):
    ix1, iy1 = xy1
    ix2, iy2 = xy2
    # 前のやつ消す
    while store['text_obj']:
        store['text_obj'].pop().remove()
    cT = T[iy1: iy2+1, ix1: ix2+1]
    data = np.average(cT)
    data_text = f'{data:.2}'
    print(f'({ix1}, {iy1}) ({ix2}, {iy2})')
    print(cT)

    # 平均値を更新
    text_obj = ax2.text(0, data, data_text, va='center', ha='right')
    store['text_obj'].append(text_obj)

    # 四角形を更新
    r = patches.Rectangle((ix1-0.5, iy1-0.5),width=ix2-ix1+1, height=iy2-iy1+1, ec='r', fill=False, lw=3)
    ax1.add_patch(r)

    # 前のやつ消す
    while store['rect_obj']:
        store['rect_obj'].pop().remove()
    # 描画
    fig.canvas.draw()
    store['rect_obj'].append(r)


def reset():
    rect_obj = store['rect_obj']
    while rect_obj:
        rect_obj.pop().remove()
    text_obj = store['text_obj']
    while text_obj:
        text_obj.pop().remove()
    store['count'] = 0
    store['xy1'] = (0, 0)
    store['xy2'] = (0, 0)



# -------------------- main

from plot import load_DAT, convert_UVT, normarize
from itertools import product


# 共有値を貯める
store = {}
store['rect_obj'] = [] 
store['text_obj'] = []
store['count'] = 0
store['xy1'] = (0, 0)
store['xy2'] = (1, 1)
store['drag_flag'] = False

# plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100)

X, Y, U, V, T = load_DAT('./out_200.dat')

U = normarize(U, -1, 1)
V = normarize(V, -1, 1)

U, V, T = convert_UVT(U, V, T)

# 画像を描画
heatmap = ax1.imshow(T, cmap='jet', vmin=-0.5, vmax=0.5)
divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax1)
cax = divider.append_axes('right', '5%', pad='3%')
cbar = fig.colorbar(heatmap, cax=cax)
ux_size, uy_size = U.shape[1], V.shape[0]
for x,y in product(range(ux_size), range(uy_size)):
    dx, dy = U[y, x], V[y, x]
    if dx or dy:
        ax1.arrow(x, y, dx, -dy, color='k', 
                 head_width=0.1, length_includes_head=True)

# 軸を消す
ax1.tick_params(labelbottom=False, bottom=False) # x軸の削除
ax1.tick_params(labelleft=False, left=False) # y軸の削除
ax1.set_xticklabels([]) 
ax2.plot()
ax2.set_ylim(-0.5, 0.5)
ax2.set_xlim(0, 1)

# 軸を消す
ax2.axis('off')

# イベント
fig.canvas.mpl_connect('button_press_event', Press)
fig.canvas.mpl_connect('motion_notify_event', Drag)
fig.canvas.mpl_connect('button_release_event', Release)

fig.tight_layout()
plt.show()

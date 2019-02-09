import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.patches as patches
import mpl_toolkits.axes_grid1
from plot import load_DAT, convert_UVT, normarize
from itertools import product


class mouse_event:
    def __init__(self, fig, ax1, ax2, T):
        self.fig = fig
        self.ax1 = ax1
        self.ax2 = ax2
        self.T = T

        self.rect_obj = []
        self.text_obj = []
        self.count = 0
        self.xy1 = (0, 0)
        self.xy2 = (0, 0)
        self.drag_flag = False


    def reset(self):
        ro = self.rect_obj
        while ro:
            ro.pop().remove()
        to = self.text_obj
        while to:
            to.pop().remove()
        self.count = 0
        self.xy1 = (0, 0)
        self.xy2 = (0, 0)
        self.drag_flag = False


    def press(self, event):
        T = self.T
        # 値がNoneなら終了
        if (event.xdata is None) or (event.ydata is None):
            return 

        self.reset()
        # 丸める
        cx = int(round(event.xdata))
        cy = int(round(event.ydata))

        xy1 = (cx, cy)
        self.xy1 = xy1

        # 描画
        self.execute(T, xy1, xy1)

        # 押してるフラグをセット
        self.drag_flag = True

    
    def drag(self, event):
        T = self.T
    
        # ドラッグしていなければ終了
        if not self.drag_flag:
            return
    
        # 値がNoneなら終了
        if (event.xdata is None) or (event.ydata is None):
            return 
    
        # 丸める
        cx = int(round(event.xdata))
        cy = int(round(event.ydata))
    
        xy2 = (cx, cy)
        self.xy2 = xy2
        xy1 = self.xy1
        x1, y1 = xy1
        x2, y2 = xy2
    
        # ソート
        ix1, ix2 = sorted([x1,x2])
        iy1, iy2 = sorted([y1,y2])
    
        # 描画
        self.execute(T, (ix1, iy1), (ix2, iy2))


    def release(self, event):
        # フラグをFalse
        self.drag_flag = False


    def execute(self, T, xy1, xy2):
        fig = self.fig
        ax1 = self.ax1
        ax2 = self.ax2
        ix1, iy1 = xy1
        ix2, iy2 = xy2

        # 前のやつ消す
        while self.text_obj:
            self.text_obj.pop().remove()
        cT = T[iy1: iy2+1, ix1: ix2+1]
        data = np.average(cT)
        data_text = f'{data:.2}'
        print(f'({ix1}, {iy1}) ({ix2}, {iy2})')
        print(cT)
    
        # 平均値を更新
        text_obj = ax2.text(0, data, data_text, va='center', ha='right')
        self.text_obj.append(text_obj)
    
        # 四角形を更新
        r = patches.Rectangle((ix1-0.5, iy1-0.5), width=ix2-ix1+1, height=iy2-iy1+1, 
                              ec='r', fill=False, lw=3)
        ax1.add_patch(r)
    
        # 前のやつ消す
        while self.rect_obj:
            self.rect_obj.pop().remove()
        fig.canvas.draw()
        self.rect_obj.append(r)


def average_checker(dat_fname, vmin=-0.5, vmax=0.5, arrow_color='k', dpi=100):
    
    X, Y, U, V, T = load_DAT(argv[1])
    
    U = normarize(U, -1, 1)
    V = normarize(V, -1, 1)
    
    U, V, T = convert_UVT(U, V, T)
    
    # 画像を描画
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=dpi)
    heatmap = ax1.imshow(T, cmap='jet', vmin=vmin, vmax=vmax)
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
    ax2.set_ylim(vmin, vmax)
    ax2.set_xlim(0, 1)
    
    # 軸を消す
    ax2.axis('off')
    
    # イベント
    event_class = mouse_event(fig, ax1, ax2, T)
    fig.canvas.mpl_connect('button_press_event', event_class.press)
    fig.canvas.mpl_connect('motion_notify_event', event_class.drag)
    fig.canvas.mpl_connect('button_release_event', event_class.release)
    
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    from sys import argv
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='DAT file name')
    parser.add_argument('--arrow_color', '-ac', default='black')
    parser.add_argument('--vmax', type=float, default=-0.5)
    parser.add_argument('--vmin', type=float, default=0.5)
    parser.add_argument('--dpi', type=int, default=100)
    args = parser.parse_args()

    average_checker(args.filename, args.vmin, args.vmax,
                    args.arrow_color, args.dpi)

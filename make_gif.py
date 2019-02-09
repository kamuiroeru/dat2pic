from PIL import Image
from os.path import isdir
from glob import glob
import re
from plot import load_DAT, convert_UVT, normarize
import animatplot as amp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict
import mpl_toolkits.axes_grid1
plt.rcParams['font.size'] = 16


def sort_function(s: str) -> int:
    digit_strings = re.findall('\d+', s)
    if digit_strings:
        return int(''.join(digit_strings))
    else:
        return -1


def pic2gif(filequery='*.png', output_filename='sample.gif', fps=10):
    pnglist = sorted(glob(filequery), key=sort_function)
    images = [Image.open(fname) for fname in pnglist]

    images[0].save(output_filename, save_all=True, append_images=images[1:], optimize=False, duration=1000/fps, loop=0)


class dat:
    def __init__(self, filequery='*.dat', columns='XYUVT'):
        d = defaultdict(list)  # XYUVTのデータを入れる辞書

        datlist = sorted(glob(filequery), key=sort_function)
        for fname in datlist:
            X, Y, U, V, T = load_DAT(fname, columns)

            U = normarize(U, -1, 1)
            V = normarize(V, -1, 1)

            U, V, T = convert_UVT(U, V, T)

            d['X'].append(X)
            d['Y'].append(Y)
            d['U'].append(U)
            d['V'].append(V)
            d['T'].append(T)

        U3d = np.stack(d['U'], axis=2)
        V3d = np.stack(d['V'], axis=2)
        X = np.arange(U3d.shape[0])
        Y = np.arange(U3d.shape[1])

        self.datlist = datlist
        self.XYUVT = dict(d)
        self.X, self.Y = X, Y
        self.U3d, self.V3d = U3d, V3d


    def to_gif(self, vmin=None, vmax=None, fps=10, dpi=100):
        datlist = self.datlist
        X, Y = self.X, self.Y
        U3d, V3d = self.U3d, self.V3d
        Ts = self.XYUVT['T']

        if vmax is None:
            vmax = np.stack(Ts).max()
        if vmin is None:
            vmin = np.stack(Ts).min()

        self.vmin = vmin
        self.vmax = vmax
        
        fig, ax = plt.subplots(figsize=(8, 6), dpi=dpi)
        arrows = amp.blocks.Quiver(X, Y, U3d, V3d, ax=ax, t_axis=2, color='k')
        blocks = amp.blocks.Imshow(Ts, ax=ax, cmap='jet', vmin=vmin, vmax=vmax, interpolation='none')
        cbar = fig.colorbar(blocks.im,ax=ax)
        timearray = np.array([sort_function(s) for s in datlist], dtype='i')
        timeline = amp.Timeline(timearray, fps=fps)
        anim = amp.Animation([blocks, arrows], timeline)

        ax.tick_params(labelbottom=False, bottom=False) # x軸の削除
        ax.tick_params(labelleft=False, left=False) # y軸の削除
        ax.set_xticklabels([]) 
        fig.tight_layout()
        anim.timeline_slider(text='ICYCLE', valfmt='%d')

        return anim, fig, ax


    def save_gif(self, output_filename='sample', **kwargs):
        anim, fig, ax = self.to_gif(**kwargs)
        anim.save_gif(output_filename)
        plt.close()


    def make_average_temp(self, output_filename='average_temp', tmin=None, tmax=None, dpi=100, **kwargs):

        datlist = self.datlist
        X, Y = self.X, self.Y
        U3d, V3d = self.U3d, self.V3d
        Ts = self.XYUVT['T']

        prev_rect = set()
        list_xy = []
        count = []
        for_average_plot = {}
        def onclick(event):
            count.append(1)
            x, y = int(round(event.xdata)), int(round(event.ydata))
            print(event.button, event.x, event.y, x, y)
            if event.button == 3:
                while prev_rect:
                    prev_rect.pop().remove()
                while list_xy:
                    list_xy.pop()
                while count:
                    count.pop()
                return
            if len(count) == 1:
                r = patches.Rectangle((x-0.5, y-0.5), width=1, height=1, ec='gray', fill=False, lw=3)
                ax.add_patch(r)
                fig.canvas.draw()
                prev_rect.add(r)
                list_xy.append((x, y))
            elif len(count) == 2:
                prev_x, prev_y = list_xy[0]
                if prev_x < x:
                    from_x = prev_x - 0.5
                    to_x = x + 0.5
                else:
                    from_x = prev_x + 0.5
                    to_x = x - 0.5
                if prev_y < y:
                    from_y = prev_y - 0.5
                    to_y = y + 0.5
                else:
                    from_y = prev_y + 0.5
                    to_y = y - 0.5
                r = patches.Rectangle((from_x, from_y), width=to_x - from_x, height=to_y - from_y, ec='k', fill=False, lw=3)
                prev_rect.pop().remove()
                ax.add_patch(r)
                fig.canvas.draw()
                prev_rect.add(r)
                list_xy.append((x, y))
            elif len(count) == 3:
                xs = sorted([l[0] for l in list_xy])
                ys = sorted([l[1] for l in list_xy])
                average_temp = [np.average(T[ys[0]:ys[1]+1, xs[0]: xs[1]+1]) for T in Ts]
                for_average_plot['temps'] = average_temp
                r = prev_rect.pop()
                x, y, w, h = r.get_x(), r.get_y(), r.get_width(), r.get_height()
                r.remove()
                r = patches.Rectangle((x, y), width=w, height=h, ec='red', fill=False, lw=3)
                ax.add_patch(r)
                fig.canvas.draw()
                prev_rect.add(r)

                for_average_plot['rect'] = patches.Rectangle((x, y), width=w, height=h, ec='black', fill=False, lw=3)
                fig.canvas.mpl_disconnect(cid)
                plt.close()



        anim, fig, ax = self.to_gif(dpi=70, **kwargs)
        vmin, vmax = self.vmin, self.vmax
        fps = anim.timeline.fps
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()

        try:
            average_temp = for_average_plot['temps']
            r = for_average_plot['rect']
        except KeyError:
            print('Canceled')
            return

        # plot Another Figure
        fig2, (ax2, ax3) = plt.subplots(1, 2, figsize=(10, 5), dpi=dpi)
        ax2.add_patch(r)
        arrows = amp.blocks.Quiver(X, Y, U3d, V3d, ax=ax2, t_axis=2, color='k')
        blocks = amp.blocks.Imshow(Ts, ax=ax2, cmap='jet', vmin=vmin, vmax=vmax, interpolation='none')
        divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax2)
        cax = divider.append_axes('right', '5%', pad='3%')
        cbar = fig2.colorbar(blocks.im, ax=ax2, cax=cax)
        timeline2 = amp.Timeline(anim.timeline.t)
        timearray2 = timeline2.t

        ax2.tick_params(labelbottom=False, bottom=False) # x軸の削除
        ax2.tick_params(labelleft=False, left=False) # y軸の削除
        ax2.set_xticklabels([]) 
        fig2.tight_layout()
        times, temps = amp.util.parametric_line(timearray2, average_temp)
        average_blocks = amp.blocks.Line(times, temps, ax=ax3, color='k', lw=3)
        ax3.set_xlim(timearray2[0], timearray2[-1])

        if tmin is None:
            tmin = vmin
        if tmax is None:
            tmax = vmax
        ax3.set_ylim(tmin, tmax)
        ax3.set_xlabel('ICYCLE')
        ax3.set_ylabel('T average')
        ax3.grid(True)
        plt.subplots_adjust(wspace=0.4)
        anim3 = amp.Animation([arrows, blocks, average_blocks], timeline2)
        anim3.timeline_slider(text='ICYCLE', valfmt='%d')

        anim3.save_gif(output_filename)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='DAT files -> gif')
    parser.add_argument('query', help='DAT files query')
    parser.add_argument('-mt', '--make_average_temp', action='store_true')
    args = parser.parse_args()

    converter = dat(args.query)
    converter.save_gif(vmin=-0.5, vmax=0.5, dpi=150)
    if args.make_average_temp:
        converter.make_average_temp(dpi=150)



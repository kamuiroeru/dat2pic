# .cの方を変更して、もろもろをそのまま出力させ、こちら側で平均する

import matplotlib.pyplot as plt
import numpy as np
from itertools import product
import re


# something.datを読み込む
def load_UVT_DAT(fname, columns='XYUVT'):

    # 行とラベルを対応させる
    label2column = {label:lc for lc, label in enumerate(columns)}
    l2c = label2column

    # 読み込む
    outer_list = [[] for _ in range(len(columns))]
    for lc, line in enumerate(open(fname)):
        line = line.rstrip()
        if line:
            try:
                inner_list = [float(s) for s in re.split('\s+', line) if s]
            except ValueError:
                continue
            for lc, val in enumerate(inner_list):
                outer_list[lc].append(val)

    # 行列の大きさを計算
    xsize, ysize = len(set(outer_list[l2c['X']])), len(set(outer_list[l2c['Y']]))

    # X, Y を適切な引数のベクトルに変更
    X, Y = np.meshgrid(range(xsize), range(ysize))
    X, Y = X.flatten(), Y.flatten()

    # 各要素の行列を定義
    T = np.zeros((ysize, xsize))
    U = np.zeros((ysize, xsize))
    V = np.zeros((ysize, xsize))

    # 代入
    T[Y, X] = outer_list[l2c['T']]
    U[Y, X] = outer_list[l2c['U']]
    V[Y, X] = outer_list[l2c['V']]

    # y軸を反転(matplotlibのy軸は下向きが正なので。)
    T = T[::-1, :]
    U = U[::-1, :]
    V = V[::-1, :]

    return X, Y, U, V, T


# もろもろ平均化、大きさ調整
def convert_UVT(U, V, T):

    U1, U2 = U[1:-1, :-2], U[1:-1, 1:-1]
    U = (U1 + U2) / 2
    V1, V2 = V[2:, 1:-1], V[1:-1, 1:-1]
    V = (V1 + V2) / 2
    T = T[1:-1, 1:-1]

    return U, V, T


# plotしてpdfとpngを出力
def plot_UVT(fname):
    X, Y, U, V, T = load_UVT_DAT(fname)

    # vecの最大値と最小値をoutmaxとoutminに標準化
    def normarize(vec, outmin=0, outmax=1):
        xmin, xmax = vec.min(), vec.max()
        func = np.vectorize(lambda x: (x - xmin)/(xmax - xmin)*(outmax - outmin) + outmin)
        return func(vec)
    
    U = normarize(U, -1, 1)
    V = normarize(V, -1, 1)
    
    U, V, T = convert_UVT(U, V, T)

    # ここまで計算
    #####################################################################
    # ここからプロット
    
    fig, ax = plt.subplots()
    axshowed = ax.imshow(T, cmap='jet', vmin=-0.5, vmax=0.5, interpolation='none')
    cbar = fig.colorbar(axshowed)
    ux_size, uy_size = U.shape[1], V.shape[0]
    for x,y in product(range(ux_size), range(uy_size)):
        dx, dy = U[y, x], V[y, x]
        if dx or dy:
            ax.arrow(x, y, dx, -dy, color='k', head_width=0.1, length_includes_head=True)

    ax.tick_params(labelbottom=False, bottom=False) # x軸の削除
    ax.tick_params(labelleft=False, left=False) # y軸の削除
    ax.set_xticklabels([]) 

    # fnameに数値nが含まれる場合、プロットタイトルをn stepに設定
    num = re.findall('\d+', fname)
    if num:
        plt.title('{} step'.format(int(num[0])))
    fig.tight_layout()
    from os.path import splitext
    fig.savefig(splitext(fname)[0] + '.pdf')
    fig.savefig(splitext(fname)[0] + '.png')
    print('complete {}'.format(fname))


if __name__ == '__main__':
    # コマンドライン引数で読み込む
    from sys import argv
    if len(argv) > 1:
        dat_filename = argv[1]
    else:
        dat_filename = 'UVT.DAT'

    plot_UVT(dat_filename)

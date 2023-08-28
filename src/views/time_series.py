from multiprocessing import Process

import numpy as np
import pyqtgraph as pg

from model.data import Data
from views.grid_plot_iterator import MEAGridPlotIterator


def do_plot(data: Data, selected, signals, envelope, derivative, mv_average,
            mv_mad, mv_var, peaks, bursts, seizure):
    sel_names = data.get_sel_names()
    if len(sel_names) == 0:
        sel_names = data.electrode_names

    t_start, t_stop = data.get_time_s()
    ts = np.linspace(t_start, t_stop, num=data.data.shape[1])
    if not selected:
        sig = data.data[data.selected_electrodes, data.start_idx:data.stop_idx]
    else:
        sig = data.data

    win = pg.GraphicsLayoutWidget(show=True, title="Raw signals")
    win.resize(1200, 800)
    prev_p = None
    it = MEAGridPlotIterator(data)
    for i, (row, col) in enumerate(it):
        title_str = f'<font size="1">{sel_names[i]}</font>'
        p = win.addPlot(row=row, col=col, title=title_str)

        if signals:
            p.plot(x=ts, y=sig[i], pen=(255, 255, 255, 200), name="Raw")
        if envelope:
            env_low = data.envelopes[0][i]
            env_high = data.envelopes[1][i]
            p.plot(x=ts[env_low], y=data.data[i][env_low],
                   pen=(0, 255, 0, 255), name="low envelope")
            p.plot(x=ts[env_high], y=data.data[i][env_high],
                   pen=(0, 255, 0, 255), name="high envelope")

        if derivative:
            p.plot(x=ts[1:], y=data.derivatives[i], pen=(0, 0, 255, 255),
                   name="Derivative")
        if mv_average:
            p.plot(x=ts, y=data.mv_means[i], pen=(255, 165, 0, 255),
                   name="Moving Average")
        if mv_mad:
            p.plot(x=ts, y=data.mv_mads[i], pen=(0, 255, 255, 255),
                   name="Moving MAD")
        if mv_var:
            p.plot(x=ts, y=data.mv_vars[i], pen=(0, 255, 255, 255),
                   name="Moving Var")
        if peaks:
            pdf = data.peaks_df[data.peaks_df['Channel'] == sel_names[i]]
            peak_idxs = pdf['PeakIndex'].values.astype(int)
            p.plot(x=ts[peak_idxs], y=data.data[i][peak_idxs], pen=None,
                   symbolBrush=(255, 0, 0, 255), symbolPen='w', name="Peaks")
            inf1 = pg.InfiniteLine(angle=0, pos=data.lower[i], pen=(0, 0, 200))
            inf2 = pg.InfiniteLine(angle=0, pos=data.upper[i], pen=(255, 0, 255))
            p.addItem(inf1)
            p.addItem(inf2)
        if bursts:
            print("TODO")
            # TODO
        if seizure:
            print("TODO")
            # TODO
        # FIXME continue here

        p.setLabel('left', units='V')
        p.setLabel('bottom', unit='s')
        if prev_p is not None:
            p.setYLink(prev_p)

        prev_p = p

    pg.exec()


def plot_time_series_grid(data: Data,
                          selected: bool = True,
                          signals: bool = True,
                          envelope: bool = False,
                          derivative: bool = False,
                          mv_average: bool = False,
                          mv_mad=False,
                          mv_var=False,
                          peaks=False,
                          bursts=False,
                          seizure=False):
    proc = Process(target=do_plot, args=(data, selected, signals, envelope,
                   derivative, mv_average, mv_mad, mv_var, peaks, bursts,
                   seizure))
    proc.start()

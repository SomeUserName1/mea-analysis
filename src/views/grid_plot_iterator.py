from model.data import Data

def MEAGridPlotIterator:
    """
    An iterator class that iterates through channels to be plotted on a grid.
    """
    def __init__(self, names) -> None:
        """
        Initialize the MEAGridPlotIterator object with a patient object.

        Parameters
        ----------
        data: model.data.Data
           The Data object containing channel data, selected channels
           and metadata to be plotted.
        """
        self.axs = None
        self.fig = None
        self.row_offset = 0
        self.col_offset = 0
        self.row_idx = -1
        self.col_idx = 0
        # See which electrodes are selected and what has to be plotted, such
        # that the grid is as small as possible. Also check if corners are
        # contained, to draw them if neccessary.
        grid_sz = 16 # as we have 256 electrodes
        all_names = [f"R {i} C {j}" for i in range(1, grid_sz + 1) \
                                for j in range(1, grid_sz + 1)]
        offset = 0
        self.crnrs = [0, grid_sz - 1, grid_sz * (grid_sz - 1), grid_size ** 2 - 1]
        adj_els = [[names[crnrs[0] + 1], names[crnrs[0] + grid_sz]],
                   [names[crnrs[1] - 1], names[crnrs[1] + grid_sz]],
                   [names[crnrs[2] + 1], names[crnrs[2] - grid_sz]],
                   [names[crnrs[3] - 1], names[crnrs[3] - grid_sz]]]
        self.plotted = np.zeros((grid_sz, grid_sz))
        for i in range(grid_sz):
            for j in range(grid_sz):
                idx = i * grid_sz + j
                if idx >= grid_size * grid_size:
                    break
                # if the channel is a corner and adjacent channels are selected
                # mark it as to be plotted
                if idx == self.crnrs[0] and all([el in names for adj_els[0]]) \
                    or idx == self.crnrs[1] and all([el in names for adj_els[1]]) \
                    or idx == self.crnrs[2] and all([el in names for adj_els[2]]) \
                    or idx == self.crnrs[3] and all([el in names for adj_els[3]]):
                        self.plotted[i, j] = 1
                        continue
                # If the channel is selected, mark it as to be plotted
                if all_names[idx] in names:
                    self.plotted[i, j] = 1

        # check for empty rows and columns.
        # if its the first row/col print it st. the cut in the grid is visible
        # for every following empty row/col omit it from the grid, st. the
        # grid is as small as possible
        self.empty_rows = []
        self.empty_cols = []
        prev_r_empty = False
        prev_c_empty = False
        for idx in range(grid_sz):
            if np.sum(self.plotted[idx, :]) == 0:
                if prev_r_empty:
                    self.empty_rows.append(idx)

                prev_r_empty = True
            else:
                prev_r_empty = False

            if np.sum(self.plotted[:, idx]) == 0:
                if prev_c_empty:
                    self.empty_cols.append(idx)

                prev_c_empty = True
            else:
                prev_c_empty = False

        # adjust the grid size according to the empty rows and cols
        # and create the figure and axes objects
        self.grid_y = grid_sz - len(empty_rows)
        self.grid_x = grid_sz - len(empty_cols)


    def __iter__(self):
        """
        Implement the iterator protocol.

        Returns
        -------
        self: GridPlotIterator
        """
        return self


    def __next__(self) -> tuple[int, int]:
        """
        Get the next axes of the grid plot.

        Returns
        -------
        data : plt.Axes
            The axes to be plotted to next according to the electrode on the MEA
            grid.

        Raises
        ------
        StopIteration
            When all channels have been plotted accordingly.
        """
        # if all channels have been plotted, raise StopIteration
        if self.row_idx >= self.grid_x \
                and self.col_idx >= self.grid_y:
            raise StopIteration

        self.col_idx += 1
        # if the current col is empty, skip it
        if self.col_idx in self.empty_cols:
            self.col_offset += 1
            return self.__next__()

        # if the current row is empty skip it by setting the col idx to the end
        if self.row_idx in self.empty_rows:
            self.row_offset += 1
            self.col_idx = self.grid_x

        # get the next channel to be plotted
        if self.col_idx >= self.grid_x:
            self.row_idx += 1
            self.col_idx = -1
            self.col_offset = 0
            return self.__next__()

        # if it's a corner/ ground electrode skip it
        if self.row_idx * grid_sz + self.col_idx in self.crnrs:
            return self.__next__()

        return self.row_idx - self.row_offset, self.col_idx - self.col_offset

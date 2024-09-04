import numpy as np
from numba import jit

from sike.atomics.impurity import Impurity


# TODO: Tidy this module up. Could do with sparse local matrices instead? May be necessary for adding transport
# TODO: Is this module necessary if not using petsc? If we're throwing out petsc, can we still do impurity transport, etc?


# class LocalMat:
#     """A local dense matrix class for storing values to be inserted into petsc sparse matrix"""

#     def __init__(self, x_idx, num_states):
#         self.rows = np.array(
#             [x_idx * num_states + k for k in range(num_states)], dtype=np.int32
#         )
#         self.cols = np.array(
#             [x_idx * num_states + k for k in range(num_states)], dtype=np.int32
#         )
#         self.values = np.zeros([num_states, num_states])


# class MatrixTerm:
#     def __init__(self):
#         self.rows = np.array([], dtype=int)
#         self.cols = np.array([], dtype=int)
#         self.values = np.array([], dtype=int)
#         self.mat_loc_positions = np.array([], dtype=int)
#         self.nnz = 0
#         self.x_positions = np.array([], dtype=int)
#         self.mults = np.array([], dtype=int)


# class TransitionTerm(MatrixTerm):
#     def __init__(self, transition):
#         super().__init__()
#         self.transition = transition
#         self.inverse = np.array([], dtype=int)

#     def add_nonzero(self, loc_row, loc_col, num_states, num_x, mult, inverse=False):
#         """Add a non-zero matrix entry to this term

#         Args:
#             loc_row (int): The spatially local row of the nonzero
#             loc_col (int):  The spatially local column of the nonzero
#             num_states (int):  The number of states being evolved (gives size of local matrix)
#             num_x (int): The number of spatial cells
#             mult (float): A multiplier for each matrix entry
#         """

#         self.rows = np.concatenate(
#             [
#                 self.rows,
#                 np.array([loc_row + i * num_states for i in range(num_x)], dtype=int),
#             ]
#         )
#         self.cols = np.concatenate(
#             [
#                 self.cols,
#                 np.array([loc_col + i * num_states for i in range(num_x)], dtype=int),
#             ]
#         )
#         self.values = np.concatenate([self.values, np.zeros(num_x)])
#         self.mat_loc_positions = np.concatenate(
#             [self.mat_loc_positions, np.zeros(num_x, dtype=int)]
#         )
#         self.x_positions = np.concatenate(
#             [self.x_positions, np.arange(num_x, dtype=int)]
#         )
#         self.mults = np.concatenate([self.mults, mult * np.ones(num_x)])
#         if inverse is True:
#             self.inverse = np.concatenate([self.inverse, np.ones(num_x)])
#         else:
#             self.inverse = np.concatenate([self.inverse, np.zeros(num_x)])

#         self.nnz += num_x


# class SparseMat:
#     def __init__(self):
#         self.locs = []
#         self.rows = np.array([], dtype=int)
#         self.cols = np.array([], dtype=int)
#         self.values = []
#         self.nnz = 0

#     def add_nonzeros(self, terms):
#         for term in terms:
#             self.locs += [(term.rows[j], term.cols[j]) for j in range(term.nnz)]
#         self.locs = list(dict.fromkeys(self.locs))
#         self.values += [0.0 for _ in range(len(self.locs))]
#         self.nnz = len(self.locs)

#     def set_rows(self):
#         self.rows = np.array([loc[0] for loc in self.locs], dtype=int)

#     def set_cols(self):
#         self.cols = np.array([loc[1] for loc in self.locs], dtype=int)

#     def get_nonzero_position(self, row, col):
#         return get_loc_pos(self.rows, self.cols, row, col)


# @jit(nopython=True)
# def get_loc_pos(rows, cols, row, col):
#     for i in range(len(rows)):
#         if row == rows[i] and col == cols[i]:
#             return i
#     return 0


def build_matrix(min_x, max_x, num_states):
    """Construct an array of local numpy matrices for the problem

    Args:
        num_states (int): number of evolved states
        evolve (bool): whether problem is evolved in time or solved assuming d/dt = 0

    Returns:
        _type_: _description_
    """

    rate_mat = []
    for i in range(min_x, max_x):
        loc_mat = np.zeros([num_states, num_states])
        rate_mat.append(loc_mat)

    return rate_mat


def fill_local_mat(transitions, num_states, fe, ne, Te, vgrid, dvc):
    # TODO: Is this function necessary?
    local_mat = np.zeros([num_states, num_states])

    # Calculate the values
    for j, trans in enumerate(transitions):
        from_pos = trans.from_pos
        to_pos = trans.to_pos
        typ = trans.type

        # Calculate the value to be added to the matrix
        val = trans.get_mat_value(fe, vgrid, dvc)

        # Add the loss term
        row = from_pos
        col = from_pos
        local_mat[row, col] -= val

        # Add the gain term
        row = to_pos
        col = from_pos
        local_mat[row, col] += val

        # Calculate inverse process matrix entries (3-body recombination & de-excitation)
        if typ == "excitation":
            val = trans.get_mat_value_inv(fe, vgrid, dvc)

            # Add the loss term
            row = to_pos
            col = to_pos
            local_mat[row, col] -= val

            # Add the gain term
            row = from_pos
            col = to_pos
            local_mat[row, col] += val

        elif typ == "ionization":
            val = trans.get_mat_value_inv(fe, vgrid, dvc, ne, Te)

            # Add the loss term
            row = to_pos
            col = to_pos
            local_mat[row, col] -= val

            # Add the gain term
            row = from_pos
            col = to_pos
            local_mat[row, col] += val

    return local_mat


def fill_rate_matrix(
    loc_num_x: int,
    min_x: int,
    max_x: int,
    mat: list,
    impurity: Impurity,
    fe: np.ndarray,
    ne: np.ndarray,
    Te: np.ndarray,
    vgrid: np.ndarray,
    dvc: np.ndarray,
):
    """Fill the rate matrix with rates calculated by each transition object

    Args:
        mat (list): the implicit matrix
        impurity (Impurity): the impurity being modelled (contains all transitions)
        fe (np.ndarray): electron distributions in each cell
        ne (np.ndarray): electron density profile
        Te (np.ndarray): electron temperature profile
        vgrid (np.ndarray): velocity grid
        dvc (np.ndarray): velocity grid widths
    """

    num_states = impurity.tot_states

    # Next, calculate the values
    rank = 0  # TODO: Implement parallelisation
    for i in range(loc_num_x):
        if rank == 0:
            print(" {:.1f}%".format(100 * float(i / loc_num_x)), end="\r")

        for j, trans in enumerate(impurity.transitions):
            from_pos = trans.from_pos
            to_pos = trans.to_pos
            typ = trans.type

            # # Calculate the value to be added to the matrix
            val = trans.get_mat_value(fe[:, i + min_x], vgrid, dvc)

            # Add the loss term
            row = from_pos
            col = from_pos
            mat[i][row, col] += -val

            # Add the gain term
            row = to_pos
            col = from_pos
            mat[i][row, col] += val

            # # Calculate inverse process matrix entries (3-body recombination & de-excitation)
            if typ == "excitation":
                val = trans.get_mat_value_inv(fe[:, i + min_x], vgrid, dvc)

                # Add the loss term
                row = to_pos
                col = to_pos
                mat[i][row, col] += -val

                # Add the gain term
                row = from_pos
                col = to_pos
                mat[i][row, col] += val

            elif typ == "ionization":
                val = trans.get_mat_value_inv(
                    fe[:, i + min_x], vgrid, dvc, ne[i + min_x], Te[i + min_x]
                )

                # Add the loss term
                row = to_pos
                col = to_pos
                mat[i][row, col] += -val

                # Add the gain term
                row = from_pos
                col = to_pos
                mat[i][row, col] += val

    if rank == 0:
        print(" {:.1f}%".format(100))

    return mat

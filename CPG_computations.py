import config as cfg # My own config.py file with configuration parameters
from models import *
import numpy as np
import pandas as pd
import runSelection as rs

def _compute_CPG_matrix_df(run_list):
    """
    A helper function which accepts a list containing multiple runs (as Run
    objects), retrieves their max speed matrices, then uses numpy to compute the
    component-wise maximum. This gives the CPG matrix for those runs, which
    is returned as a Pandas DataFrame.

    Attributes:
        run_list: a list of Run objects
    """

    minimum_gradient = cfg.minimum_gradient
    maximum_gradient = cfg.maximum_gradient
    gradient_interval = np.arange(minimum_gradient, maximum_gradient + 1)

    msm_list = [run._retrieve_msm().as_matrix() for run in run_list]
    CPG_matrix = np.maximum.reduce(msm_list)
    CPG_matrix_df = pd.DataFrame(CPG_matrix, columns=gradient_interval)
    return CPG_matrix_df

def CPG_matrix_by_date(start_date, end_date):
    """
    Given a starting and ending date (which are validated in
    runSelection.runs_by_date()), compute a CPG matrix for only those dates.
    The resulting matrix is returned as a CPG_matrix object
    """
    run_list = rs.runs_by_date(start_date, end_date)
    CPG_matrix_df = _compute_CPG_matrix_df(run_list)
    CPG_matrix_obj = CPG_matrix(CPG_matrix_df)
    return CPG_matrix_obj

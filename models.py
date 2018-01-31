import fileIO
import dataProcessing
import os
import config as cfg # My own config.py file with configuration parameters
import pandas as pd

class Run(object):
    """
    A run. Runs have the following properties:

    Attributes:
        filename: A string showing the filename given to the run by Strafva
        name: A string showing the name of the run. This is typically the
                filename, but with spaces instead of '_'
        date: The date the run occurred on
    """
    gpx_directory = cfg.data_directories['gpx']
    csv_directory = cfg.data_directories['csv']
    msm_directory = cfg.data_directories['msm']

    def __init__(self, filename):
        self.filename = filename
        try:
            # Retrieve the metadata from the gpx file
            self.name, self.date, self.time = fileIO.metadata_from_gpx(filename)
        except:
            return None

        csv_date_directory = self.csv_directory + self.date + r'/'
        msm_date_directory = self.msm_directory + self.date + r'/'

        # First, check if the csv file has already been created (from the gpx),
        # and if not, create it
        if os.path.isfile(csv_date_directory  + filename + '.csv'):
            pass
        else:
            fileIO.gpx_to_csv(filename, self.date)

        # Next, check if the max speed matrix (msm) has already been created,
        # and if not, create it
        if os.path.isfile(msm_date_directory  + filename + '.csv'):
            pass
        else:
            fileIO.csv_to_msm(filename, self.date)


    def _retrieve_dataframe(self):
        """
        Fetches the Pandas DataFrame associated with a run. Primarily used for
        debugging or exploratory analysis. Should not be visible to the
        end-user.
        """
        df = fileIO.load_csv_to_df(self.filename, self.date)
        cleaned_df = dataProcessing.prep_df(df)
        return cleaned_df

    def _retrieve_msm(self):
        """
        Fetches the Pandas DataFrame of max speeds for a run. This matrix has
        rows representing time in seconds, from 0 to the time specified in
        the config file. The columns represent the gradients, and are strings.
        The range the gradient takes on is determined by the config file when
        the matrix is first computed in __init__.
        """
        msm = fileIO.read_max_speed_matrix(self.filename, self.date)
        return msm

    def speed_at_gradient(self, gradient):
        """
        Return a Pandas series with the maximum speed over all time_offset
        frames at a given gradient.

        Attributes:
            gradient: An integer specifying slope * 100 (rounded)
        """
        msm = self._retrieve_msm()
        speed_at_gradient = msm[str(gradient)]
        return speed_at_gradient

class CPG_matrix(pd.DataFrame):
    """
    A Pandas DataFrame with rows indexed by time (t), and columns by
    gradient (g), where gradient is slope * 100. The (t, g) entry holds the
    fastest speed run for time t at gradient g. These are computed separately,
    so fastest speed *across which runs* is determined elsewhere. This object
    simply holds the DataFrame. The range of time and gradient is determined
    in the config file.
    """

    def speed_at_gradient(self, gradient):
        """
        Returns the fastest speeds run at the specified gradient. Time is
        inherited from the CPG_matrix.

        Attributes:
            gradient: An integer specifying slope * 100 (rounded).
        """
        CPG_matrix_df = self[gradient]
        return CPG_matrix_df

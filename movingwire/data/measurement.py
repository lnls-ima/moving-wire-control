"""Moving Wire measurement data module"""

import numpy as _np
import collections as _collections
import imautils.db.database as _database


class MeasurementDataFC(_database.DatabaseAndFileDocument):
    """Read, write and store moving wire measurement results data."""

    label = 'Measurement'
    collection_name = 'measurements_fc_I1'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('software_version',
            {'field': 'software_version', 'dtype': str, 'not_null': False}),
        ('name',
            {'field': 'name', 'dtype': str, 'not_null': True}),
        ('comments',
            {'field': 'comments', 'dtype': str, 'not_null': True}),
        ('I1_mean',
            {'field': 'I1_mean', 'dtype': float, 'not_null': True}),
        ('I1_std',
            {'field': 'I1_std', 'dtype': float, 'not_null': True}),
        ('data_frw',
            {'field': 'data_frw', 'dtype': _np.ndarray, 'not_null': True}),
        ('data_bck',
            {'field': 'data_bck', 'dtype': _np.ndarray, 'not_null': True}),
        ('pos7f',
            {'field': 'pos7f', 'dtype': _np.ndarray, 'not_null': True}),
        ('pos8f',
            {'field': 'pos8f', 'dtype': _np.ndarray, 'not_null': True}),
        ('pos7b',
            {'field': 'pos7b', 'dtype': _np.ndarray, 'not_null': True}),
        ('pos8b',
            {'field': 'pos8b', 'dtype': _np.ndarray, 'not_null': True}),
        ('cfg_id',
            {'field': 'cfg_id', 'dtype': int, 'not_null': True}),
        ('Iamb_id',
            {'field': 'Iamb_id', 'dtype': int, 'not_null': True}),
        ('x_pos',
            {'field': 'x_pos', 'dtype': _np.ndarray, 'not_null': True}),
        ('y_pos',
            {'field': 'y_pos', 'dtype': _np.ndarray, 'not_null': True}),
        ('acq_init_interval',  # [s]
            {'field': 'acq_init_interval', 'dtype': float, 'not_null': False}),
        ('acq_final_interval',  # [s]
            {'field': 'acq_final_interval', 'dtype': float, 'not_null': False}),
    ])

    def __init__(
            self, database_name=None, mongo=False, server=None):
        """Initialize object.

        Args:
            filename (str): connection configuration filepath.
            database_name (str): database file path (sqlite) or name (mongo).
            idn (int): id in database table (sqlite) / collection (mongo).
            mongo (bool): flag indicating mongoDB (True) or sqlite (False).
            server (str): MongoDB server.

        """
        super().__init__(
            database_name=database_name, mongo=mongo, server=server)


class MeasurementDataSW(_database.DatabaseAndFileDocument):
    """Read, write and store stretched wire measurement results data."""

    #.start, end, step, x|y, nturns
    #.velocidade, aceleração jerk
    #postions
    label = 'MeasurementSW'
    collection_name = 'measurements_sw_I1'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('software_version',
            {'field': 'software_version', 'dtype': str, 'not_null': False}),
        ('mode',
            {'field': 'mode', 'dtype': str, 'not_null': True}),
        ('name',
            {'field': 'name', 'dtype': str, 'not_null': True}),
        ('comments',
            {'field': 'comments', 'dtype': str, 'not_null': True}),
        ('I1_mean',
            {'field': 'I1_mean', 'dtype': float, 'not_null': True}),
        ('I1_std',
            {'field': 'I1_std', 'dtype': float, 'not_null': True}),
        ('start_pos',
            {'field': 'start_pos', 'dtype': float, 'not_null': False}),
        ('end_pos',
            {'field': 'end_pos', 'dtype': float, 'not_null': False}),
        ('step',
            {'field': 'step', 'dtype': float, 'not_null': True}),
        ('motion_axis',
            {'field': 'motion_axis', 'dtype': str, 'not_null': True}),
        ('gain',
            {'field': 'gain', 'dtype': float, 'not_null': True}),
        ('turns',
            {'field': 'turns', 'dtype': float, 'not_null': True}),
        ('length',
            {'field': 'length', 'dtype': float, 'not_null': True}),
        ('nplc',
            {'field': 'nplc', 'dtype': float, 'not_null': True}),
        ('duration',
            {'field': 'duration', 'dtype': float, 'not_null': True}),
        ('nmeasurements',
            {'field': 'nmeasurements', 'dtype': int, 'not_null': True}),
        ('speed',
            {'field': 'speed', 'dtype': float, 'not_null': True}),
        ('accel',
            {'field': 'accel', 'dtype': float, 'not_null': True}),
        ('jerk',
            {'field': 'jerk', 'dtype': float, 'not_null': True}),
        ('data_frw',
            {'field': 'data_frw', 'dtype': _np.ndarray, 'not_null': True}),
        ('data_bck',
            {'field': 'data_bck', 'dtype': _np.ndarray, 'not_null': True}),
        ('Iamb_id',
            {'field': 'Iamb_id', 'dtype': int, 'not_null': True}),
        ('x_pos',
            {'field': 'x_pos', 'dtype': float, 'not_null': True}),
        ('y_pos',
            {'field': 'y_pos', 'dtype': float, 'not_null': True}),
        ('acq_init_interval',  # [s]
            {'field': 'acq_init_interval', 'dtype': float, 'not_null': False}),
        ('acq_final_interval',  # [s]
            {'field': 'acq_final_interval', 'dtype': float, 'not_null': False}),
    ])

    def __init__(
            self, database_name=None, mongo=False, server=None):
        """Initialize object.

        Args:
            filename (str): connection configuration filepath.
            database_name (str): database file path (sqlite) or name (mongo).
            idn (int): id in database table (sqlite) / collection (mongo).
            mongo (bool): flag indicating mongoDB (True) or sqlite (False).
            server (str): MongoDB server.

        """
        super().__init__(
            database_name=database_name, mongo=mongo, server=server)


class MeasurementDataSW2(_database.DatabaseAndFileDocument):
    """Read, write and store stretched wire measurement results data."""

    label = 'MeasurementSWI2'
    collection_name = 'measurements_sw_I2'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('software_version',
            {'field': 'software_version', 'dtype': str, 'not_null': False}),
        ('mode',
            {'field': 'mode', 'dtype': str, 'not_null': True}),
        ('name',
            {'field': 'name', 'dtype': str, 'not_null': True}),
        ('comments',
            {'field': 'comments', 'dtype': str, 'not_null': True}),
        ('I2_mean',
            {'field': 'I2_mean', 'dtype': float, 'not_null': True}),
        ('I2_std',
            {'field': 'I2_std', 'dtype': float, 'not_null': True}),
        ('start_pos',
            {'field': 'start_pos', 'dtype': float, 'not_null': True}),
        ('end_pos',
            {'field': 'end_pos', 'dtype': float, 'not_null': True}),
        ('step',
            {'field': 'step', 'dtype': float, 'not_null': True}),
        ('motion_axis',
            {'field': 'motion_axis', 'dtype': str, 'not_null': True}),
        ('gain',
            {'field': 'gain', 'dtype': float, 'not_null': True}),
        ('turns',
            {'field': 'turns', 'dtype': float, 'not_null': True}),
        ('length',
            {'field': 'length', 'dtype': float, 'not_null': True}),
        ('nplc',
            {'field': 'nplc', 'dtype': float, 'not_null': True}),
        ('duration',
            {'field': 'duration', 'dtype': float, 'not_null': True}),
        ('nmeasurements',
            {'field': 'nmeasurements', 'dtype': int, 'not_null': True}),
        ('speed',
            {'field': 'speed', 'dtype': float, 'not_null': True}),
        ('accel',
            {'field': 'accel', 'dtype': float, 'not_null': True}),
        ('jerk',
            {'field': 'jerk', 'dtype': float, 'not_null': True}),
        ('data_frw',
            {'field': 'data_frw', 'dtype': _np.ndarray, 'not_null': True}),
        ('data_bck',
            {'field': 'data_bck', 'dtype': _np.ndarray, 'not_null': True}),
        ('Iamb_id',
            {'field': 'Iamb_id', 'dtype': int, 'not_null': True}),
        ('x_pos',
            {'field': 'x_pos', 'dtype': float, 'not_null': True}),
        ('y_pos',
            {'field': 'y_pos', 'dtype': float, 'not_null': True}),
        ('acq_init_interval',  # [s]
            {'field': 'acq_init_interval', 'dtype': float, 'not_null': False}),
        ('acq_final_interval',  # [s]
            {'field': 'acq_final_interval', 'dtype': float, 'not_null': False}),
    ])

    def __init__(
            self, database_name=None, mongo=False, server=None):
        """Initialize object.

        Args:
            filename (str): connection configuration filepath.
            database_name (str): database file path (sqlite) or name (mongo).
            idn (int): id in database table (sqlite) / collection (mongo).
            mongo (bool): flag indicating mongoDB (True) or sqlite (False).
            server (str): MongoDB server.

        """
        super().__init__(
            database_name=database_name, mongo=mongo, server=server)


class IntegralMaps(_database.DatabaseAndFileDocument):
    """Read, write and store stretched wire integrals map data."""

    label = 'IntegralMaps'
    collection_name = 'integral_maps'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('name', {'field': 'name', 'dtype': str, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('software_version',
            {'field': 'software_version', 'dtype': str, 'not_null': False}),
        ('comments',
            {'field': 'comments', 'dtype': str, 'not_null': True}),
        ('Ix',
            {'field': 'Ix', 'dtype': int, 'not_null': True}),
        ('Iy',
            {'field': 'Iy', 'dtype': int, 'not_null': True}),
        ('I1',
            {'field': 'I1', 'dtype': int, 'not_null': True}),
        ('I2',
            {'field': 'I2', 'dtype': int, 'not_null': True}),
        ('I1x_amb_id',
            {'field': 'I1x_amb_id', 'dtype': int, 'not_null': True}),
        ('I1y_amb_id',
            {'field': 'I1y_amb_id', 'dtype': int, 'not_null': True}),
        ('I2x_amb_id',
            {'field': 'I2x_amb_id', 'dtype': int, 'not_null': True}),
        ('I2y_amb_id',
            {'field': 'I2y_amb_id', 'dtype': int, 'not_null': True}),
        ('x_start_pos',
            {'field': 'x_start_pos', 'dtype': float, 'not_null': True}),
        ('x_end_pos',
            {'field': 'x_end_pos', 'dtype': float, 'not_null': True}),
        ('x_step',
            {'field': 'x_step', 'dtype': float, 'not_null': True}),
        ('x_duration',
            {'field': 'x_duration', 'dtype': float, 'not_null': True}),
        ('y_start_pos',
            {'field': 'y_start_pos', 'dtype': float, 'not_null': True}),
        ('y_end_pos',
            {'field': 'y_end_pos', 'dtype': float, 'not_null': True}),
        ('y_step',
            {'field': 'y_step', 'dtype': float, 'not_null': True}),
        ('y_duration',
            {'field': 'y_duration', 'dtype': float, 'not_null': True}),
        ('repetitions',
            {'field': 'repetitions', 'dtype': int, 'not_null': True}),
        ('I1_start_id',
            {'field': 'I1_start_id', 'dtype': int, 'not_null': True}),
        ('I1_end_id',
            {'field': 'I1_end_id', 'dtype': int, 'not_null': True}),
        ('I2_start_id',
            {'field': 'I2_start_id', 'dtype': int, 'not_null': True}),
        ('I2_end_id',
            {'field': 'I2_end_id', 'dtype': int, 'not_null': True}),
        ('x_pos_array',
            {'field': 'x_pos_array', 'dtype': _np.ndarray, 'not_null': True}),
        ('y_pos_array',
            {'field': 'y_pos_array', 'dtype': _np.ndarray, 'not_null': True}),
        ('I1x',
            {'field': 'I1x', 'dtype': _np.ndarray, 'not_null': True}),
        ('I1x_std',
            {'field': 'I1x_std', 'dtype': _np.ndarray, 'not_null': True}),
        ('I1y',
            {'field': 'I1y', 'dtype': _np.ndarray, 'not_null': True}),
        ('I1y_std',
            {'field': 'I1y_std', 'dtype': _np.ndarray, 'not_null': True}),
        ('I2x',
            {'field': 'I2x', 'dtype': _np.ndarray, 'not_null': True}),
        ('I2x_std',
            {'field': 'I2x_std', 'dtype': _np.ndarray, 'not_null': True}),
        ('I2y',
            {'field': 'I2y', 'dtype': _np.ndarray, 'not_null': True}),
        ('I2y_std',
            {'field': 'I2y_std', 'dtype': _np.ndarray, 'not_null': True}),
    ])

    def __init__(
            self, database_name=None, mongo=False, server=None):
        """Initialize object.

        Args:
            filename (str): connection configuration filepath.
            database_name (str): database file path (sqlite) or name (mongo).
            idn (int): id in database table (sqlite) / collection (mongo).
            mongo (bool): flag indicating mongoDB (True) or sqlite (False).
            server (str): MongoDB server.

        """
        super().__init__(
            database_name=database_name, mongo=mongo, server=server)

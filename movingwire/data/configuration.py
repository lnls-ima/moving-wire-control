"""Moving Wire configuration module"""

import collections as _collections
import imautils.db.database as _database
import numpy as _np


# Conection Config
# class ConnectionConfig(_database.DatabaseAndFileDocument):
#     """Read, write and store connection configuration data."""
# 
#     label = 'Connection'
#     collection_name = 'connections'
#     db_dict = _collections.OrderedDict([
#         ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
#         ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
#         ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
#         ('software_version',
#             {'field': 'software_version', 'dtype': str, 'not_null': False}),
#         ('fdi_enable',
#             {'field': 'fdi_enable', 'dtype': int, 'not_null': True}),
#         ('pmac_enable',
#             {'field': 'pmac_enable', 'dtype': int, 'not_null': True}),
#         ('ps_enable',
#             {'field': 'ps_enable', 'dtype': int, 'not_null': True}),
#         ('fdi_address',
#             {'field': 'fdi_address', 'dtype': str, 'not_null': True}),
#         ('ppmac_address',
#             {'field': 'ppmac_address', 'dtype': str, 'not_null': True}),
#         ('fdi_address',
#             {'field': 'fdi_address', 'dtype': str, 'not_null': True}),
#         ('ps_port',
#             {'field': 'fdi_address', 'dtype': str, 'not_null': True}),
#     ])
# 
#     def __init__(
#             self, database_name=None, mongo=False, server=None):
#         """Initialize object.
# 
#         Args:
#             filename (str): connection configuration filepath.
#             database_name (str): database file path (sqlite) or name (mongo).
#             idn (int): id in database table (sqlite) / collection (mongo).
#             mongo (bool): flag indicating mongoDB (True) or sqlite (False).
#             server (str): MongoDB server.
# 
#         """
#         super().__init__(
#             database_name=database_name, mongo=mongo, server=server)


# class IntegratorConfig(_database.DatabaseAndFileDocument):
#     """Read, write and store FDI2056 integrator configuration data."""
#
#     label = 'Integrator'
#     collection_name = 'integrator'
#     db_dict = _collections.OrderedDict([
#         ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
#         ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
#         ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
#         ('software_version',
#             {'field': 'software_version', 'dtype': str, 'not_null': False}),
#         ('trigger_source',
#             {'field': 'trigger_source', 'dtype': str, 'not_null': True}),
#         ('mode',
#             {'field': 'mode', 'dtype': str, 'not_null': True}),
#         ('timer_base',
#             {'field': 'timer_base', 'dtype': float, 'not_null': True}),
#     ])
#
#     def __init__(
#             self, database_name=None, mongo=False, server=None):
#         """Initialize object.
#
#         Args:
#             filename (str): connection configuration filepath.
#             database_name (str): database file path (sqlite) or name (mongo).
#             idn (int): id in database table (sqlite) / collection (mongo).
#             mongo (bool): flag indicating mongoDB (True) or sqlite (False).
#             server (str): MongoDB server.
#
#         """
#         super().__init__(
#             database_name=database_name, mongo=mongo, server=server)


class PpmacConfig(_database.DatabaseAndFileDocument):
    """Read, write and store ppmac configuration data."""

    label = 'PPMAC'
    collection_name = 'ppmac'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('software_version',
            {'field': 'software_version', 'dtype': str, 'not_null': False}),
        ('name',
            {'field': 'name', 'dtype': str, 'not_null': True}),
        ('speed',
            {'field': 'speed', 'dtype': float, 'not_null': True}),
        ('accel',
            {'field': 'accel', 'dtype': float, 'not_null': True}),
        ('jerk',
            {'field': 'jerk', 'dtype': float, 'not_null': True}),
        ('rot_sf',
            {'field': 'rot_sf', 'dtype': float, 'not_null': True}),
        ('rot_max_err',
            {'field': 'rot_max_err', 'dtype': int, 'not_null': True}),
        ('steps_per_turn',
            {'field': 'steps_per_turn', 'dtype': int, 'not_null': True}),
        ('pos_x',
            {'field': 'pos_x', 'dtype': float, 'not_null': True}),
        ('x_step',
            {'field': 'x_step', 'dtype': float, 'not_null': True}),
        ('speed_x',
            {'field': 'speed_x', 'dtype': float, 'not_null': True}),
        ('accel_x',
            {'field': 'accel_x', 'dtype': float, 'not_null': True}),
        ('jerk_x',
            {'field': 'jerk_x', 'dtype': float, 'not_null': True}),
        ('min_x',
            {'field': 'min_x', 'dtype': float, 'not_null': True}),
        ('max_x',
            {'field': 'max_x', 'dtype': float, 'not_null': True}),
        ('x_sf',
            {'field': 'x_sf', 'dtype': float, 'not_null': True}),
        ('x_offset',
            {'field': 'x_offset', 'dtype': float, 'not_null': False}),
        ('pos_y',
            {'field': 'pos_y', 'dtype': float, 'not_null': True}),
        ('y_step',
            {'field': 'y_step', 'dtype': float, 'not_null': True}),
        ('speed_y',
            {'field': 'speed_y', 'dtype': float, 'not_null': True}),
        ('accel_y',
            {'field': 'accel_y', 'dtype': float, 'not_null': True}),
        ('jerk_y',
            {'field': 'jerk_y', 'dtype': float, 'not_null': True}),
        ('min_y',
            {'field': 'min_y', 'dtype': float, 'not_null': True}),
        ('max_y',
            {'field': 'max_y', 'dtype': float, 'not_null': True}),
        ('y_sf',
            {'field': 'y_sf', 'dtype': float, 'not_null': True}),
        ('y_stps_per_cnt',
            {'field': 'y_stps_per_cnt', 'dtype': float, 'not_null': True}),
        ('y_offset',
            {'field': 'y_offset', 'dtype': float, 'not_null': False}),
        ('home_offset1',
            {'field': 'home_offset1', 'dtype': int, 'not_null': True}),
        ('home_offset2',
            {'field': 'home_offset2', 'dtype': int, 'not_null': True}),
        ('home_offset3',
            {'field': 'home_offset3', 'dtype': int, 'not_null': True}),
        ('home_offset4',
            {'field': 'home_offset4', 'dtype': int, 'not_null': True}),
        ('home_offset5',
            {'field': 'home_offset5', 'dtype': int, 'not_null': True}),
        ('home_offset6',
            {'field': 'home_offset6', 'dtype': int, 'not_null': True}),
        ('max_pos_error',
            {'field': 'max_pos_error', 'dtype': float, 'not_null': True}),
    ])

    def __init__(self, database_name=None, mongo=False, server=None):
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


class PowerSupplyConfig(_database.DatabaseAndFileDocument):
    """Read, write and store Power Supply configuration data."""

    label = 'PowerSupply'
    collection_name = 'power_supply'
    db_dict = _collections.OrderedDict([
        ('idn',
            {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date',
            {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour',
            {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('name',
            {'field': 'name', 'dtype': str, 'not_null': True}),
        ('ps_type',
            {'field': 'ps_type', 'dtype': int, 'not_null': True}),
        ('dclink',
            {'field': 'dclink', 'dtype': float, 'not_null': False}),
        ('current_setpoint',
            {'field': 'current_setpoint', 'dtype': float, 'not_null': True}),
        ('min_current',
            {'field': 'min_current', 'dtype': float, 'not_null': True}),
        ('max_current',
            {'field': 'max_current', 'dtype': float, 'not_null': True}),
#         ('dcct',
#             {'field': 'DCCT Enabled', 'dtype': int, 'not_null': True}),
#         ('dcct_head',
#             {'field': 'DCCT Head', 'dtype': int, 'not_null': True}),
        ('kp',
            {'field': 'kp', 'dtype': float, 'not_null': True}),
        ('ki',
            {'field': 'ki', 'dtype': float, 'not_null': True}),
        ('current_array', {
            'field': 'current_array',
            'dtype': _np.ndarray, 'not_null': False}),
    ])


class MeasurementConfig(_database.DatabaseAndFileDocument):
    """Read, write and store measurement configuration data."""

    label = 'MeasurementCfg'
    collection_name = 'measurement_cfg'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('software_version',
            {'field': 'software_version', 'dtype': str, 'not_null': False}),
        ('name',
            {'field': 'name', 'dtype': str, 'not_null': True, 'unique': True}),
        ('mode',
            {'field': 'mode', 'dtype': str, 'not_null': True}),
        ('width',
            {'field': 'width', 'dtype': float, 'not_null': True}),
        ('turns',
            {'field': 'turns', 'dtype': float, 'not_null': True}),
        ('length',
            {'field': 'length', 'dtype': float, 'not_null': True}),
        ('direction',
            {'field': 'direction', 'dtype': str, 'not_null': True}),
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
        ('range',
            {'field': 'range', 'dtype': str, 'not_null': True}),
        ('steps_f',
            {'field': 'steps_f', 'dtype': _np.ndarray, 'not_null': True}),
        ('steps_b',
            {'field': 'steps_b', 'dtype': _np.ndarray, 'not_null': True}),
        ('speed',
            {'field': 'speed', 'dtype': float, 'not_null': True}),
        ('accel',
            {'field': 'accel', 'dtype': float, 'not_null': True}),
        ('jerk',
            {'field': 'jerk', 'dtype': float, 'not_null': True}),
        ('nplc',
            {'field': 'nplc', 'dtype': float, 'not_null': True}),
        ('duration',
            {'field': 'duration', 'dtype': float, 'not_null': True}),
        ('nmeasurements',
            {'field': 'nmeasurements', 'dtype': int, 'not_null': True}),
        ('max_init_error',  # [um]
            {'field': 'max_init_error', 'dtype': float, 'not_null': True}),
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


class IntegralMapsCfg(_database.DatabaseAndFileDocument):
    """Read, write and store stretched wire integrals map configuration."""

    label = 'IntegralMapsCfg'
    collection_name = 'integral_maps_cfg'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('software_version',
            {'field': 'software_version', 'dtype': str, 'not_null': False}),
        ('name',
            {'field': 'name', 'dtype': str, 'not_null': True, 'unique': True}),
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


class FiducializationCfg(_database.DatabaseAndFileDocument):
    """Read, write and store stretched wire fiducialization configuration."""

    label = 'FiducializationCfg'
    collection_name = 'fiducialization_cfg'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('offset_xa',
            {'field': 'offset_xa', 'dtype': int, 'not_null': True}),
        ('offset_xb',
            {'field': 'offset_xb', 'dtype': int, 'not_null': True}),
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

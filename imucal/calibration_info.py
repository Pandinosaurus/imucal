import json
from collections import namedtuple

import h5py
import numpy as np

_calibration_info = namedtuple('CalibrationInfo', ['K_a', 'R_a', 'b_a', 'K_g', 'R_g', 'K_ga', 'b_g'])

# TODO: Is this best practice? :D
class CalibrationInfo(_calibration_info):
    __slots__ = ()

    def __repr__(self):
        out = 'CalibrationInfo('
        for val in self._fields:
            out += '\n' + val + ' =\n' + getattr(self, val).__repr__() + ',\n'
        out += '\n)'
        return out

    def __eq__(self, other):
        # Check type:
        if not isinstance(other, self.__class__):
            raise ValueError('Comparison is only defined between two CalibrationInfo object!')

        # Test keys equal:
        if not self._fields == other._fields:
            return False

        # Test Calibration values
        for v1, v2 in zip(self._asdict().values(), other._asdict().values()):
            if not np.array_equal(v1, v2):
                return False
        return True

    def _to_list_dict(self):
        return {key: getattr(self, key).tolist() for key in self._fields}

    def to_hdf5(self, filename):
        """
        Saves calibration matrices to hdf5 fileformat
        :param filename: filename (including h5 at end)
        """

        with h5py.File(filename, 'w') as hdf:
            for k, v in self._asdict().items():
                hdf.create_dataset(k, data=v)

    def to_json(self):
        data_dict = self._to_list_dict()
        return json.dumps(data_dict, indent=4)

    def to_json_file(self, path):
        data_dict = self._to_list_dict()
        return json.dump(data_dict, open(path, 'w'))

    @classmethod
    def from_hdf5(cls, path):
        """
        Reads calibration data stored in hdf5 fileformat (created by CalibrationInfo save_to_hdf5)
        :param filename: filename
        :return: CalibrationInfo object
        """

        with h5py.File(path, 'r') as hdf:
            values = dict()
            for k in cls._fields:
                values[k] = np.array(hdf.get(k))

        return cls(**values)

    @classmethod
    def _from_list_dict(cls, list_dict):
        raw_json = {k: np.array(v) for k, v in list_dict.items()}
        return cls(**raw_json)

    @classmethod
    def from_json(cls, json_str):
        raw_json = json.loads(json_str)
        return cls._from_list_dict(raw_json)

    @classmethod
    def from_json_file(cls, path):
        raw_json = json.load(open(path, 'r'))
        return cls._from_list_dict(raw_json)

    def calibrate_acc(self, acc):
        # Combine Scaling and rotation matrix to one matrix
        acc_mat = np.matmul(np.linalg.inv(self.R_a), np.linalg.inv(self.K_a))
        acc_out = acc_mat @ (acc.T - self.b_a)

        return acc_out.T

    def calibrate_gyro(self, gyro, calibrated_acc):
        # Combine Scaling and rotation matrix to one matrix
        gyro_mat = np.matmul(np.linalg.inv(self.R_g), np.linalg.inv(self.K_g))

        d_ga = self.K_ga @ calibrated_acc
        gyro_out = gyro_mat @ (gyro.T - d_ga - self.b_g)
        return gyro_out.T

    def calibrate(self, acc, gyro):
        acc_out = self.calibrate_acc(acc)
        gyro_out = self.calibrate_gyro(gyro, acc_out.T)

        return acc_out, gyro_out

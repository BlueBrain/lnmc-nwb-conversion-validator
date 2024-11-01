"""Validator for the NWB file.

Copyright 2024 Blue Brain Project / EPFL

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import tarfile
import os
import shutil
from pynwb import NWBHDF5IO
import numpy as np
import pandas as pd
from bluepyefe import igorpy
from nwb_data_validator.exceptions import UnregisteredMetadata, UnregisteredTest
from nwb_data_validator import utils


class DatasetValidator:
    """Class to perform QC on an nwb dataset.

    Attributes:
        nwb_dataset: The NWB dataset object containing the signal and metadata
        igor_header: Metadata object of the IGOR file
        igor_signal: The IGOR signal (voltage or current traces)
        nwb_id: Id of the NWB file

    """

    metadata_for_validation = frozenset(
        {"sampling_rates_close", "igor_header_correct", "wavenotes_equal"}
    )
    metadata_for_verification = frozenset(
        {
            "wavenotes_present",
            "description_present",
            "sampling_rate_present",
            "gain_present",
        }
    )

    additional_tests = frozenset({"igor_file_present"})

    def __init__(self, nwb_dataset, nwb_file_id):
        """Constructor."""
        self.nwb_dataset = nwb_dataset
        self.nwb_id = nwb_file_id
        self.igor_file_present = None
        self.igor_header, self.igor_signal = self.__parse_igor_file()

    @property
    def additional_test_results(self):
        """Contains the json result for the additional tests.

        These tests are not part of the main requirements.
        They are created to help NMC lab with the data conversion.

        Returns:
            Dictionary containing the boolean additional test results.
        """
        res = {}
        res["igor_file_present"] = self.igor_file_present

        for key in res:
            if key not in self.additional_tests:
                raise UnregisteredTest(f"{key} is not part of the additional tests.")

        return res

    def __parse_igor_file(self):
        """Parses the IGOR file contained in the NWB Dataset.

        Returns:
            tuple: tuple containing:

            igorpy.IgorHeader: Header metadata object
            numpy.ndarray: The 1D signal

        """
        igor_fname = self.nwb_dataset.description.strip("/")
        igor_file = os.path.join(".temp-igor", self.nwb_id, igor_fname)

        if os.path.isfile(igor_file):
            self.igor_file_present = True
        else:
            self.igor_file_present = False
            igor_split = igor_file.split("/")
            igor_file = "/".join(igor_split[0:2] + igor_split[11:])

        header, signal = igorpy.read(igor_file)

        return (header, signal)

    def validate_signal(self):
        """Checks if the signal in NWB is equal to the IGOR signal.

        Returns:
            dict: A dictionary representing the data validation by
             mapping the 'data_equal' key to a boolean.
        """
        nwb_signal = self.nwb_dataset.data[:]
        igor_signal = self.igor_signal

        return {
            "data_equal": np.allclose(
                nwb_signal, igor_signal, rtol=0, atol=0, equal_nan=True
            )
        }

    def validate_metadata(self, nwb_wavenote):
        """Checks if the metadata of interest for a given dataset is correct.

        Args:
            nwb_wavenote (str): wavenote associated with the nwb dataset.

        Returns:
            dict: The metadata validation results.

        """
        nwb_sampling_rate = self.nwb_dataset.rate
        igor_sampling_rate = 1 / self.igor_header.dx

        validation_results = {}

        validation_results["sampling_rates_close"] = np.isclose(
            nwb_sampling_rate, igor_sampling_rate
        )
        validation_results["igor_header_correct"] = (
            self.igor_header.bname in self.nwb_dataset.description
        )
        validation_results["wavenotes_equal"] = (
            self.igor_header.wavenotes == nwb_wavenote
        )

        for key in validation_results:
            if key not in self.metadata_for_validation:
                raise UnregisteredMetadata(
                    f"{key} is not part of the metadata validation schema."
                )

        return validation_results

    def verify_metadata(self, nwb_wavenote):
        """Checks if the nwb dataset metadata is complete.

        Args:
            nwb_wavenote (str): wavenote associated with the nwb dataset.

        Returns:
            dict: The metadata verification results.
        """
        verification_results = {}

        # wavenotes_present is false iff not wavenotes_present and igor_present
        if bool(nwb_wavenote):
            wavenotes_present = True
        else:
            if bool(self.igor_header.wavenotes):
                wavenotes_present = False
            else:
                wavenotes_present = True

        verification_results["wavenotes_present"] = wavenotes_present
        verification_results["description_present"] = bool(self.nwb_dataset.description)
        verification_results["sampling_rate_present"] = bool(self.nwb_dataset.rate)
        verification_results["gain_present"] = bool(self.nwb_dataset.gain)

        for key in verification_results:
            if key not in self.metadata_for_verification:
                raise UnregisteredMetadata(
                    f"{key} is not part of the metadata verification schema."
                )

        return verification_results


class NWBValidator:
    """To validate a single NWB file using multiple IGOR files.

    Attributes:
        nwb_path: Path to NWB file
        igor_tarfile: The corresponding IGOR archive
        io: The NWBHDF5IO object to read the NWB file
        file_id: Identifier for an NWB file
        required_metadata: The static list of metadata to be verified.
    """

    required_metadata = [
        "experiment_description",
        "file_create_date",
        "identifier",
        "session_description",
        "session_start_time",
        "timestamps_reference_time",
        "experimenter",
        "institution",
        "lab",
        "slices",
    ]

    def __init__(self, nwb_path, igor_tarfile):
        """Constructor."""
        self.nwb_path = nwb_path
        self.igor_tarfile = igor_tarfile
        self.io = None
        self.file_id = None

    def __enter__(self):
        """Enters the runtime context related to this object."""
        self.connect()
        self.extract_igor()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Exits the runtime context related to this object."""
        self.disconnect()
        self.clean_up()

    def connect(self):
        """Connect to the NWB file."""
        self.io = NWBHDF5IO(
            path=self.nwb_path, mode="r"
        )  # pylint: disable=consider-using-with
        nwbfile_in = self.io.read()
        self.file_id = nwbfile_in.identifier

    def extract_igor(self):
        """Extracts the IGOR tar file to a temporary directory."""
        with tarfile.open(self.igor_tarfile) as tar:
            tar.extractall(path=os.path.join(".temp-igor", self.file_id))

    def disconnect(self):
        """Closes the NWBHDFIO connection."""
        self.io.close()

    def clean_up(self):
        """Deletes the temporary IGOR files extracted."""
        shutil.rmtree(os.path.join(".temp-igor", self.file_id))

    def verify_metadata(self):
        """Verifies the NWB metadata.

        Returns:
            dict: NWB metadata verification results.
        """
        nwbfile_in = self.io.read()

        verification_results = {}
        for metadata in self.required_metadata:
            try:
                if nwbfile_in.fields[metadata]:
                    verification_results[metadata] = True
            except KeyError:
                verification_results[metadata] = False

        return verification_results

    # pylint: disable=too-many-locals
    def validate_datasets(self):
        """Validates all of the datasets within NWB.

        Returns:
            dict: The combined qc results for all dataset.
        """
        nwbfile_in = self.io.read()

        acquisitions = list(nwbfile_in.acquisition)
        stimuli = list(nwbfile_in.stimulus)
        intracellular_df = nwbfile_in.get_intracellular_recordings().to_dataframe()
        response_names = intracellular_df["responses"]["response"].apply(
            lambda x: x[2].name
        )
        response_idx = pd.Series(data=response_names.index.values, index=response_names)
        stimuli_names = intracellular_df["stimuli"]["stimulus"].apply(
            lambda x: x[2].name
        )
        stimuli_idx = pd.Series(data=stimuli_names.index.values, index=stimuli_names)

        nwb_datasets_qc = {"acquisition": {}, "stimulus": {}}

        for ac_name in acquisitions:
            idx = response_idx.loc[ac_name]
            row = intracellular_df.loc[idx]
            try:
                wavenote = row["responses"].wavenote_original
                wavenote = utils.decode_bstring(wavenote)
            except AttributeError:
                wavenote = ""
            if ac_name in nwb_datasets_qc["acquisition"]:
                raise ValueError(
                    "The dataset key already exists!"
                    "There are datasets with the same name."
                )
            nwb_acquisition = nwbfile_in.acquisition[ac_name]
            nwb_datasets_qc["acquisition"][ac_name] = self.__get_dataset_qc(
                nwb_acquisition, wavenote
            )

        for stim_name in stimuli:
            idx = stimuli_idx.loc[stim_name]
            row = intracellular_df.loc[idx]
            try:
                wavenote = row["stimuli"].wavenote_original
            except AttributeError:
                wavenote = ""
            if stim_name in nwb_datasets_qc["stimulus"]:
                raise ValueError(
                    "The dataset key already exists!"
                    "There are datasets with the same name."
                )

            nwb_stimulus = nwbfile_in.stimulus[stim_name]
            nwb_datasets_qc["stimulus"][stim_name] = self.__get_dataset_qc(
                nwb_stimulus, wavenote
            )

        return nwb_datasets_qc

    def __get_dataset_qc(self, nwb_dataset, wavenote):
        """Performs QC on an NWB dataset and returns the combined results.

        Args:
            nwb_dataset: The nwb PatchClampSeries dataset.
            wavenote (str): Wavenote associated with the nwb_dataset.

        Returns:
            dict: Combined QC results of the nwb_dataset.
        """
        qc_results = {}
        dv = DatasetValidator(nwb_dataset, self.file_id)
        qc_results["data"] = dv.validate_signal()
        qc_results["metadata_verification"] = dv.verify_metadata(wavenote)
        qc_results["metadata_validation"] = dv.validate_metadata(wavenote)
        qc_results["additional_tests"] = dv.additional_test_results

        return qc_results

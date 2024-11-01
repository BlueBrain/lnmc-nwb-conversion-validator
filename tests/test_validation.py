"""Test the validation.

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

import pprint
from nwb_data_validator import NWBValidator
import ndx_lnmc_icephys_hierarchy


def test_verify_nwb_metadata():
    """Checking if metadata is contained in NWB"""
    nwb_path = "tests/data/170106_2A-BJM.nwb"
    igor_path = "tests/data/170106_2A.tgz"

    print("Verifying NWB metadata...")
    with NWBValidator(nwb_path, igor_path) as nwb_validator:
        nwb_meta_results = nwb_validator.verify_metadata()

    print("Metadata results")
    pprint.pprint(nwb_meta_results)

    # check if all are bool
    for _, v in nwb_meta_results.items():
        assert isinstance(v, bool)

    # all results are true
    assert len(nwb_meta_results) == 10
    assert sum(nwb_meta_results.values()) == 10


def test_validate_recording():
    """Checking the recording validation of NWB and IGOR files"""
    nwb_path = "tests/data/170106_2A-BJM.nwb"
    igor_path = "tests/data/170106_2A.tgz"

    print("Validating NWB and IGOR data & metadata...")
    with NWBValidator(nwb_path, igor_path) as nwb_validator:
        dataset_res = nwb_validator.validate_datasets()
        sample_acquisition = dataset_res["acquisition"]["ccs__IDdepol__42"]

    pprint.pprint(sample_acquisition)
    all_test_res = [all(list(val.values())) for val in sample_acquisition.values()]
    pprint.pprint(all_test_res)
    assert all(all_test_res)

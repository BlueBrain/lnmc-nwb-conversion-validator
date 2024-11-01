"""Test report generation.

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

from nwb_data_validator import NWBValidator, AsciiReport
import ndx_lnmc_icephys_hierarchy


def test_ascii_report():
    """Tests if text report is generated as expected."""
    nwb_path = "tests/data/170106_2A-BJM.nwb"
    igor_path = "tests/data/170106_2A.tgz"

    validation_results = {}
    with NWBValidator(nwb_path, igor_path) as nwb_validator:
        validation_results["metadata"] = nwb_validator.verify_metadata()
        validation_results["datasets"] = nwb_validator.validate_datasets()

    txt_report = AsciiReport(
        experimenter_name="test", validation_results=validation_results
    )
    txt_report.to_txt(".")

    with open("test_report.txt") as f:
        contents = f.read().splitlines()
        assert contents[-1] == "Report is created successfully."

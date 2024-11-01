"""Creates the tex file given a pickle of dictionary containing validation results.

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

import argparse
import pickle
import ndx_icephys_meta
from nwb_data_validator import AsciiReport, LatexReport


def main():
    """The main validator procedure"""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pickle_path",
        type=str,
        help="path to the pickle containing validation results dict",
    )

    parser.add_argument(
        "-p",
        "--postfix",
        type=str,
        help="Postfix to be attached to the files generated",
        default="",
    )
    parser.add_argument("-l", "--latex_report", default=False)

    args = parser.parse_args()
    pickle_path = args.pickle_path
    postfix = args.postfix
    create_tex_report = args.latex_report

    validation_results = pickle.load(open(pickle_path, "rb"))

    if create_tex_report:
        doc = LatexReport(experimenter_name=postfix)
        doc.fill_criteria_description()
        doc.fill_from_dict(validation_results)
        doc.generate_tex(f"nwb_qc_{postfix}")
        print("Latex file is generated.")

    txt_report = AsciiReport(experimenter_name=postfix, validation_results=validation_results)
    txt_report.to_txt()
    print("Ascii report is generated.")


if __name__ == "__main__":
    main()

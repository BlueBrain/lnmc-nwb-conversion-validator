"""
Script to validate a batch of NWB files

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
import sys
import pickle
from pathlib import Path
from joblib import Parallel, delayed
from tqdm import tqdm
import pandas as pd
from nwb_data_validator import NWBValidator, AsciiReport, LatexReport, utils, tqdm_joblib



def validate_nwb(nwb_fpath, map_df, igor_path):
    """Validates a single nwb and returns the results."""
    nwb_file_id = nwb_fpath.stem

    igor_fname = map_df[map_df.nwb == nwb_file_id].tar.values[0].strip()
    igor_tarfile = igor_path / igor_fname

    try:
        igor_tarfile = utils.get_existing_tar_on_disk(igor_tarfile)
    except FileNotFoundError:
        sys.exit(
            f"Corresponding IGOR tar file for the nwb file {nwb_file_id}"
            f" with name: {igor_fname} cannot be found on {igor_path}."
        )
    res_dict = {}
    res_dict[nwb_file_id] = {}
    with NWBValidator(str(nwb_fpath), igor_tarfile) as nwb_validator:
        res_dict[nwb_file_id]["metadata"] = nwb_validator.verify_metadata()
        res_dict[nwb_file_id]["datasets"] = nwb_validator.validate_datasets()

    return res_dict


def main():
    """The main validator procedure"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--nwb_path", type=str, help="Path that contains NWB files", required=True
    )
    parser.add_argument(
        "-i",
        "--igor_path",
        type=str,
        help="Path that contains IGOR file archives",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--mapfile",
        type=str,
        help="Path to the nwb-igor map file",
        default="",
    )
    parser.add_argument(
        "-p",
        "--postfix",
        type=str,
        help="Postfix to be attached to the files generated",
        default="",
    )
    parser.add_argument("-l", "--latex_report", default=False)
    parser.add_argument("-j", "--n_jobs", help="Number of processes", default=-1)
    args = parser.parse_args()
    nwb_path, igor_path = Path(args.nwb_path), Path(args.igor_path)
    map_path = Path(args.mapfile)
    create_tex_report = args.latex_report
    print(f"nwb_path: {nwb_path} \n igor_path: {igor_path} \n postfix: {args.postfix}")

    if not nwb_path.is_dir:
        sys.exit("NWB path is not valid!")

    if not igor_path.is_dir:
        sys.exit("IGOR path is not valid!")

    map_df = pd.read_csv(map_path, header=None)
    map_df.columns = ["nwb", "tar"]

    nwb_files = [x for x in nwb_path.glob("*.nwb")]

    validation_results = {}

    with tqdm_joblib(
        tqdm(desc="NWB validation in parallel", total=len(nwb_files))
    ) as progress_bar:
        val_results = Parallel(n_jobs=args.n_jobs)(
            delayed(validate_nwb)(nwb_fpath, map_df, igor_path)
            for nwb_fpath in nwb_files
        )

    for result in val_results:
        validation_results.update(result)

    pickle.dump(validation_results, open(f"qc_dict_{args.postfix}.pickle", "wb"))

    if create_tex_report:
        doc = LatexReport(experimenter_name=args.postfix)
        doc.fill_criteria_description()
        doc.fill_from_dict(validation_results)
        doc.generate_tex(f"nwb_qc_{args.postfix}")

    txt_report = AsciiReport(experimenter_name=args.postfix, validation_results=validation_results)
    txt_report.to_txt()


if __name__ == "__main__":
    main()

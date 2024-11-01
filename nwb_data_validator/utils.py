"""Utility functions.

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

import os.path
from pynwb import NWBHDF5IO


def get_igor_tar_filename(nwb_file):
    """Extract and return the igor tar fname from the nwb.

    Attributes:
        nwb_file (str): path to the nwb file
    Returns:
        str: the igor fname
    """
    io = NWBHDF5IO(path=nwb_file, mode="r")
    nwbfile_in = io.read()

    one_acquisition = list(nwbfile_in.acquisition)[0]
    igor_fname = nwbfile_in.acquisition[one_acquisition].description.split("/")[-2]

    if "Folder" in igor_fname:
        igor_fname = igor_fname.split(" ")[0]

    io.close()
    return igor_fname


def get_existing_tar_on_disk(tar_path):
    """Checks if the tar archive exists on the disk and returns the path (str).

    Tries .tar and .tgz extensions.
    Raises an exception if the file's not found on the disk.
    """
    if os.path.isfile(tar_path):
        return tar_path
    elif os.path.isfile(f"{tar_path}.tar"):
        return f"{tar_path}.tar"
    elif os.path.isfile(f"{tar_path}.tgz"):
        return f"{tar_path}.tgz"
    else:
        raise FileNotFoundError(
            f"{tar_path} " f"(with or without .tar or .tgz extension) does not exist."
        )


def chunker(seq, size):
    """Create a list of list of a desired size.

    Args:
        seq (list): Main list containing the items to be chunked.
        size (int): the desired size of the inner list.
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def flatten_nested_keys_of_failed_tests(nested_dict):
    """Flattens keys of value "False" in the nested dict by concatenating them.

    Args:
        nested_dict (dict): nested dictionary containing tests and results.

    Returns:
        List of concatenated keys pointing to "False".
    """
    flattened_keys = []

    stack = [(val, nested_dict[val]) for val in nested_dict.keys()]
    while len(stack) > 0:
        popped_path, popped_val = stack.pop()
        if isinstance(popped_val, dict):
            for key_in_next in popped_val.keys():
                stack.append((f"{popped_path}/{key_in_next}", popped_val[key_in_next]))
        elif popped_val is False:
            flattened_keys.append(f"{popped_path} failed.")

    return flattened_keys


def decode_bstring(bstr_obj):
    """Decodes and returns the str object from bytes.

    Args:
        bstr_obj: the bytes string object
    Returns:
        string object if conversion is successful, input object otherwise.
    """
    try:
        decoded_bstring = bstr_obj.decode()
    except (UnicodeDecodeError, AttributeError):
        return bstr_obj
    return decoded_bstring

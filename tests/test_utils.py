"""
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

from nwb_data_validator import utils


def test_flatten_nested_keys_of_failed_tests():
    """test the dictionary flattening through key concatenation."""
    nested_dict = {
        "key1": {"key1.1": {"key2": True}, "key1.2": {"key3": True, "key4": False}}
    }

    flattened_keys = utils.flatten_nested_keys_of_failed_tests(nested_dict)
    assert (len(flattened_keys)) == 1
    assert flattened_keys[0] == "key1/key1.2/key4 failed."


def test_decode_bstring():
    """test the bstring decoding function."""
    bstr_obj = b"this is a byte string"
    decoded_bstr = "this is a byte string"
    assert utils.decode_bstring(bstr_obj) == decoded_bstr

    str_obj = "this is a string"
    assert utils.decode_bstring(str_obj) == str_obj

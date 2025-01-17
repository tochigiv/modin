# Licensed to Modin Development Team under one or more contributor license agreements.
# See the NOTICE file distributed with this work for additional information regarding
# copyright ownership.  The Modin Development Team licenses this file to you under the
# Apache License, Version 2.0 (the "License"); you may not use this file except in
# compliance with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import importlib
import pkgutil
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

import modin.pandas


@pytest.fixture
def doc_urls(get_generated_doc_urls):
    # ensure all docstring are generated - import _everything_ under 'modin.pandas'
    for modinfo in pkgutil.walk_packages(modin.pandas.__path__, "modin.pandas."):
        try:
            importlib.import_module(modinfo.name)
        except ModuleNotFoundError:
            # some optional 3rd-party dep missing, ignore
            pass
    return sorted(get_generated_doc_urls())


def test_all_urls_exist(doc_urls):
    broken = []
    # TODO: remove the hack after pandas fixes it
    broken_urls = (
        "https://pandas.pydata.org/pandas-docs/version/2.2.0/reference/api/pandas.DataFrame.flags.html",
        "https://pandas.pydata.org/pandas-docs/version/2.2.0/reference/api/pandas.Series.info.html",
        "https://pandas.pydata.org/pandas-docs/version/2.2.0/reference/api/pandas.DataFrame.isetitem.html",
        "https://pandas.pydata.org/pandas-docs/version/2.2.0/reference/api/pandas.Series.swapaxes.html",
        "https://pandas.pydata.org/pandas-docs/version/2.2.0/reference/api/pandas.DataFrame.to_numpy.html",
        "https://pandas.pydata.org/pandas-docs/version/2.2.0/reference/api/pandas.Series.axes.html",
        "https://pandas.pydata.org/pandas-docs/version/2.2.0/reference/api/pandas.Series.divmod.html",
        "https://pandas.pydata.org/pandas-docs/version/2.2.0/reference/api/pandas.Series.rdivmod.html",
    )
    for broken_url in broken_urls:
        doc_urls.remove(broken_url)

    def _test_url(url):
        try:
            with urlopen(url):
                pass
        except HTTPError:
            broken.append(url)

    with ThreadPoolExecutor(32) as pool:
        pool.map(_test_url, doc_urls)

    assert not broken, "Invalid URLs detected"

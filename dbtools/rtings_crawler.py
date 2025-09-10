# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import json
import re
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from autoeq.frequency_response import FrequencyResponse
from autoeq.utils import is_file_name_allowed

ROOT_PATH = Path(__file__).parent.parent
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(1, str(ROOT_PATH))
from dbtools.name_index import NameIndex, NameItem
from dbtools.crawler import Crawler, ProcessingError
from dbtools.constants import MEASUREMENTS_PATH


class RtingsCrawler(Crawler):
    def __init__(self, driver=None, delete_existing_on_prompt=True, redownload=False):
        if driver is None:
            opts = Options()
            opts.add_argument('--headless')
            driver = webdriver.Chrome(options=opts)
        super().__init__(driver=driver, delete_existing_on_prompt=delete_existing_on_prompt, redownload=redownload)

    @property
    def measurements_path(self):
        return MEASUREMENTS_PATH.joinpath('Rtings')

    def guess_name(self, item):
        name = re.sub(r'(Truly Wireless|True Wireless|Wireless)$', '', item.source_name).strip()
        name = self.manufacturers.replace(name)
        return name

    def resolve(self, item):
        """Resolve name for a single item. Updates the item in place."""
        ground_truths = self.name_index.find(source_name=item.source_name)
        if ground_truths is None:
            return
        for ground_truth in ground_truths:
            if ground_truth.name is not None:
                item.name = ground_truth.name
            if ground_truth.form is not None:
                item.form = ground_truth.form
            if ground_truth.rig is not None and item.rig is None:
                item.rig = ground_truth.rig

    @staticmethod
    def graph_data_test_configs():
        test_configs = {}
        for version in ['1-8', '1-7', '1-6', '1-5', '1-4', '1-2']:
            html = requests.get(f'https://www.rtings.com/headphones/{version}/graph').text
            document = BeautifulSoup(html, 'html.parser')
            test_bench = json.loads(document.find(class_='app-body').find('div').get('data-props'))['test_bench']
            for product in test_bench['comparable_products']:
                # if product["fullname"] in [payload['source_name'] for payload in product_graph_data_url_payloads]:
                #     # The versions are iterated from newest to oldest, if product with the same name already exists,
                #     # that means it was included in the results of the newer test methodology and so this one can
                #     # be skipped
                #     continue
                # IDs of all the tests done for the current headphone
                tids = set([test_result['test']['original_id'] for test_result in product['review']['test_results']])
                valid_test_ids = []
                # Look for test IDs that correspond to left channel raw frequency response
                matching_raw_fr_l_ids = [
                    tid for tid in tids if tid in ['4011', '7917', '21564', '1344', '2060', '3182']]
                if matching_raw_fr_l_ids:
                    valid_test_ids.append(matching_raw_fr_l_ids[0])
                # Look for test IDs that correspond to right channel raw frequency response
                matching_raw_fr_r_ids = [
                    tid for tid in tids if tid in ['4012', '7918', '21565', '1343', '2061', '3183']]
                if matching_raw_fr_r_ids:
                    valid_test_ids.append(matching_raw_fr_r_ids[0])
                if not valid_test_ids:
                    # This must be one of the tests that don't have raw FR, but instead has bass, mid and treble, skip
                    continue
                if product['fullname'] not in test_configs:
                    test_configs[product['fullname']] = []
                for test_id in valid_test_ids:
                    test_configs[product['fullname']].append({
                        'test_methodology': tuple([int(x) for x in version.split('-')]),
                        'payload': {
                            'named_version': 'public',
                            'product_id': product['id'],
                            'test_original_id': test_id,

                        }
                    })
        return test_configs

    @staticmethod
    def graph_data_url(payload, cache=None):
        """Fetches URL for JSON file from API

        Args:
            payload: payload, {"named_version": "public", "proudct_id": str, "test_original_id": str}
            cache: Optional cache dict

        Returns:

        """
        cache_key = f'{payload["product_id"]}/{payload["test_original_id"]}'
        if cache_key in cache:  # Item found in cache
            url = cache[cache_key]
        else:  # Item not found in cache, get URL with API call
            res = requests.post('https://www.rtings.com/api/v2/safe/graph_tool__product_graph_data_url', data=payload)
            if res.status_code < 200 or res.status_code >= 300:
                print(f'Failed to get graph URL with payload {payload}: {res.text}')
                return None
            data = res.json()
            try:
                path = data['data']['product']['review']['test_results'][0]['graph_data_url']
                return f'https://i.rtings.com{path}'
            except:
                print(f'Graph data URL for {payload} returned an unexpected data format: {data}')
                return None
        if url is not None:
            cache[cache_key] = url
        return url

    def crawl(self):
        if self.measurements_path.joinpath('crawl_graph_data_urls.json').exists():
            with open(self.measurements_path.joinpath('crawl_graph_data_urls.json')) as fh:
                graph_data_url_cache = json.load(fh)
        else:
            graph_data_url_cache = {}
        self.name_index = self.read_name_index()
        self.crawl_index = NameIndex()
        for source_name, product_test_configs in tqdm(self.graph_data_test_configs().items()):
            methodologies = sorted(set([test_config['test_methodology'] for test_config in product_test_configs]))
            # This sort gives the earliest methodology version
            # Headphones measured on v1.8 are not available in the earlier sets
            earliest_methodology = methodologies[0]
            latest_methodology = methodologies[-1]
            if earliest_methodology >= (1, 8):
                rig = 'Bruel & Kjaer 5128'
                old = self.name_index.find(source_name=source_name, rig='HMS II.3')
                if old:  # An entry exists with old rig, remove it so it can be replaced with the new one
                    for item in old.items:
                        self.name_index.remove(item)
                        continue
            else:
                rig = 'HMS II.3'

            # Create crawl index items
            for test_config in product_test_configs:
                if test_config['test_methodology'] != latest_methodology:
                    # Skip all tests that were performed with older test methodologies
                    continue
                item = NameItem(
                    source_name=source_name,
                    rig=rig,
                    url=self.graph_data_url(test_config['payload'], cache=graph_data_url_cache))
                self.resolve(item)
                self.crawl_index.add(item)

        with open(self.measurements_path.joinpath('crawl_graph_data_urls.json'), 'w', encoding='utf-8') as fh:
            json.dump(graph_data_url_cache, fh, ensure_ascii=False, indent=4)
        self.write_name_index()
        return self.crawl_index

    def json_path(self, item):
        uid = item.url.split('/')[-2]
        return self.measurements_path.joinpath('json', f'{uid}.json')

    @staticmethod
    def parse_json(json_data):
        """Parses Rtings.com JSON data

        Args:
            json_data: JSON data object as returned by Rtings API

        Returns:
            Parsed FrequencyResponse
        """
        data = np.array(json_data['data'])
        if 'header' in json_data:
            header = json_data['header']
            frequency = data[:, header.index('Frequency')]
            target = data[:, header.index('Target Response')]
            col_ix = None
            for col_name in ['Left Avg', 'Right Avg']:
                if col_name in header:
                    col_ix = header.index(col_name)
                    break
            if col_ix is None:
                raise ProcessingError('Could not find any of the data columns in JSON')
            raw = data[:, col_ix]
        else:
            frequency = data[:, 0]
            target = data[:, -1]
            raw = data[:, 1]
        fr = FrequencyResponse(name='fr', frequency=frequency, raw=raw, target=target)
        return fr

    def target_path(self, item):
        """Target file path for the item in measurements directory

        Args:
            item: NameItem for the measurement

        Returns:
            Target file path, None if necessary props are missing
        """
        if item.is_ignored or item.form is None or item.name is None:
            return None
        path = self.measurements_path.joinpath('data', item.form, item.rig, f'{item.name}.csv')
        if not is_file_name_allowed(item.name):
            raise ValueError(f'Target path cannot be "{path}"')
        return path

    def process_group(self, items, new_only=True):
        if items[0].is_ignored:
            return
        if len(items) == 0 or len(items) > 2:
            raise ProcessingError(f'{len(items)} measurements of {items[0].name} grouped together, don\'t know what to do.')
        file_path = self.target_path(items[0])
        if new_only and file_path.exists():
            return
        frs = []
        for item in items:
            raw = self.download(item.url, self.json_path(item))
            frs.append(self.parse_json(json.loads(raw.decode('utf-8'))))
        fr = FrequencyResponse(
            name=items[0].name,
            frequency=frs[0].frequency,
            raw=np.mean([fr.raw for fr in frs], axis=0))
        fr.interpolate()
        fr.center()
        # Write to file
        file_path.parent.mkdir(exist_ok=True, parents=True)
        fr.write_csv(file_path)


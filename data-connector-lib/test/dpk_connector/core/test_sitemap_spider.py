# (C) Copyright IBM Corp. 2024.
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

from pathlib import Path

import pytest
from dpk_connector.core.item import ConnectorItem
from dpk_connector.core.spiders.sitemap import BaseSitemapSpider, ConnectorSitemapSpider
from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.http import HtmlResponse


@pytest.fixture
def crawler() -> Crawler:
    crawler = Crawler(
        ConnectorSitemapSpider,
        settings={
            "STATS_CLASS": "scrapy.statscollectors.MemoryStatsCollector",
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        },
    )
    crawler._apply_settings()
    return crawler


def test_init_subdomain_focus():
    spider = BaseSitemapSpider(
        seed_urls=(
            "http://blog.example.com/",
            "http://contents.example.com/",
        ),
        subdomain_focus=True,
    )
    assert spider.seed_urls == {
        "http://blog.example.com/",
        "http://contents.example.com/",
    }
    assert spider.allowed_domains == {"blog.example.com", "contents.example.com"}


def test_init_path_focus():
    spider = BaseSitemapSpider(
        seed_urls=(
            "https://openshiftjsonschema.dev/v4.9.18-standalone-strict/",
            "https://openshiftjsonschema.dev/",
        ),
        path_focus=True,
    )
    assert spider.seed_urls == {
        "https://openshiftjsonschema.dev/v4.9.18-standalone-strict/",
        "https://openshiftjsonschema.dev/",
    }
    assert spider.sitemap_urls == {
        "https://openshiftjsonschema.dev/robots.txt",
        "https://openshiftjsonschema.dev/robots.txt/",
        "https://openshiftjsonschema.dev/sitemap.xml",
        "https://openshiftjsonschema.dev/sitemap_index.xml",
        "https://openshiftjsonschema.dev/sitemapindex.xml",
        "https://openshiftjsonschema.dev/sitemap",
        "https://openshiftjsonschema.dev/sitemap-index.xml",
        "https://openshiftjsonschema.dev/sitemap/index.xml",
        "https://openshiftjsonschema.dev/sitemap/sitemap.xml",
        "https://openshiftjsonschema.dev/sitemap1.xml",
    }
    assert spider.allowed_domains == {"openshiftjsonschema.dev"}
    assert spider.sitemaps_seen == {"openshiftjsonschema.dev"}
    assert spider.focus_paths == {"/v4.9.18-standalone-strict/"}


def test_parse(datadir: Path, crawler: Crawler):
    response_body = (datadir / "index.html").read_text()

    def callback(url: str, body: bytes, headers: dict):
        assert url == "http://example.com/index.html"
        assert body.decode("utf-8") == response_body
        assert headers == {"Content-Type": "text/html"}

    spider = ConnectorSitemapSpider.from_crawler(crawler, seed_urls=("http://example.com",), callback=callback)
    request = Request(
        "http://example.com/index.html",
        meta={
            "seed_url": "http://example.com",
            "depth": 1,
        },
    )
    response = HtmlResponse(
        "http://example.com/index.html",
        headers={"Content-Type": "text/html"},
        body=response_body,
        request=request,
        encoding="utf-8",
    )
    parsed = spider.parse(response)

    item = next(parsed)
    assert item == ConnectorItem(dropped=False, downloaded=True, system_request=False, sitemap=False)

    for next_request in parsed:
        assert isinstance(next_request, Request) is True
        assert next_request.url in (
            "http://example.com/blog/",
            "http://example.com/contents/",
            "http://example.com/css/app.css",
            "http://example.com/favicon.ico?r=1.6",
            "http://example.com/",
        )
        assert next_request.callback == spider.parse
        assert next_request.meta["seed_url"] == "http://example.com"
        assert next_request.meta["previous_url"] == "http://example.com/index.html"

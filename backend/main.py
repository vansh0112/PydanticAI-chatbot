# main.py

import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from processing_utils import smart_chunk_text

CHUNKS_PATH = "chunks.json"

async def crawl_and_store_chunks():
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        deep_crawl_strategy=BestFirstCrawlingStrategy(max_depth=2, max_pages=30),
        stream=False,
        verbose=True,
        markdown_generator=DefaultMarkdownGenerator(
            options={"citations": True, "body_width": 80}
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(
            url="https://ai.pydantic.dev/",
            config=crawl_config,
            session_id="session1"
        )

        print(f"[Crawling] Completed: {len(results)} pages crawled.")
        all_markdown = "\n\n".join(
            result.markdown.raw_markdown for result in results if result.markdown
        )

        chunks = smart_chunk_text(all_markdown)
        print(f"[Chunking] Created {len(chunks)} chunks")

        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"[Saved] Chunks saved to {CHUNKS_PATH}")


if __name__ == "__main__":
    asyncio.run(crawl_and_store_chunks())

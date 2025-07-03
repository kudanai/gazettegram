import asyncio
import httpx
from asyncio import Queue
import sys

from api.scraper import get_max_page_number, fetch_index_links, fetch_and_parse_announcement
from data.gazettedb import GazetteDB
from config import TARGET_GAZETTE_TYPE, DATABASE_PATH, MAX_CONCURRENT_REQUESTS, REQUEST_DELAY, MAX_INDEX_PAGES


async def main():
    """
    Main function to orchestrate the scraping process.
    """
    db = GazetteDB(DATABASE_PATH)
    total_new_iulaans = 0
    total_fetched_iulaans = 0
    total_failed_iulaans = 0

    print("Starting gazette sync...")

    async with httpx.AsyncClient() as client:
        for gazette_type in TARGET_GAZETTE_TYPE:
            print(f"--- Processing Type: {gazette_type.value} ---")
            
            # 1. Determine the total number of pages to scrape
            max_page = await get_max_page_number(client, gazette_type)
            if MAX_INDEX_PAGES:
                max_page = min(max_page, MAX_INDEX_PAGES)
            print(f"Found {max_page} pages to check for announcements.")

            page_queue = Queue()
            iulaan_id_queue = Queue()
            
            # Counters for logging
            type_new_iulaans = 0
            type_skipped_iulaans = 0
            type_fetched_iulaans = 0
            type_failed_iulaans = 0

            # Define Page Worker to find announcement IDs
            async def page_worker():
                nonlocal type_new_iulaans, type_skipped_iulaans
                while True:
                    page_num = await page_queue.get()
                    try:
                        iulaan_ids = await fetch_index_links(client, gazette_type, page_num)
                        for iulaan_id in iulaan_ids:
                            if not db.iulaan_exists(iulaan_id):
                                await iulaan_id_queue.put(iulaan_id)
                                type_new_iulaans += 1
                            else:
                                type_skipped_iulaans += 1
                    except httpx.HTTPStatusError as e:
                        print(f"HTTP error fetching page {page_num}: {e}", file=sys.stderr)
                    finally:
                        page_queue.task_done()
                    await asyncio.sleep(REQUEST_DELAY)

            # Define Iulaan Worker to fetch announcement data
            async def iulaan_worker():
                nonlocal type_fetched_iulaans, type_failed_iulaans
                while True:
                    iulaan_id = await iulaan_id_queue.get()
                    try:
                        iulaan_data = await fetch_and_parse_announcement(client, iulaan_id)
                        db.insert_iulaan(iulaan_data)
                        type_fetched_iulaans += 1
                    except httpx.HTTPStatusError as e:
                        print(f"HTTP error fetching iulaan {iulaan_id}: {e}", file=sys.stderr)
                        type_failed_iulaans += 1
                    except Exception as e:
                        print(f"An error occurred processing {iulaan_id}: {e}", file=sys.stderr)
                        type_failed_iulaans += 1
                    finally:
                        iulaan_id_queue.task_done()

            # Start all workers. They will wait until the queues are populated.
            page_workers = [asyncio.create_task(page_worker()) for _ in range(MAX_CONCURRENT_REQUESTS)]
            iulaan_workers = [asyncio.create_task(iulaan_worker()) for _ in range(MAX_CONCURRENT_REQUESTS)]

            # Populate page queue, which starts the page workers
            for page_num in range(1, max_page + 1):
                await page_queue.put(page_num)
            
            # Wait for all pages to be processed
            await page_queue.join()

            # Now that all pages are processed, no more iulaan_ids will be added.
            # Wait for the remaining iulaan_ids to be processed.
            await iulaan_id_queue.join()

            # Cancel all workers to gracefully exit their `while True` loops
            for worker in page_workers + iulaan_workers:
                worker.cancel()
            await asyncio.gather(*page_workers, *iulaan_workers, return_exceptions=True)

            # Log results for this type
            total_new_iulaans += type_new_iulaans
            total_fetched_iulaans += type_fetched_iulaans
            total_failed_iulaans += type_failed_iulaans
            
            print(f"Found {type_new_iulaans} new announcements. Skipped {type_skipped_iulaans} existing ones.")
            print(f"Successfully fetched {type_fetched_iulaans} new announcements. Failed: {type_failed_iulaans}.")
            print(f"--- End Processing Type: {gazette_type.value} ---")

    print("\n--- Sync Summary ---")
    print(f"Total new announcements found: {total_new_iulaans}")
    print(f"Total successfully fetched: {total_fetched_iulaans}")
    print(f"Total failed: {total_failed_iulaans}")
    print("Sync complete.")


if __name__ == "__main__":
    asyncio.run(main())

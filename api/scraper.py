from bs4 import BeautifulSoup
from .gazette_types import GazetteType, Iulaan

# base configuration
BASE_URL = "https://gazette.gov.mv/iulaan"


async def get_max_page_number(client, type: GazetteType):
    """
    Fetches the maximum page number for a given type.
    """
    response = await client.get(BASE_URL, params={"type": type.value, "page": 1})
    page_numbers = []

    soup = BeautifulSoup(response.text, "html.parser")
    page_tags = soup.find_all('li', class_="page-item")
    for page_tag in page_tags:
        try:
            page_link = page_tag.find('a')
            if page_link:
                page_number = page_link.get_text(strip=True)
                page_numbers.append(int(page_number))
        except:
            pass

    return max(page_numbers)


async def parse_index_page(response) -> list[str]:
    """
    :param response: index page response
    :return: list of iulaan_id from links found in the page
    """
    soup = BeautifulSoup(response.text, "html.parser")
    iulaan_ids = []
    for link_tag in soup.find_all('a', class_="iulaan-title"):
        href = link_tag.get('href')
        if href and '/iulaan/' in href:
            iulaan_id = href.split('/')[-1]
            iulaan_ids.append(iulaan_id)
    return iulaan_ids


async def fetch_index_links(client, type: GazetteType, page_number: int = 1):
    """
    Fetches the page for a given type and returns a BeautifulSoup object.
    """
    response = await client.get(BASE_URL, params={"type": type.value, "page": page_number})
    response.raise_for_status()
    iulaan_links = await parse_index_page(response)
    return iulaan_links


async def fetch_and_parse_announcement(client, iulaan_id: str) -> Iulaan:
    """
    Fetches and parses an individual announcement page.
    """
    url = f"{BASE_URL}/{iulaan_id}"
    response = await client.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    title = ''
    office_name = ''
    iulaan_type = ''
    additional_info = {}
    attachments = {}
    body = ''

    # The main content is within the div with class 'col-md-9 iulaan-info bordered no-padding items-list'
    main_content_div = soup.find('div', class_="iulaan-info")

    if main_content_div:
        # Extract title
        title_tag = main_content_div.find('div', class_="iulaan-title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract office name and iulaan type
        office_name_tag = main_content_div.find('span', class_="office-name")
        if office_name_tag:
            office_name = office_name_tag.get_text(strip=True)

        iulaan_type_tag = main_content_div.find('a', class_="iulaan-type")
        if iulaan_type_tag:
            iulaan_type = iulaan_type_tag.get_text(strip=True)

        # Extract body content
        # The actual body content is within a div with class 'details'
        details_divs = main_content_div.find_all('div', class_="details")
        if details_divs:
            # Concatenate text from all 'details' divs
            body = '\n\n'.join([str(div) for div in details_divs])

    # Extract metadata (additional_info) from the col-md-3 div
    metadata = soup.find_all('div', class_="info")
    for metadata_div in metadata:
        text = metadata_div.get_text(strip=True)
        key, value = text.split(':', 1)
        additional_info[key.strip()] = value.strip()

    # Extract attachments
    for link in soup.find_all('a', href=True):
        if '.pdf' in link['href'] or '.docx' in link['href'] or '.xlsx' in link['href']:
            attachments[link.get_text(strip=True)] = link['href']

    return Iulaan(
        id=iulaan_id,
        title=title,
        office_name=office_name,
        iulaan_type=iulaan_type,
        additional_info=additional_info,
        attachments=attachments,
        body=body
    )


if __name__ == '__main__':
    import sys
    import asyncio
    import httpx
    from pprint import pprint

    async def main(iulaan_id):
        async with httpx.AsyncClient() as client:
            announcement = await fetch_and_parse_announcement(client, iulaan_id)
            pprint(announcement)

    if len(sys.argv) > 1:
        asyncio.run(main(sys.argv[1]))
    else:
        print("Usage: python -m api.scraper <iulaan_id>")
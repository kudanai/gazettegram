import httpx

from config import KEYWORD_SCORE_CUTOFF, KEYWORD_MAP, DATABASE_PATH
from config import TG_URL_SEND, TG_ADMIN_CHATID, REQUEST_DELAY, BASE_URL, TG_CHAT_ID
from data.filters import analyze_document_score, html_to_text
from data.gazettedb import GazetteDB


async def post_telegram(message, chat_id=TG_ADMIN_CHATID):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TG_URL_SEND,
            data={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
        )

        return response.json()


def get_scored_iulaans(db: GazetteDB):
    items = db.get_all_iulaan(is_processed=False)
    print(f"Analysing {len(items)} iulaans")
    for item in items:
        doc = item.title + " " + html_to_text(item.body)
        score_res = analyze_document_score(doc, KEYWORD_MAP)
        if score_res['score'] >= KEYWORD_SCORE_CUTOFF:
            yield item # to be updated after it's posted
        else:
            db.set_iulaan_processed(item.id, True)


def format_iulaan(iulaan) -> str:
    additional_info = ""
    for key, value in iulaan.additional_info.items():
        additional_info += f"{key}: {value}\n"

    attachments = ""
    for key, value in iulaan.attachments.items():
        attachments += f"- [{key}]({value})\n"

    return f"[{iulaan.title}]({BASE_URL}/iulaan/{iulaan.id})\n{iulaan.office_name}\n\n{additional_info}\n{attachments}"


async def main():
    db = GazetteDB(DATABASE_PATH)

    for iulaan in get_scored_iulaans(db):
        res = await post_telegram(
            format_iulaan(iulaan).strip(),
            TG_CHAT_ID
        )

        if res['ok']:
            db.set_iulaan_processed(iulaan.id, True)

        await asyncio.sleep(REQUEST_DELAY)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
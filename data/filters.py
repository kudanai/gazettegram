from bs4 import BeautifulSoup


def analyze_document_score(text: str, keyword_map: dict = dict()) -> dict:
    """
    Analyzes announcement text based on the keyword_map.

    Args:
        text: The full text of the announcement (title + body).
        keyword_map: a dictionary containing the final score and matched keywords.

    Returns:
        A dictionary containing the final score and matched keywords.
        e.g., {'score': 9, 'matches': ['BID_REQUEST', 'TECH_SOFTWARE']}
    """
    score = 0
    matched_categories = set()

    for category, details in keyword_map.items():
        for term in details['terms']:
            if term in text:
                score += details['weight']
                matched_categories.add(category)
                # Once a category is matched, no need to check other terms in it
                break

    return {
        "score": score,
        "matches": list(matched_categories)
    }


def html_to_text(html_string):
    """
    Converts a given HTML string to plain text.

    Args:
        html_string: The HTML to be converted.

    Returns:
        A string containing the text from the HTML, with all tags removed.
    """
    soup = BeautifulSoup(html_string, 'html.parser')
    return soup.get_text(strip=True)

from yarl import URL

md_link_escape_table = str.maketrans(
    {
        ")": r"\)",
        "\\": r"\\",
    }
)


def url_to_markdown(url: URL) -> str:
    """
    Convert an URL to a Markdown link.
    """
    return str(url).translate(md_link_escape_table)

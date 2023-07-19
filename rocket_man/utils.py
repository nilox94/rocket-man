from yarl import URL

md_link_escape_table = str.maketrans(
    {
        ")": r"\)",
        "\\": r"\\",
    }
)


def escape_md_link(url: URL, text: str = "") -> str:
    """
    Convert a URL to a Markdown link.
    """
    return str(url).translate(md_link_escape_table)

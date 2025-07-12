from typing import List

from db.firestore_client import get_all_cuisines_db


def create_resources(mcp):

    @mcp.resource("foodapp://cuisines")
    def list_all_cuisines() -> List[str]:
        """
        Provides a list of all available cuisine types from the restaurants.
        This helps the AI know what options are valid for searching.
        """
        return get_all_cuisines_db()

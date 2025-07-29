import unittest
from bigbook_api.book_api_client import search_books

class TestSearchBooks(unittest.TestCase):
    def test_search_books_returns_list(self):
        query = "books about wizards"
        results = search_books(query)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_search_book_has_expected_fields(self):
        query = "Dune"
        results = search_books(query)
        if results:
            book = results[0]
            self.assertIn('title', book)
            self.assertIn('author', book)
            self.assertIn('rating', book)

if __name__ == '__main__':
    unittest.main()

"""Basic tests. Run with:  python test_app.py   (works in demo mode, no API key needed)"""
import os
import unittest

os.environ["GEMINI_API_KEY"] = ""  # force demo mode for predictable tests
import app as studio  # noqa: E402


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.client = studio.app.test_client()

    def post(self, **kw):
        return self.client.post("/api/generate", json=kw)

    def test_home_page_loads(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"AI Project Studio", r.data)

    def test_every_task_works_in_demo_mode(self):
        for tid in studio.TASKS:
            r = self.post(task=tid, input="Machine learning basics", tone="Simple", points=3)
            self.assertEqual(r.status_code, 200, tid)
            self.assertTrue(r.get_json()["demo"])

    def test_empty_input_rejected(self):
        self.assertEqual(self.post(task="summarize", input="   ").status_code, 400)

    def test_invalid_task_rejected(self):
        self.assertEqual(self.post(task="hack", input="hello").status_code, 400)

    def test_too_long_input_rejected(self):
        self.assertEqual(self.post(task="text", input="a" * 7000).status_code, 400)

    def test_points_clamped_and_prompt_filled(self):
        r = self.post(task="ideas", input="IoT", tone="Formal", points=99).get_json()
        self.assertIn("10 distinct ideas", r["prompt"])
        self.assertIn("Formal", r["prompt"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

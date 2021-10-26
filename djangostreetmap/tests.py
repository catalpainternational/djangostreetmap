from django.core import management
from django.test import TestCase

# Create your tests here.


class MyTestCase(TestCase):
    def test_foo(self):
        management.call_command("import_highways", "djangostreetmap/papua-new-guinea-latest.osm.pbf", "highways")
        self.assertEqual(True, True)

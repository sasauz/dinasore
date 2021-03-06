import unittest
from core import fb_resources


class TestResources(unittest.TestCase):

    def test_exists_fb(self):
        fb_res = fb_resources.FBResources('TEST_FB')
        result = fb_res.exists_fb()
        self.assertEqual(True, result)

        fb_res = fb_resources.FBResources('E_EXAMPLE_1')
        result = fb_res.exists_fb()
        self.assertEqual(False, result)

    def test_import_fb(self):
        fb_res = fb_resources.FBResources('TEST_FB')
        element, fb_obj = fb_res.import_fb()
        result = fb_obj.schedule('EI', 23, None)
        tag = element.tag
        self.assertEqual('FBType', tag)
        self.assertEqual(24, result[0])

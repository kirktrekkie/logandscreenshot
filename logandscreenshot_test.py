from logandscreenshot import LogAndScreenshot
import unittest
import re

class LogAndScreenshotTests(unittest.TestCase):

    def setUp(self):
        self.las = LogAndScreenshot()

    def test_set_parameters(self):
        self.las.set_parameters("path=testpath")
        self.assertEqual(self.las.path,"testpath")

    def test_set_unknown_parameter(self):
        response = self.las.set_parameters("pathh=testpath")
        self.assertEqual(response, "Unknown parameter: pathh")

    def test_file_and_name_path(self):
        self.las.path = "c:\\temp\\"
        self.las.testcase = "testname"
        self.las.file_name_and_path()
        regex = re.compile('c:\\\\temp\\\\testname\\\\.*')
        self.assertTrue(regex.search(self.las.filepathname))
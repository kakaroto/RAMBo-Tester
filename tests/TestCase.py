
class TestStatus:
    DISABLED = 0
    PENDING = 1
    SUCCESS = 2
    FAILED = 4
    TESTING = 8
    CANCELED = 16

class TestCase(object):
    def __init__(self):
        self.reset()
        self._enabled = True
        self._required = False
        self._finally = False
        self._fatal = False

    def name(self):
        """ The name of the test case """
        return "Unnamed Test Case"

    @property
    def required(self):
        """Whether this test case is required (cannot be disabled)"""
        return self._required

    @required.setter
    def required(self, required):
        self._required = required

    @property
    def fatal(self):
        """Whether this test case is fatal (stop subsequent tests)"""
        return self._fatal

    @fatal.setter
    def fatal(self, fatal):
        self._fatal = fatal

    @property
    def _finally(self):
        """Whether this test case is required should always be called even if
        previous tests in the list have failed (such as poweroff/disconnect)"""
        return self._finally

    @_finally.setter
    def _finally(self, _finally):
        self._finally = _finally

    @property
    def enabled(self):
        """Whether this test case is enabled or not """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        # Can't disable a required test case
        if self.required:
            enabled = True
        self._enabled = enabled
        self.reset()

    def reset(self):
        """ Reset the test case before running the test again """
        self.results = []
        if self.enabled:
            self.status = TestStatus.PENDING
            self.error_string = None
        else:
            self.status = TestStatus.DISABLED
            self.error_string = "This test is disabled"

    def cancel(self):
        self.status = TestStatus.CANCELED
        self.error_string = "Testing was canceled"


    def success(self):
        """ Whether the test was successful """
        return self.status == TestStatus.SUCCESS

    def failed(self):
        """ Whether the test failed """
        return self.status == TestStatus.FAILED

    def Test(self, context):
        """ Execute the test and fill self.results with the result """
        self.reset()
        if self.status == TestStatus.DISABLED:
            return False
        self.status = TestStatus.TESTING

        self._test(context)
        return self.Verify(context)

    def _test(self, context):
        """ Function to be overridden by child class """
        raise NotImplementedError

    def Verify(self, context):
        """ Verify self.results and set self.status and self.error_string """
        # Do not verify results more than once and we only need to verify them
        # After we just finished testing
        if self.status == TestStatus.TESTING:
            self._verify(context)
        return self.success()


    def _verify(self, context):
        """ Function to be overridden by child class """
        raise NotImplementedError


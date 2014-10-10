from TestCase import *

class TestMotor(TestCase):
    def __init__(self, steps):
        TestCase.__init__(self)
        self.steps = int(steps)

    def name(self):
        if self.steps == 1:
            step = "Full"
        elif self.steps == 2:
            step = "Half"
        else:
            step = "1/%d" % self.steps
        return "Motors %s Step" % step

    def _test(self, context):
        context.log("Testing %s forward..." % self.name())
        context.target.setMicroStepping(self.steps)
        context.target.runSteppers(frequency = 200 * self.steps * stepperTestRPS,
                                   steps = 200 * self.steps,
                                   direction = target.UP,
                                   triggerPin = triggerPin, wait = False)
        self.forward = context.controller.monitorSteppers(pin = monitorPin,
                                                          frequency = monitorFrequency)

        context.log("Testing %s reverse..." % self.name())
        context.target.setMicroStepping(self.steps)
        context.target.runSteppers(frequency = 200 * self.steps * stepperTestRPS,
                                   steps = 200 * self.steps,
                                   direction = target.UP,
                                   triggerPin = triggerPin, wait = False)
        self.reverse = context.controller.monitorSteppers(pin = monitorPin,
                                                           frequency = monitorFrequency)
        self.results = [self.forward, self.reverse]

        finished = target.waitForFinish(commands = 2, timeout = 2, clear = True)
        if not finished:
            self.error_string = "Monitoring failed"
            self.status = TestStatus.FAILED


    def _verify(self, context):
        if -1 in self.results:
            self.error_string = "Timed out"
            self.status = TestStatus.FAILED
        else:
            self.status = TestStatus.SUCCESS
            self.error_string = None
            for i in range(5): #Iterate over each stepper
                forward = self.forward[i]
                reverse = self.reverse[i]
                context.log("Forward -> " + str(forward) + \
                            "Reverse -> " + str(reverse))
                for j in range(5): #Iterates over each entry in the test list
                    #Here we fold the recording values onto each other and make sure
                    #each residency time in a flag section is within +- 10 for
                    #the forward and reverse segments
                    validRange = range(reverse[4-j]-10,reverse[4-j]+10)
                    if forward[j] not in validRange and not self.failedAxes[i]:
                        self.errors += "Check "+self.axisNames[i]+" stepper\n"
                        self.failedAxes[i] = True
                        if self.error_string is None:
                            self.error_string = "Failed steppers : %s" % \
                                                self.axisNames[i]
                        else:
                            self.error_string = "%s, %s" % \
                                                (self.error_strng, \
                                                 self.axisNames[i])
                    self.status = TestStatus.FAILED


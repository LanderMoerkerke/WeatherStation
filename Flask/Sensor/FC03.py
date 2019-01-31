from RPi import GPIO
import time, math


class FC03:
    def __init__(self, pin, straal):
        self.__pin = pin
        self.aantal = 0

        self.__radius = straal
        self.__omtrek = math.pi * 2 * straal

        self.__startTimer = time.time()
        self.__tijdTussenRotatie = 0

        self.__RPM = 0

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.__pin, GPIO.IN, GPIO.PUD_UP)
        # GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.__pin, GPIO.BOTH, callback=self.sensorTrigger, bouncetime=20)

    def sensorTrigger(self, pKnop):
        # aantal rotaties + 1
        self.aantal += 1
        # tijd tussen de rotaties
        self.__tijdTussenRotatie = time.time() - self.__startTimer
        # tijd aanpassen
        self.__startTimer = time.time()

    def berekenRPM(self):
        if self.__tijdTussenRotatie != 0:
            self.__RPM = 1 / self.__tijdTussenRotatie * 60
            return self.__RPM
        return 0

    def berekenSnelheid(self):
        if self.__tijdTussenRotatie != 0:
            #              OMZETTEN OMTREK KM                              PER UUR
            return ((self.__omtrek / 100000) / self.__tijdTussenRotatie * 3600)
        return 0

    def getSampleDatabase(self):
        samples = []
        t_end = time.time() + 5
        while time.time() < t_end:
            samples.append(self.berekenSnelheid())
        return (sum(samples) / len(samples))

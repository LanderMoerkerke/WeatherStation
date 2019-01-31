import threading

from Database.DbClass import DbClass
from Sensor.BMP280 import BMP280
from Sensor.MCP3008 import MCP3008
from Sensor.TH02 import TH02
from Sensor.FC03 import FC03


class RecordData():
    # Database connector
    __database = DbClass()

    def __init__(self, pId):
        self.__id = int(pId)

        # lichtsensor
        self.__ls = MCP3008()
        # druksensor + temperatuur
        self.__ds = BMP280()
        # temperatuur + vochtigheid
        self.__ts = TH02()
        # snelheidsmeter
        self.__fc = FC03(26, 5)

        self.__aantalMetingen = 0

        # Periodieke uitvoering van de methode CapturePeriodically (in sec)
        # self.__thread = threading.Timer(5.0, self.CapturePeriodically)

    def getDataSensors(self):
        presTemp = self.__ds.getPresTemp()
        temp = (presTemp[0] + self.__ts.getTemp()) / 2
        lucht = presTemp[1]
        vocht = self.__ts.getHum()
        licht = self.__ls.readChannel(0) / 1023 * 100
        snelheid = self.__fc.getSampleDatabase()
        print(snelheid)

        weerdata = {'temperatuur': temp, 'vochtigheid': vocht, 'luchtdruk': lucht, 'windsnelheid': snelheid,
                    'licht': licht}

        return weerdata

    def insertDataInDatabase(self):
        try:
            dictGegevens = self.getDataSensors()
            self.__database.insertSample(
                dictGegevens['temperatuur'],
                dictGegevens['vochtigheid'],
                dictGegevens['luchtdruk'],
                dictGegevens['windsnelheid'],
                dictGegevens['licht'],
                self.__id, 2
            )
        except:
            print('inserDataInDatabe fail')

    def CapturePeriodically(self):
        actief = self.__database.checkActive(self.__id)
        threading.Timer(30.0, self.CapturePeriodically).start()
        if self.__aantalMetingen == 0:
            self.insertDataInDatabase()
            try:
                print('Capture succesful')
                self.__aantalMetingen += 1
            except:
                # self.__thread.cancel()
                # self.__thread._stop()
                print('Error, capture unsuccesful, thread stopped')
        elif actief:
            self.insertDataInDatabase()
            try:
                print('Capture succesful')
                self.__aantalMetingen += 1
            except:
                # self.__thread.cancel()
                # self.__thread._stop()
                print('Error, capture unsuccesful, thread stopped')

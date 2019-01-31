import smbus, time


class TH02:
    # Registers
    __CONFIGURATION = 0x03
    __STATUS = 0x00
    __DATA = 0x01  # 2 bytes (MSB, LSB)

    def __init__(self, pI2cbus=1, pAddress=0x40):
        self.__bus = smbus.SMBus(pI2cbus)
        self.__ADDRESS = pAddress

    def __getData(self):
        return self.__bus.read_i2c_block_data(self.__ADDRESS, self.__DATA, 2)

    def getStatus(self):
        return self.__bus.read_byte(self.__ADDRESS, self.__STATUS)

    def getTemp(self):
        self.__bus.write_byte_data(0x40, self.__CONFIGURATION, 0x11)
        time.sleep(0.1)
        data = self.__getData()

        # Convert the data to 14-bits
        cTemp = ((data[0] * 256 + (data[1] & 0xFC)) / 4.0) / 32.0 - 50.0
        fTemp = cTemp * 1.8 + 32

        return cTemp

    def getHum(self):
        self.__bus.write_byte_data(0x40, self.__CONFIGURATION, 0x01)
        time.sleep(0.1)
        data = self.__getData()

        # Convert the data to 12-bits
        humidity = ((data[0] * 256 + (data[1] & 0xF0)) / 16.0) / 16.0 - 24.0
        humidity = humidity - (((humidity * humidity) * (-0.00393)) + (humidity * 0.4008) - 4.7844)
        humidity = humidity + (self.getTemp() - 30) * (humidity * 0.00237 + 0.1973)

        return humidity

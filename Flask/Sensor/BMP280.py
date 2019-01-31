import smbus


class BMP280:
    # Registers
    __CALIBRATION_COEFFICIENTS = 0x88  # (24 bytes)
    __CONTROL_MEASUREMENT = 0xF4
    __CONFIGURATION = 0xF5
    __DATA_ALL = 0xF7  # (8 bytes)
    __DATA_PRES = 0xF7  # 3 bytes
    __DATA_TEMP = 0xFA  # 3 bytes

    # Calibration
    __t_fine = 0
    __dig_T1 = __dig_T2 = __dig_T3 = 0
    __dig_P1 = __dig_P2 = __dig_P3 = __dig_P4 = __dig_P5 = __dig_P6 = __dig_P7 = __dig_P8 = __dig_P9 = 0

    def __init__(self, pI2cbus=1, pAddress=0x77):
        self.__bus = smbus.SMBus(pI2cbus)
        self.__ADDRESS = pAddress
        self.__b1 = self.__bus.read_i2c_block_data(self.__ADDRESS, 0x88, 24)

        self.__control_measurement()
        self.__config()

    def __control_measurement(self):
        normalMode = 0x3
        sleepMode = 0x0  # default
        forcedMode = 0x2

        # oversampling (temp en pres beide op x1)
        oversampling = 0x24

        self.__bus.write_byte_data(self.__ADDRESS, self.__CONTROL_MEASUREMENT, oversampling | normalMode)

    def __config(self):
        standbyTime = 0xA0  # (100 ms, enkel bij normal mode)
        self.__bus.write_byte_data(self.__ADDRESS, self.__CONFIGURATION, standbyTime)

    def __calibrationTemperature(self):
        # Convert the data
        # Temp coefficents
        self.__dig_T1 = self.__b1[1] * 256 + self.__b1[0]
        self.__dig_T2 = self.__b1[3] * 256 + self.__b1[2]
        if self.__dig_T2 > 32767:
            self.__dig_T2 -= 65536
            self.__dig_T3 = self.__b1[5] * 256 + self.__b1[4]
        if self.__dig_T3 > 32767:
            self.__dig_T3 -= 65536

    def __calibrationPressure(self):
        # Pressure coefficents
        self.__dig_P1 = self.__b1[7] * 256 + self.__b1[6]
        self.__dig_P2 = self.__b1[9] * 256 + self.__b1[8]
        if self.__dig_P2 > 32767:
            self.__dig_P2 -= 65536
        self.__dig_P3 = self.__b1[11] * 256 + self.__b1[10]
        if self.__dig_P3 > 32767:
            self.__dig_P3 -= 65536
        self.__dig_P4 = self.__b1[13] * 256 + self.__b1[12]
        if self.__dig_P4 > 32767:
            self.__dig_P4 -= 65536
        self.__dig_P5 = self.__b1[15] * 256 + self.__b1[14]
        if self.__dig_P5 > 32767:
            self.__dig_P5 -= 65536
        self.__dig_P6 = self.__b1[17] * 256 + self.__b1[16]
        if self.__dig_P6 > 32767:
            self.__dig_P6 -= 65536
        self.__dig_P7 = self.__b1[19] * 256 + self.__b1[18]
        if self.__dig_P7 > 32767:
            self.__dig_P7 -= 65536
        self.__dig_P8 = self.__b1[21] * 256 + self.__b1[20]
        if self.__dig_P8 > 32767:
            self.__dig_P8 -= 65536
        self.__dig_P9 = self.__b1[23] * 256 + self.__b1[22]
        if self.__dig_P9 > 32767:
            self.__dig_P9 -= 65536

    def getPresTemp(self):
        # Callibration
        self.__calibrationTemperature()
        self.__calibrationPressure()

        # Read data back from 0xF7(247), 8 bytes
        # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
        # Temperature xLSB, Humidity MSB, Humidity LSB
        data = self.__bus.read_i2c_block_data(self.__ADDRESS, self.__DATA_ALL, 8)

        # Convert pressure and temperature data to 19-bits
        adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
        adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16

        # Temperature offset calculations
        var1 = ((adc_t) / 16384.0 - (self.__dig_T1) / 1024.0) * (self.__dig_T2)
        var2 = (((adc_t) / 131072.0 - (self.__dig_T1) / 8192.0) * ((adc_t) / 131072.0 - (self.__dig_T1) / 8192.0)) * (
            self.__dig_T3)
        t_fine = (var1 + var2)
        cTemp = (var1 + var2) / 5120.0
        fTemp = cTemp * 1.8 + 32

        # Pressure offset calculations
        var1 = (t_fine / 2.0) - 64000.0
        var2 = var1 * var1 * (self.__dig_P6) / 32768.0
        var2 = var2 + var1 * (self.__dig_P5) * 2.0
        var2 = (var2 / 4.0) + ((self.__dig_P4) * 65536.0)
        var1 = ((self.__dig_P3) * var1 * var1 / 524288.0 + (self.__dig_P2) * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * (self.__dig_P1)
        p = 1048576.0 - adc_p
        p = (p - (var2 / 4096.0)) * 6250.0 / var1
        var1 = (self.__dig_P9) * p * p / 2147483648.0
        var2 = p * (self.__dig_P8) / 32768.0
        pressure = (p + (var1 + var2 + (self.__dig_P7)) / 16.0) / 100

        return [cTemp, pressure]

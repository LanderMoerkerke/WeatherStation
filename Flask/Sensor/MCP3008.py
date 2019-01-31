import spidev


class MCP3008:
    def __init__(self, pSpiPort=0, pCs=0):
        self.__SpiPort = pSpiPort
        self.__CS = pCs

    def __open(self):
        spi = spidev.SpiDev()
        spi.open(self.__SpiPort, self.__CS)
        return spi

    def readChannel(self, pChannel):
        spi = self.__open()
        adc = spi.xfer2([1, (8 + pChannel) << 4, 0])
        data = ((adc[1] & 3) << 8) | adc[2]  # in byte 1 en 2 zit resultaat
        spi.close()
        return data

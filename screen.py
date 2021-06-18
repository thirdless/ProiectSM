import RPi.GPIO as GPIO
from time import sleep

LINES = 16

class LEDMatrix:

    #matrix rotation, changing the screen orientation from vertical to horizontal
    def rotate_matrix(self, m):
        return [m[j * LINES + i] for i in range(LINES - 1, -1, -1) for j in range(LINES)]

    def Delay(self, timp):
        #sleep(timp / 100000000.0) # 1 timp = ~ 10 ns - alternative option with longer delay, requested from the OS

        #NOP for n number of cycles
        n = 4
        i = 0
        while i < timp * n:
            i += 1

    def __LineSelect(self, line):
        #selecting the current line for the LED matrix, transforming from decimal to binary
        if line >= LINES:
            return

        b = [0] * 4

        for i in range(0, 4):
            b[i] = line >> i
            b[i] = b[i] & 0x1

        GPIO.output(self.__D, b[3])
        GPIO.output(self.__C, b[2])
        GPIO.output(self.__B, b[1])
        GPIO.output(self.__A, b[0])


    def Draw(self, array):
        #from vertical to horizontal
        array = self.rotate_matrix(array)

        #G signal turns the whole screen off, we don't want this
        GPIO.output(self.__G, 0)

        for line in range(0, LINES):
            #setting the signals on low
            GPIO.output(self.__LAT, 0) #latch
            GPIO.output(self.__CLK, 0) #clock
            
            self.__LineSelect(line)

            for column in range(LINES - 1, -1, -1):
                self.Delay(1)

                #sending the current bit on the led
                GPIO.output(self.__DI, array[line * LINES + column])

                #clock signal
                self.Delay(1)
                GPIO.output(self.__CLK, 1)

                self.Delay(1)
                GPIO.output(self.__CLK, 0)

            #latch signal
            GPIO.output(self.__LAT, 1)
            self.Delay(1)


    def __init__(self, D, C, B, A, G, DI, CLK, LAT):
        self.__D = D
        self.__C = C
        self.__B = B
        self.__A = A
        self.__G = G
        self.__DI = DI
        self.__CLK = CLK
        self.__LAT = LAT

        #pins configuration
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(D, GPIO.OUT)
        GPIO.setup(C, GPIO.OUT)
        GPIO.setup(B, GPIO.OUT)
        GPIO.setup(A, GPIO.OUT)
        GPIO.setup(G, GPIO.OUT)
        GPIO.setup(DI, GPIO.OUT)
        GPIO.setup(CLK, GPIO.OUT)
        GPIO.setup(LAT, GPIO.OUT)
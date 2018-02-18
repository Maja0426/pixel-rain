import board
from time import sleep
from digitalio import DigitalInOut, Pull, Direction
import neopixel
from random import randint, choice
import audioio
from microcontroller import reset

btn_a = DigitalInOut(board.BUTTON_A)
btn_a.switch_to_input(pull=Pull.DOWN)
btn_b = DigitalInOut(board.BUTTON_B)
btn_b.switch_to_input(pull=Pull.DOWN)

spkrenable = DigitalInOut(board.SPEAKER_ENABLE)
spkrenable.switch_to_output()
spkrenable.value = True

np = neopixel.NeoPixel(board.A1, 64, brightness=.3, auto_write=0)

PICTURES = ['main_screen_1.txt', '3.txt', '2.txt', '1.txt', 'go.txt', 'game1.txt', 'heart.txt',
'end.txt', 'a.txt', 'main_screen_2.txt']

R, G, B, Y, M, W, T, O, BL  = (64, 0, 0), (0, 32, 0), (0, 0, 32), (32, 32, 0), (32, 0, 32),\
(20, 20, 20), (0, 32, 32), (42, 10, 0), (0, 0, 0)
COLORS = [R, G, B, Y, M, W, T, O]
FLOOR = [56, 57, 58, 59, 60, 61, 62, 63]
PAD_pos, DIG = 58, 51

color = choice(COLORS)
BOMB = randint(9, 14)

def play_file(filename):
    f = open(filename, "rb")
    a = audioio.AudioOut(board.A0, f)
    a.play()
    while a.playing:
        pass
    f.close()

def picread(file):
    f = open(file, 'rt')
    picdata = []
    sordata = []
    pics = []
    for sor in f:
        sor = sor.strip().split()
        sordata.append(sor)
    f.close()
    for i in range(len(sordata)):
        for pix in range(len(sor)):
            if sordata[i][pix] == 'r' or sordata[i][pix] == 'R':
                pic_color = R
            if sordata[i][pix] == 'g' or sordata[i][pix] == 'G':
                pic_color = G
            if sordata[i][pix] == 'b' or sordata[i][pix] == 'B':
                pic_color = B
            if sordata[i][pix] == 'w' or sordata[i][pix] == 'W':
                pic_color = W
            if sordata[i][pix] == 'y' or sordata[i][pix] == 'Y':
                pic_color = Y
            if sordata[i][pix] == 'o' or sordata[i][pix] == 'O':
                pic_color = O
            if sordata[i][pix] == 'm' or sordata[i][pix] == 'M':
                pic_color = M
            if sordata[i][pix] == '0':
                pic_color = BL
            picdata.append(pic_color)
    for i in range(len(picdata)):
        pics.append([i, picdata[i]])
    return pics

def picdraw(pics):
    pics = picread(pics)
    for i in range(len(pics)):
        np[i] = (pics[i][1])
    np.show()

def scroll(pics, direction):
    pics = picread(pics)
    if direction == 'down':
        for sor in range(64, -1, -8):
            for i in range(sor, len(pics)):
                np[i-sor] = (pics[i][1])
            np.show()
        np.fill((0,0,0))
    elif direction == 'up':
        for sor in range(64, -1, -8):
            for i in range(len(pics)-sor):
                np[i+sor] = (pics[i][1])
            np.show()
        np.fill((0,0,0))

def PAD(color):
    for i in range(PAD_pos, PAD_pos+3):
        np[i] = color
    np[PAD_pos-8] = color
    np[PAD_pos-6] = color

def RainCloud():
    for i in range(8):
        np[i] = choice(COLORS)

scroll(PICTURES[0], 'down')
while btn_a.value != True:
    for i in range(-1, 1):
        picdraw(PICTURES[i])
        sleep(.1)
np.fill((0, 0, 0))
for i in range(1, 5):
    scroll(PICTURES[i], 'down')
    play_file('Beep1.wav')
sleep(.1)
scroll(PICTURES[5], 'up')

life = 3

while True:
    PAD(color)
    RainCloud()
    np[BOMB] = color
    for i in range(8):
        if (BOMB == FLOOR[i] or BOMB == PAD_pos-8 or BOMB == PAD_pos-6) and life != 0:
            life -= 1
            np[BOMB] = color
            np.show()
            play_file("Explosion3.wav")
            for g in range(224, -1, -16):
                PAD((g, g, g))
                np[BOMB] = (g, g, g)
                np.show()
            sleep(.1)
            np.fill((0, 0, 0))
            BOMB = randint(9, 14)
            if life == 0:
                scroll('end.txt', 'down')
                while btn_a.value != True:
                    picdraw('end.txt')
                    sleep(1)
                    picdraw('a.txt')
                    sleep(1)
                reset()
            if life > 0:
                for i in range(life):
                    scroll(PICTURES[6], 'down')
                    play_file('Beep1.wav')
                    sleep(.3)
        elif BOMB == DIG:
            break
        elif BOMB == PAD_pos+1:
            np[PAD_pos+1] = color
            break
    if btn_a.value == True and DIG > 48:
        DIG -= 1
        PAD_pos -= 1
    if btn_a.value == True and DIG == 48:
        DIG = 54
        PAD_pos = 61
    if btn_b.value == True and DIG < 55:
        DIG += 1
        PAD_pos += 1
    if btn_b.value == True and DIG == 55:
        DIG = 49
        PAD_pos = 56
    BOMB += 8
    if BOMB > 63:
        BOMB = randint(9, 14)
        play_file('Beep8.wav')
        color = choice(COLORS)
    np.show()
    sleep(.1)
    np.fill((0, 0, 0))

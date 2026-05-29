import random


def Glider(world):
    world[1][1].currState = 1
    world[1][3].currState = 1
    world[2][2].currState = 1
    world[2][3].currState = 1
    world[3][2].currState = 1


def GosperGun(world):
    world[5][1].currState = 1
    world[5][2].currState = 1
    world[6][1].currState = 1
    world[6][2].currState = 1
 
    world[3][13].currState = 1
    world[3][14].currState = 1
    world[4][12].currState = 1
    world[4][16].currState = 1
    world[5][11].currState = 1
    world[5][17].currState = 1
    world[6][11].currState = 1
    world[6][15].currState = 1
    world[6][17].currState = 1
    world[6][18].currState = 1
    world[7][11].currState = 1
    world[7][17].currState = 1
    world[8][12].currState = 1
    world[8][16].currState = 1
    world[9][13].currState = 1
    world[9][14].currState = 1
 
    world[1][25].currState = 1
    world[2][23].currState = 1
    world[2][25].currState = 1
    world[3][21].currState = 1
    world[3][22].currState = 1
    world[4][21].currState = 1
    world[4][22].currState = 1
    world[5][21].currState = 1
    world[5][22].currState = 1
    world[6][23].currState = 1
    world[6][25].currState = 1
    world[7][25].currState = 1
 
    world[3][35].currState = 1
    world[3][36].currState = 1
    world[4][35].currState = 1
    world[4][36].currState = 1


def Pulsar(world):
    world[1][3].currState = 1
    world[1][4].currState = 1
    world[1][5].currState = 1
    world[1][9].currState = 1
    world[1][10].currState = 1
    world[1][11].currState = 1

    world[3][1].currState = 1
    world[3][6].currState = 1
    world[3][8].currState = 1
    world[3][13].currState = 1
    world[4][1].currState = 1
    world[4][6].currState = 1
    world[4][8].currState = 1
    world[4][13].currState = 1
    world[5][1].currState = 1
    world[5][6].currState = 1
    world[5][8].currState = 1
    world[5][13].currState = 1

    world[6][3].currState = 1
    world[6][4].currState = 1
    world[6][5].currState = 1
    world[6][9].currState = 1
    world[6][10].currState = 1
    world[6][11].currState = 1

    world[8][3].currState = 1
    world[8][4].currState = 1
    world[8][5].currState = 1
    world[8][9].currState = 1
    world[8][10].currState = 1
    world[8][11].currState = 1

    world[9][1].currState = 1
    world[9][6].currState = 1
    world[9][8].currState = 1
    world[9][13].currState = 1
    world[10][1].currState = 1
    world[10][6].currState = 1
    world[10][8].currState = 1
    world[10][13].currState = 1
    world[11][1].currState = 1
    world[11][6].currState = 1
    world[11][8].currState = 1
    world[11][13].currState = 1

    world[13][3].currState = 1
    world[13][4].currState = 1
    world[13][5].currState = 1
    world[13][9].currState = 1
    world[13][10].currState = 1
    world[13][11].currState = 1


def LWSS(world):
    world[1][2].currState = 1
    world[1][3].currState = 1
    world[1][4].currState = 1
    world[1][5].currState = 1
    world[2][1].currState = 1
    world[2][5].currState = 1
    world[3][5].currState = 1
    world[4][1].currState = 1
    world[4][4].currState = 1


def Random(world):
    for y in range(1, len(world) - 1):
        for x in range(1, len(world[0]) - 1):
            world[y][x].currState = random.randint(0,1)
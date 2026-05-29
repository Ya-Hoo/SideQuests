# Get file contents
FILENAME = input("Enter file name: ")
DIRECTORY_STRING = r"all" + "\\" + FILENAME
fileContent = []
file = open(DIRECTORY_STRING, 'r')
for line in file:
    if '#' in line:
        continue
    fileContent.append(line.strip())
file.close()

# Process contents into computable form
META_DATA = []
for data in fileContent[0].split(", "):
    dataValue = data.split(" = ")[1]
    try:
        META_DATA.append(int(dataValue))
    except ValueError:
        META_DATA.append(dataValue)

PATTERN_RAW = (''.join(fileContent[1::])).split('$')

WIDTH, HEIGHT = META_DATA[0], META_DATA[1]

# Turn RAW_PATTERN into processable form
for i in range(HEIGHT):
    new_line = []
    repeat = 0
    for j in range(len(PATTERN_RAW[i])):
        if PATTERN_RAW[i][j] in ['b', 'o']:
            if repeat != 0:
                new_line.append(repeat)
            else:
                new_line.append(1)
            new_line.append(PATTERN_RAW[i][j])
            repeat = 0
        elif PATTERN_RAW[i][j].isnumeric():
            repeat *= 10
            repeat += int(PATTERN_RAW[i][j])
    PATTERN_RAW.append(new_line)

for i in range(len(PATTERN_RAW)//2):
    PATTERN_RAW.pop(0)

# Turn the world into the pattern imported
def pattern(world):
    tag = {
        'b': 0,
        'o': 1
    }

    for index, line in enumerate(PATTERN_RAW):
        indent = 0
        for i in range(1, len(line), 2):
            repeat = line[i - 1]
            for j in range(repeat):
                world[index + 2][indent + 2].currState = tag[line[i]]
                indent += 1
import ascii
def createMap(size, fillCharacter, playerSymbol="#"):
    m = {}
    m["grid"] = []
    m["size"] = size  # map size (square)
    m["pSym"] = playerSymbol
    m["fillCharacter"] = fillCharacter
    m["pRow"] = 0
    m["pCol"] = 0

    # Make the empty grid
    for x in range(m["size"]):
        m["grid"].append([])  # make it a size-by-size 2D list

    # fill it with the fillCharacter
    for row in m["grid"]:
        for x in range(m["size"]):
            row.append(m["fillCharacter"])
    return m


def displayMap(m):
    # Top label
    count = 0
    print(" ", end="")
    print(ascii.fort_boise)
    for x in range(m["size"]):
        #print(' ', count, end="")
        count += 1
    print()


    # Each row
    count = 0
    for row in m["grid"]:
        print(count, end="")
        for col in row:
            print(col, end="")
        count += 1
        print()
    print(ascii.oregon_city)

def setPlayerPos(m, row, col):
    if row >= m["size"] or row < 0 or col >= m["size"] or col < 0:
        print(f"Invalid location:{row} {col}")
    else:
        curRow = m["pRow"]
        curCol = m["pCol"]

        # overwrite the old position
        m["grid"][curRow][curCol] = m["fillCharacter"]  # brutal syntax...

        # update pos
        m["pRow"] = row
        m["pCol"] = col

        # update the map
        m["grid"][row][col] = m["pSym"]

def getPlayerPos(m):
    position = m["pRow"]
    return position

def move(m, direction):
    if direction == "down":
        setPlayerPos(m, m["pRow"] + 1, m["pCol"])
    elif direction == "up":
        setPlayerPos(m, m["pRow"] - 1, m["pCol"])
    elif direction == "left":
        setPlayerPos(m, m["pRow"], m["pCol"] - 1)
    elif direction == "right":
        setPlayerPos(m, m["pRow"], m["pCol"] + 1)
    else:
        print("Invalid direction:", direction)


# Add something to the map
def add(m, row, col, symbol):
    m["grid"][row][col] = symbol
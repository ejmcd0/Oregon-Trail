'''
This game is a simpler version of The Oregon Trail

1. Create main menu with story and rules
2. Create characters (banker, carpenter, farmer)
    - each character starts with a different amt of money and skill level
3. Have user select and name character, then name 4 other wagon-mates
4. Create supply store
    -oxen, ammo, food, clothing
5. Create in game menu
    - continue on trail
    - check supplies
    - hunt
    - buy supplies (if at landmark)
    - rest (increases health)
6. Create header for game that displays throughout entire game
    - date
    - health
    - miles to go
    - lbs of food left
7. Generate random events/encounters
    - illness (lose health)
    - thieves (lose supplies)
    - ox hurt/died
    - death of wagon-mates
    - found wild fruit (increase lbs of food)
    - found abandoned wagon
8. Hunting
    - random chance to shoot animal
    - increases lbs of food
    - decreases ammo
9. Crossing a river
    - ford (high chance of losing supplies, 3 days)
    - caulk wagon and float (medium chance of losing supplies, 5 days)
    - take ferry (decrease money, add 4 days)
10. Create a save and load feature
'''
import pickle
import random
import ascii
import map
from datetime import datetime
from time import time, sleep
from gameDate import GameDate

NAME = 0
TYPE = 1
MONEY = 2
HP = 3
LEVEL = 4

# place holders in inventory
OXEN = 0
AMMO = 1
CLOTHES = 2
FOOD = 3

DIVIDER = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

BIN_FILE = 'oregontrail.bin'


def sPrint(text, delay=0.03):
    import time
    for x in text:
        print(x, end="")
        time.sleep(delay)
    print()


def displayIntro():
    story = """
    Get ready to complete the last leg of The Oregon Trail. As the wagon leader, 
    it is up to you to get your party from Fort Boise to Oregon City. This trek is 
    about 500 miles of plains, rivers, and mountains in a covered wagon. Beware of 
    thieves, cholera, snakebites, and other potential fatalities. If you can make it 
    all the way and complete the Oregon Trail, acres of free, fertile farmland are yours 
    to claim! Your adventure awaits!
    """
    rules = """
    Choose your profession - banker, carpenter, or farmer. Each option presents a different 
    amount of money to start with, as well as difficulty level. If you run low on supplies, 
    you can hunt for food or stop into a shop if there's one nearby. How will you cross the 
    rivers? You can attempt to ford the river or caulk your wagon and try to float across, 
    hoping you and your wagon aren't swallowed alive! If you have money, you can take a ferry. 
    Resting and having an adequate food supply can increase health. Good luck, travelers!
    """
    choice = input("View the story? (y/n): ")
    if choice.lower() == "y":
        sPrint(story)
        print(DIVIDER)
    choice = input("View the rules? (y/n): ")
    if choice.lower() == "y":
        sPrint(rules, 0.06)
        print(DIVIDER)


def gamePlay(inventory, game_date, player, party, m, milesLeft=None):
    if milesLeft is None:
        totalMiles = loadGame(BIN_FILE)[0]  # load miles from saved game
    else:
        totalMiles = milesLeft  # if a value is provided, use that

    gameOn = True  # when true, the game is still happening

    # Setting up for three different timers
    lastAction = {
        "sixty_seconds": time(),
        "fifteen_seconds": time(),
        "forty_seconds": time()
    }

    while gameOn:
        currentTime = time()

        if currentTime - lastAction['sixty_seconds'] > 60:  # if current time - the 60 second timer is greater than 60
            game_date.advance_days(1)  # date increases
            map.move(m, "down")  # move down on the map
            lastAction['sixty_seconds'] = currentTime  # reset the timer

        if currentTime - lastAction['fifteen_seconds'] > 15:  # every 15 seconds
            inventory[FOOD] -= 13  # food eaten
            totalMiles -= 23  # miles traveled
            lastAction['fifteen_seconds'] = currentTime
            # return totalMiles

        if currentTime - lastAction['forty_seconds'] > 40:  # every 40 seconds, random encounter
            encounter(player, inventory, party, m)
            lastAction['forty_seconds'] = currentTime

        if inventory[OXEN] <= 0:  # no oxen to pull wagon
            gameOn = False
            return "stuck"
        elif inventory[FOOD] <= -10:  # not enough food
            gameOn = False
            return "starved"
        elif len(party) == 0:  # everyone is dead
            gameOn = False
            return "grim fate"
        elif map.getPlayerPos(m) == 9 and totalMiles <= 0:  # user survived the whole trail
            gameOn = False
            return "oregon"
        elif inventory[CLOTHES] < 0:  # no clothes for your wagon party, plus a little buffer - why it isnt <= 0
            gameOn = False
            return "frozen"
        elif saveGame(totalMiles, inventory, game_date, player, party, m):
            return "saved"

        header = gameHeader(player, inventory, game_date, totalMiles)
        print(header)  # always show header if not in menu

        if view_menu():  # opens gameMenu if user enters "M"
            gameMenu(inventory, party, m, player, game_date, totalMiles)

        if player[HP] <= 0 and inventory[FOOD] <= -10:  # if the player has no health or food
            gameOn = False

        # Encounters based on map position
        if map.getPlayerPos(m) == 2 or map.getPlayerPos(m) == 6:
            crossRiver(inventory, party, player, game_date)
            map.move(m, "down")  # move on the map after crossing the river
        if map.getPlayerPos(m) == 4:
            print(ascii.fort_1)
            sPrint("Welcome to The Dalles. The shop is open.")
        if map.getPlayerPos(m) == 8:
            print(ascii.fort_2)
            sPrint("Welcome to Fort Walla Walla. The shop is open.")

    return totalMiles


def view_menu():
    return input('Press M to view menu: ').lower() == 'm'


def gameHeader(player, inventory, game_date, totalMiles):
    while True:
        dateNow = game_date.current_date.strftime('%B %d, %Y')  # reformats the date

        header = f'''
        -=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-
                            {dateNow}

            HEALTH         MILES REMAINING        FOOD REMAINING 
             {player[HP]}\t\t\t   {totalMiles} miles \t\t\t  {inventory[FOOD]} lbs 

                    press M at any time to view menu
        -=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-
        '''

        return header


def gameMenu(inventory, party, m, player, game_date, totalMiles):
    inMenu = True
    menu = '''
    1. Continue on trail
    2. Check inventory
    3. Wagon party
    4. Display map
    5. Hunt for food
    6. Rest
    7. Shop for supplies (if shop is nearby)
    8. View progress
    9. Save game
    '''

    showInventory = f'''
    OXEN: {inventory[OXEN]}
    AMMO: {inventory[AMMO]} bullets
    CLOTHES: {inventory[CLOTHES]} outfits
    FOOD: {inventory[FOOD]} lbs
    '''

    while inMenu:
        print(menu)
        choice = input(">>> ")
        if choice in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            if choice == "1":
                encounter(player, inventory, party, m)
                break  # break will return us to the header once the action is done
            elif choice == "2":
                print(showInventory)
                break
            elif choice == "3":
                print("Party Members:")
                for person in party:
                    print("- " + person)  # print each person in the wagon party
                break
            elif choice == "4":
                map.displayMap(m)
                break
            elif choice == "5":
                hunt(inventory)
                break
            elif choice == "6":
                sPrint("You rest for 2 days.")  # resting restores health and adds 2 days
                player[HP] += 20
                game_date.advance_days(2)
                break
            elif choice == "7" and (  # the shop is only available if you
                    map.getPlayerPos(m) == 4 or  # are at the starting position or one of the forts
                    map.getPlayerPos(m) == 8 or
                    map.getPlayerPos(m) == 0
            ):
                inventory = supplyStore(player, inventory)
                break

            elif choice == "8":  # return to header
                break
            elif choice == "9":
                saveGame(totalMiles, inventory, game_date, player, party, m)
                sPrint("Your progress has been saved.")
                exit()
            else:
                sPrint("There is no shop nearby.")  # catches if the user presses 7 not near a shop
        else:
            sPrint("Please enter a valid selection")
    return inventory  # updates the inventory


def createCharacter():
    player = ["", "", 0, 0, 0]
    characterMenu = '''
    Many kinds of people made the journey on The Oregon Trail.

    You may:

    1. Be a banker from Boston
        - Easy
        - 500 HP
        - $1000
    2. Be a carpenter from Ohio
        - Normal
        - 350 HP
        - $750
    3. Be a farmer from Illinois
        - Brutal
        - 200 HP
        - $400

    What is your choice? (1, 2, or 3)

    '''

    print(characterMenu)
    choice = input(">>> ")
    while choice not in ("1", "2", "3"):
        print("Please make a valid selection.")
        choice = input(">>> ")
    if choice == "1":
        print(ascii.banker2)
        player[NAME] = input("What is the first name of the wagon leader?: ")
        while len(player[NAME]) == 0:  # wagon leader must have a name
            player[NAME] = input("What is the first name of the wagon leader?: ")
        player[TYPE] = "Banker"
        player[MONEY] = 1000
        player[HP] = 500
        player[LEVEL] = 1

        return player
    elif choice == "2":
        print(ascii.carpenter)
        player[NAME] = input("What is the first name of the wagon leader?: ")
        while len(player[NAME]) == 0:
            player[NAME] = input("What is the first name of the wagon leader?: ")
        player[TYPE] = "Carpenter"
        player[MONEY] = 750
        player[HP] = 350
        player[LEVEL] = 2
        return player
    elif choice == "3":
        print(ascii.farmer)
        player[NAME] = input("What is the first name of the wagon leader?: ")
        while len(player[NAME]) == 0:
            player[NAME] = input("What is the first name of the wagon leader?: ")
        player[TYPE] = "Farmer"
        player[MONEY] = 400
        player[HP] = 200
        player[LEVEL] = 3
        return player


def wagon_party():
    party = []
    names = "What are the first names of the four other members in your party? Enter one at a time."
    print(names)
    for i in range(4):
        name = input(">>> ")
        while len(name) == 0:
            print("Enter party member's name")
            name = input(">>> ")
        party.append(name)
    return party


def supplyStore(player, existing_inventory=None):
    if existing_inventory == None:
        inventory = [0, 0, 0, 0]  # use this the first time we go into the store
    else:
        inventory = existing_inventory  # this prevents the inventory from resetting
        # if we go back into the store later on
    keepShopping = True
    storeMenu = '''
    ------------------------------------------------------------
    | Welcome to Otto's Outpost! What can I get for you today? |
    ------------------------------------------------------------

    1. Oxen $20
    2. Ammo $3/box, 10 bullets/box
    3. Clothes $10
    4. Food $1/lb
    5. Exit store

    '''

    while player[MONEY] > 0 and keepShopping:  # while the player has money and keepShopping is true
        print(f"You have ${player[MONEY]}")
        print(storeMenu)

        purchase = int(input("Make a selection\n>>> "))
        while purchase not in (1, 2, 3, 4, 5):
            purchase = int(input("Make a selection\n>>> "))
        if purchase in range(1, 5):  # actually 1-4
            how_many = int(input("How many would you like to purchase?: "))
            if purchase == 1:
                cost = how_many * 20  # number purchased times cost of item
            elif purchase == 2:
                cost = how_many * 3
            elif purchase == 3:
                cost = how_many * 10
            elif purchase == 4:
                cost = how_many
            if player[MONEY] < cost:  # if the player has less money than what the purchase costs
                sPrint("You don't have enough money to buy that.")
                continue
            else:  # had to separate this so the inventory doesn't increase when the player doesn't have enough $
                if purchase == 1:
                    inventory[OXEN] += how_many  # adds to inventory
                elif purchase == 2:
                    inventory[AMMO] += (how_many * 10)
                elif purchase == 3:
                    inventory[CLOTHES] += how_many
                elif purchase == 4:
                    inventory[FOOD] += how_many
                player[MONEY] -= cost  # subtracts what the player spent from what they have
        elif purchase == 5:  # can't exit the store without certain necessary supplies
            if inventory[OXEN] < 2:
                sPrint("You need at least 2 oxen to pull your wagon.")
            elif inventory[FOOD] <= 0:
                sPrint("You won't make it very far without food.")
            else:
                break  # exit store
        else:
            print("Please make a valid selection")

    return inventory, storeMenu


def hunt(inventory):
    print(ascii.deer)

    if inventory[AMMO] < 10:
        sPrint("You do not have enough ammo to hunt.")
        return  # exits the hunt option without giving the option to hunt
    shoot = input("Press 'S' to shoot or 'X' to escape\n>>> ").lower()
    if shoot == 'x':
        return  # escapes the hunting screen
    elif shoot == 's':
        chance = random.randint(1, 5)
        if chance == 2:  # if the random number is 2, the animal has been shot
            inventory[FOOD] += 100
            sPrint("Good aim. From the animal you shot, you got 100 pounds of meat.")
        else:
            sPrint("No luck this time.")
        inventory[AMMO] -= 10  # takes ammo regardless of if the hunt was successful or not


def crossRiver(inventory, party, player, game_date):
    menu = """

    1. Ford the river on foot
    2. Caulk the wagon and float
    3. Take a ferry for $10

    """
    print(ascii.river)
    print(menu)
    choice = input(">>> ")
    while choice not in ("1", "2", "3"):
        print("Please make a valid selection.")
        choice = input(">>> ")
    if choice == "1":
        game_date.advance_days(3)
        odds = random.randint(1, 10)
        if odds in (3, 4, 5, 6):  # fording the river is risky, high chance of losing items/party members
            inventory[CLOTHES] -= 2
            bulletsLost = random.randint(1, inventory[AMMO] - 1)
            inventory[AMMO] -= bulletsLost
            sPrint(f"The water was higher than anticipated. You lost 2 outfits and {bulletsLost} bullets.")

        else:
            sPrint("Your party and wagon made it across the river safely.")
    elif choice == "2":
        game_date.advance_days(5)
        odds = random.randint(1, 4)
        if odds in (2, 3):
            inventory[OXEN] -= 1
            n = random.randint(0, len(party) - 1)
            casualty = party.pop(n)  # removes casualty from list of party members
            print(ascii.gravestone)
            sPrint(f"Your wagon sunk. You lost 1 ox and {casualty}.")
            return party
        else:
            sPrint("You made it across the river safely.")
    elif choice == "3":
        game_date.advance_days(4)
        player[MONEY] -= 10
        sPrint("You made it across the river safely.")
        return player


def encounter(player, inventory, party, m):
    odds = random.randint(0, 75)
    if len(party) == 0:  # if nobody is left in the wagon party
        print(ascii.gravestone)
        sPrint(f"{player[NAME]} has died of dysentery.")
        gameOn = False  # ends game

    # encounters based on random number (odds)
    if odds in range(0, 4):
        stolen = random.randint(0, inventory[CLOTHES])
        inventory[CLOTHES] -= stolen
        sPrint(f"A thief comes during the night and steals {stolen} sets of clothing.")
    elif odds in range(4, 9):
        inventory[OXEN] -= 1
        sPrint("One of your ox has fallen sick and died.")
    elif odds in range(9, 14):
        player[HP] -= 30
        sPrint(f"{party[random.randint(0, len(party) - 1)]} has cholera.")
    elif odds in range(14, 20):
        person = random.randint(0, len(party) - 1)
        casualty = party[person]
        player[HP] -= 40
        print(ascii.gravestone)
        sPrint(f"{casualty} has died of typhoid.")
        party.pop(person)
        return party
    elif odds in range(20, 25):
        player[HP] += 10
        inventory[FOOD] += 10
        sPrint("You found edible wild fruit.")
    elif odds in range(25, 30):
        person = random.randint(0, len(party) - 1)
        casualty = party[person]
        player[HP] -= 40
        print(ascii.gravestone)
        sPrint(f"{casualty} has died of a snake bite.")
        party.pop(person)
        return party
    elif odds in range(30, 36):
        foodFound = random.randint(1, 50)
        clothesFound = random.randint(1, 5)
        ammoFound = random.randint(1, 100)
        inventory[FOOD] += foodFound
        inventory[CLOTHES] += clothesFound
        inventory[AMMO] += ammoFound
        sPrint(f"You've come across an abandoned wagon. "
               f"You salvaged {foodFound}lbs of food, {clothesFound} outfits, "
               f"and {ammoFound} bullets.")
    elif odds in range(44, 50):
        player[HP] -= 20
        sPrint(f"You have broken your arm.")
    elif odds in range(36, 44) or range(50, 76):
        sPrint("Travelling along the trail.")

    sleep(.5)


def ending(result):  # what prints depending on how the game ends
    if result == "starved":
        print(ascii.starved)
        sPrint("You ran out of food and starved to death.")
    elif result == "oregon":
        print(ascii.celebrate)
        sPrint("Congratulations, you completed the Oregon Trail!")
    elif result == "grim fate":
        print(ascii.perished)
        sPrint("You and your entire party have perished.")
    elif result == "stuck":
        print(ascii.no_cows)
        sPrint("You cannot continue with no oxen to pull your wagon.")
    elif result == "frozen":
        print(ascii.froze)
        sPrint("You do not have any clothes left. You and your party froze to death in the mountains.")
    elif result == "saved":
        sPrint("Your progress has been saved.")


def saveGame(totalMiles, inventory, dateInGame, player_1, party, theMap):
    saveData = {
        "totalMiles": totalMiles,
        "inventory": inventory,
        "dateInGame": dateInGame,
        "player_1": player_1,
        "party": party,
        "theMap": theMap
    }
    with open(BIN_FILE, 'wb') as writeBin:
        pickle.dump(saveData, writeBin)


def loadGame(BIN_FILE):
    with open(BIN_FILE, 'rb') as readBin:
        loadData = pickle.load(readBin)
        milesLeft = loadData["totalMiles"]
        inventory = loadData["inventory"]
        dateInGame = loadData["dateInGame"]
        player_1 = loadData["player_1"]
        party = loadData["party"]
        theMap = loadData["theMap"]
        return milesLeft, inventory, dateInGame, player_1, party, theMap


def main():
    load_successful = False
    startDate = datetime(1846, 3, 1)
    dateInGame = GameDate(startDate)
    print(ascii.title + ascii.wagon)
    load_game = input("Load previous game? y/n: ").lower()
    if load_game == 'y':
        try:
            milesLeft, inventory, dateInGame, player_1, party, theMap = loadGame(BIN_FILE)
            load_successful = True
        except FileNotFoundError:
            print("This file does not exist.")
        except EOFError:
            print("This file is empty.")

    if not load_successful:  # this will catch if the user tries to load a game and it
        # isn't successful, or if the user chooses to start a new game
        milesLeft = 500  # resets totalMiles when starting a new game
        displayIntro()
        sleep(1)
        player_1 = createCharacter()
        sleep(.5)
        party = wagon_party()

        leavingTips = f"""
        Before leaving Fort Boise, you should buy supplies. You have ${player_1[MONEY]} in cash 
        but you don't have to spend it all now.
        You will need:
        - a team of oxen to pull your wagon (at least 6 is recommended)
        - clothing for both summer and winter (1-2 outfits per person)
        - plenty of food for the trip (50lbs per person is recommended)
        - ammunition for your rifles
        """
        sleep(1)
        print(DIVIDER)
        sPrint(leavingTips)
        print(DIVIDER)
        sleep(1)

        inventory, storeMenu = supplyStore(player_1)  # existing_inventory does not need to be defined -it is set to
        # none and this is the first time we are going into the shop

        theMap = map.createMap(10, " ⛰ ", " 𖥞 ")  # creates a 10x10 map of mountains with
        # the wagon wheel representing the player
        map.setPlayerPos(theMap, 0, 5)  # start the player at row 0, column 5
        sleep(1)
    result = gamePlay(inventory, dateInGame, player_1, party, theMap, milesLeft)  # returns how the game ends
    ending(result)  # prints the ending
    sleep(.5)


main()
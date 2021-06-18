import os
import screen

BIG_DIMENSIONS = {"width": 8, "height": 7}
SMALL_DIMENSIONS = {"width": 3, "height": 5}

big_characters = {}
small_characters = {}

TYPE_BIG = 1
TYPE_SMALL = 2

#reading the character from file on init
def get_matrix(path, dimensions):
    filename = os.path.dirname(os.path.abspath(__file__)) + path
    array = [1] * (dimensions["width"] * dimensions["height"])
    arrayIndex = 0
    
    if os.path.exists(filename):
        file = open(filename, "r", encoding="utf-8")
        lines = file.read().split('\n')

        #reading each line
        for i in range(0, len(lines)):
            columns = lines[i].split(' ')

            #reading every value on the line
            for j in range(0, len(columns)):
                if columns[j] != "":
                    #int to string casting, and if it is impossible, turn the led off
                    try:
                        array[arrayIndex] = int(columns[j])
                    except:
                        array[arrayIndex] = 1

                    #moving to the next stored bit
                    arrayIndex += 1

                #returning from the function if the values count is bigger than the char dimension
                if arrayIndex >= (dimensions["width"] * dimensions["height"]):
                    break

            if arrayIndex >= (dimensions["width"] * dimensions["height"]):
                break

    return array

def place_character_intern(parent, character, dimensions, position):
    index = 0
    #replacing the lines with the character values
    for i in range(position["top"], position["top"] + dimensions["height"]):
        for j in range(position["left"], position["left"] + dimensions["width"]):
            parent[i * screen.LINES + j] = character[index]
            index += 1

    return parent

#function to place the char on the given position by type - BIG / SMALL
def place_character(parent, character, type, position):
    dimensions = BIG_DIMENSIONS
    array = big_characters

    if type == TYPE_SMALL:
        dimensions = SMALL_DIMENSIONS
        array = small_characters
    elif type == TYPE_BIG:
        pass
    else:
        return

    return place_character_intern(parent, array[character], dimensions, position)

#module initialization
def init():
    #storing the numbers
    for i in range(0, 10):
        big_characters[i] = get_matrix("/big_numbers/" + str(i), BIG_DIMENSIONS)
        small_characters[i] = get_matrix("/small_numbers/" + str(i), SMALL_DIMENSIONS)

    # and the special characters
    small_characters["o"] = get_matrix("/small_numbers/o", SMALL_DIMENSIONS)
    small_characters["i"] = get_matrix("/small_numbers/i", SMALL_DIMENSIONS)
    small_characters["-"] = get_matrix("/small_numbers/dash", SMALL_DIMENSIONS)

init()
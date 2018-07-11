from sys import exit

from random import randint
import re


# design notes:
# want to add, looking at items in your inventory
# because when we look at a container we only get the name
# and thus we have to take it to look at it (description)
# else, we can search the container objects in the room?
# use "if key in dictionary" as needed
# figure out how to print lines after without needing newlines

def print_remap(stri):
    print((stri.rstrip()))

def pretty_print_w(text_list, width, offset):
    # type: (list, int, int) -> string
    print_width = width
    return_string = ""
    # make one big ass string
    big_string = ""
    for i in text_list:
        big_string += i

    re.sub(r"\s+", "", big_string)
    words = re.split(" ", big_string)

    char_count = offset
    working_line = " " * offset
    for word in words:
        if (char_count + len(word)) > print_width:
            return_string += "%s\n" % working_line
            working_line = " " * offset
            working_line += word
            char_count = offset + len(word)
        else:
            working_line += word
            char_count += len(word)

        if char_count < print_width:
            working_line += " "
            char_count += 1

    if char_count > 0:
        return_string += "%s\n" % working_line

    return return_string


def pretty_print(text_list):
    return pretty_print_w(text_list, 80, 0)


def pretty_response(text_list):
    return pretty_print_w(text_list, 80, 10)


def pretty_list(text_list):
    last = len(text_list)
    c = 1
    final = ""
    for word in text_list:
        if c == 1:
            final += word
        elif c == last:
            final += " and %s" % word
        else:
            final += ", %s" % word
        c += 1
    return final


#######################################################################
## Command Class and sub-classes
#######################################################################
class Command(object):
    def __init__(self, verb, verb_orig, noun, noun_orig, target, target_orig, full):
        self.verb = verb
        self.verb_orig = verb_orig
        self.noun = noun
        self.noun_orig = noun_orig
        self.target = target
        self.target_orig = target_orig
        self.full = full


#######################################################################
## Room Class and sub-classes
#######################################################################

class Room(object):
    add_room = False

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.people_here = {}
        self.exits = {}
        self.response = "No response yet"

    def add_item(self, item):
        self.items_here[item.name.lower()] = item

    def take_item(self, item_name):
        if item_name in self.items_here:
            item = self.items_here[item_name]
            del self.items_here[item_name]
            return item
        else:
            for x in self.items_here:
                if self.items_here[x].is_container():
                    item = self.items_here[x].take_item(item_name)
                    if item:
                        return item
            return None

    def add_person(self, person):
        self.people_here[person.name.lower()] = person

    def move_person(self, person):
        person = self.people_here[person.name.lower()]
        del self.people_here[person.name.lower()]
        return person

    def add_exit(self, room):
        self.exits[room.name.lower()] = room

    def describe(self):
        stri = "%s " % self.description
        return stri

    def find_item_in_items(self, item_name):
        item = self.items_here.get(item_name)
        if item:
            return item
        else:
            for x in self.items_here:
                if self.items_here[x].is_container():
                    item_here = self.items_here[x].find_item(item_name)
                    if item_here:
                        return item_here
            return None

    def find_item_on_person(self, item_name):
        for x in self.people_here:
            item_found = self.people_here[x].find_item(item_name)
            if item_found:
                return item_found
        return None

    def find_item_here(self, item_name):
        item = self.find_item_in_items(item_name)
        if not item:
            item = self.find_item_on_person(item_name)
        return item

    def find_item_container(self, item_name):
        if item_name in self.items_here:
            return self
        for person in self.people_here:
            if self.people_here[person].find_item(item_name):
                return self.people_here[person]
        for item in self.items_here:
            if self.items_here[item].is_container():
                item_here = self.items_here[item].find_item_container(item_name)
                if item_here:
                    return item_here
        return None

    def enter(self):
        text_block = []
        text_block.append(self.describe())
        if self.items_here:
            for item in self.items_here.values():
                text_block.append(item.view())

        if self.people_here:
            for people in self.people_here.values():
                text_block.append(people.view())

        if self.exits:
            for exit_ in self.exits:
                name = self.exits[exit_].name
                add_room = self.exits[exit_].add_room
                if add_room:
                    stri = "There is a passage to the %s Room. " % name
                else:
                    stri = "There is a passage to the %s. " % name
                text_block.append(stri)
        return pretty_print(text_block)

    # For now, only pass in 2 items, not 0, not 1, and not > 2
    def process_cmd(self, cmd_obj, player):

        verb = cmd_obj.verb
        verb_orig = cmd_obj.verb_orig
        noun = cmd_obj.noun
        noun_orig = cmd_obj.noun_orig
        target = cmd_obj.target
        target_orig = cmd_obj.target_orig
        full = cmd_obj.full
        stri = None
        return_pointer = self.name
        long_stri = ""

        if verb == "help":
            long_stri += pretty_response(["It is most helpful to construction sentences like this:"])
            long_stri += pretty_response(["verb noun"])
            long_stri += pretty_response(["Examples:"])
            long_stri += pretty_response(["go to the kitchen"])
            long_stri += pretty_response(["look at rick"])
            long_stri += pretty_response(["talk to rick"])
            stri3 = "Here are some verbs that may work:"
            verbs = ["look", "take", "go", "give", "help", "exit", "talk", "open", "inv"]
            for i in verbs:
                stri3 += " %s" % i
            long_stri += pretty_response([stri3])
            long_stri += pretty_response(["Try: exit - If you want to exit the game"])
        elif verb == "go":
            nounl = noun.lower()
            if nounl in self.exits:
                exit_ = self.exits[nounl]
                name = exit_.name
                add_room = exit_.add_room
                stri = "You move to the %s" % name
                if add_room:
                    stri += " Room"
                return_pointer = noun
            else:
                stri = "You can not go there! %s" % noun_orig
        elif verb == "inv":
            stri = player.inv()
        elif (verb == "look") or (verb == "open"):
            found = False
            if noun == "player":
                person = player
            else:
                person = self.people_here.get(noun)

            if person:
                long_stri += person.look()
                found = True
            if not person:
                item = self.find_item_in_items(noun)
                if not item:
                    item = self.find_item_on_person(noun)
                if not item:
                    item = player.find_item(noun)
                if item:
                    if (item.openable) and (verb == "open"):
                        stri2 = "You open the %s." % item.name
                        long_stri += pretty_response(stri2)
                    long_stri += item.look()
                    found = True

            if found == False:
                stri = "You see nothing special about the %s" % noun_orig
        elif verb == "talk":
            if noun == "player":
                person = player
            else:
                person = self.people_here.get(noun)
            if person:
                dialog = "What's up %s?" % noun_orig
                long_stri += person.talk(dialog)
            else:
                stri = "%s is not here to talk to!" % noun_orig
        elif verb == "take":
            item = self.find_item_here(noun)
            if item:
                if item.is_moveable():
                    if target:
                        # this is of the form take item from person/object
                        objec = self.find_item_in_items(target)
                        if objec:
                            if objec.is_container():
                                got_item = objec.take_item(noun)
                                if got_item:
                                    player.add_item(got_item)
                                    stri = "You take the %s from the %s" % (noun_orig, target_orig)
                                else:
                                    stri = "Failed to get item %s from the %s" % (item.name, target_orig)
                            else:
                                stri = "You can NOT take the %s from the %s" % (noun_orig, target_orig)
                        else:
                            person = self.people_here.get(target)
                            if person:
                                got_item = person.take_item(noun)
                                if got_item:
                                    player.add_item(got_item)
                                    stri = "You take the %s from %s" % (noun_orig, person.name)
                                else:
                                    stri = "Failed to get item %s from the %s" % (noun_orig, person.name)
                            else:
                                stri = "You can NOT take the %s from %s because %s is NOT here!" % (
                                noun_orig, target_orig, target_orig)
                    else:
                        item_container = self.find_item_container(noun)
                        if item_container:
                            got_item = item_container.take_item(noun)
                            player.add_item(got_item)
                            stri = "You take the %s" % got_item.name
                        else:
                            stri = "Failed to find container for %s" % noun_orig
                else:
                    stri = "You can NOT %s the %s!" % (verb_orig, noun_orig)
            else:
                stri = "You can NOT find the %s!" % noun_orig

        elif verb == "give":
            item = player.find_item(noun)
            if item:
                if target:
                    objec = self.find_item_here(target)
                    if objec:
                        if objec.is_container():
                            got_item = player.take_item(noun)
                            objec.add_item(got_item)
                            stri = "You put the %s into the %s" % (noun_orig, target_orig)
                        else:
                            stri = "You can NOT put the %s into the %s" % (noun_orig, target_orig)
                    else:
                        person = self.people_here.get(target)
                        if person:
                            got_item = player.take_item(noun)
                            person.add_item(got_item)
                            stri = "You give the %s to %s" % (noun_orig, person.name)
                        else:
                            stri = "You can NOT give the %s to %s because %s is NOT here!" % (
                            noun_orig, target_orig, target_orig)
                else:
                    got_item = player.take_item(noun)
                    self.add_item(got_item)
                    stri = "You drop the %s into this room" % got_item.name
            else:
                stri = "Did not find %s on yourself!" % noun_orig

        elif verb == "skip":
            pass
        elif verb == "error":
            stri = "DOES NOT COMPUTE! %s" % full
        elif verb == "exit":
            print_remap("Exiting Game! Thanks for playing!")
            exit(1)
        else:
            other_stri = "Should NOT GET HERE! : verb %s noun %s full %s" % (verb, noun, full)
            print_remap(other_stri)
            exit(1)

        if stri:
            long_stri += pretty_response(stri)
        self.response = long_stri
        return return_pointer


class RoomRoom(Room):
    add_room = True


#######################################################################
## Item Class and sub-classes
#######################################################################

class Item(object):
    name = "no name yet"
    description = "This Item is not yet configured.  Subclass it and implement."
    moveable = True
    container = False
    container_type = "On"
    single = True
    openable = False

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}

    def is_moveable(self):
        return self.moveable

    def is_container(self):
        return self.container

    def add_item(self, item):
        if (self.container):
            self.items_here[item.name.lower()] = item
        else:
            print("Tried to add item to a NON container: %s" % self.name)
            exit(1)

    def take_item(self, item_name):
        if (self.container):
            if item_name.lower() in self.items_here:
                item = self.items_here[item_name.lower()]
                del self.items_here[item_name.lower()]
                return item
            else:
                for x in self.items_here:
                    if self.items_here[x].is_container():
                        item = self.items_here[x].take_item(item)
                        if item:
                            return item
                return None
        else:
            return None

    def describe(self):
        stri = "%s " % self.description
        return stri

    def view(self):
        if self.single:
            stri = "You see a %s. " % self.name
        else:
            stri = "You see some %s. " % self.name
        return stri

    def look(self):
        text_block = []
        text_block.append(self.describe())
        if self.items_here:
            stri = "%s the %s you see " % (self.container_type, self.name)
            text_block.append(stri)
            item_list = []
            for item in self.items_here.values():
                stri = "%s" % item.name
                item_list.append(stri)
            text_block.append(pretty_list(item_list))
            text_block.append(".")
        return pretty_response(text_block)

    def find_item(self, item):
        item_found = self.items_here.get(item)
        if item_found:
            return item_found
        else:
            for x in self.items_here:
                if self.items_here[x].is_container():
                    item_found = self.items_here[x].find_item(item)
                    if item_found:
                        return item_found
            return None

    def find_item_container(self, item_name):
        if item_name in self.items_here:
            return self
        for item in self.items_here:
            if self.items_here[item].is_container():
                item_here = self.items_here[item].find_item_container(item_name)
                if item_here:
                    return item_here
        return None


class Workbench(Item):
    container_type = "On"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False
        self.container = True
        flies = Item("flies", "Just a couple of flies looking all dead.")
        flies.moveable = True
        flies.single = False
        self.add_item(flies)


class Refrigerator(Item):
    container_type = "Inside"
    openable = True

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False
        self.container = True
        oj = Item("Orange Juice", "Tropicana Grove Stand.  It looks opened.")
        oj.moveable = True
        self.add_item(oj)


class Couch(Item):
    container_type = "In"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False
        self.container = True
        coins = Item("Coin Collection", "Jerry's Starwars quarters. Mint condition.  Worth like, 2 cents.")
        coins.moveable = True
        self.add_item(coins)


class Tv(Item):

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False


class DTable(Item):
    container_type = "On"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False
        self.container = True


class Bed(Item):
    container_type = "Under"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False
        self.container = True


class BookShelf(Item):
    container_type = "On"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False
        self.container = True


class Desk(Item):
    container_type = "On"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False
        self.container = True


class Cabinets(Item):
    container_type = "In"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.moveable = False
        self.container = True


#######################################################################
## Person Class and children
#######################################################################

class Person(object):
    solved_item = False
    solved_text = "Class init error, need to define this for children of Person"

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items_here = {}
        self.last_rand = 0

    def add_item(self, item):
        self.items_here[item.name.lower()] = item

    def del_item(self, item):
        del self.items_here[item.name.lower()]

    def describe(self):
        stri = "%s " % self.description
        return stri

    def view(self):
        stri = "You see %s. " % self.name
        return stri

    def look(self):
        text_block = []
        text_block.append(self.describe())
        if self.items_here:
            stri = "%s has " % (self.name)
            text_block.append(stri)
            item_list = []
            for item in self.items_here.values():
                item_list.append(item.name)
            text_block.append(pretty_list(item_list))
            text_block.append(".")
        return pretty_response(text_block)

    def inv(self):
        text_block = []
        if self.items_here:
            stri = "%s has " % (self.name)
            text_block.append(stri)
            item_list = []
            for item in self.items_here.values():
                item_list.append(item.name)
            text_block.append(pretty_list(item_list))
            text_block.append(".")
        return pretty_response(text_block)

    def find_item(self, item):
        item_found = self.items_here.get(item)
        if item_found:
            return item_found
        else:
            for x in self.items_here:
                if self.items_here[x].is_container():
                    item_found = self.items_here[x].find_item(item)
                    if item_found:
                        return item_found
            return None

    def solved(self):
        if self.solved_item:
            if self.find_item(self.solved_item):
                return True
        else:
            return False

    def take_item(self, item_name):
        if item_name.lower() in self.items_here:
            item = self.items_here[item_name.lower()]
            del self.items_here[item_name.lower()]
            return item
        else:
            for x in self.items_here:
                if self.items_here[x].is_container():
                    item = self.items_here[x].take_item(item)
                    if item:
                        return item
            return None

    def talk(self, dialog):
        if self.solved():
            stri = self.solved_text
        else:
            this_rand = randint(0, len(self.random_dialog) - 1)
            while this_rand == self.last_rand:
                this_rand = randint(0, len(self.random_dialog) - 1)
            stri = self.random_dialog[this_rand]
            self.last_rand = this_rand
        return pretty_response(stri)


class Player(Person):
    solved_item = "laptop"

    random_dialog = ["I wonder what Jessica is wearing today?",
                     "You look really silly talk to yourself.",
                     "Did Rick destroy all of the pieces of Gwendolyn?",
                     "If I solve this, I'm totally asking Rick to take us back to Atlantis.",
                     ]


    def __init__(self, name, description):
        super(Player, self).__init__(name, description)
        self.solved_text = "For some reason, you feel more secure."



class Rick(Person):
    solved_item = "flask"

    random_dialog = ["Hey Morty, have you seen my flask laying around anywhere?",
                     "Grandpa needs to get his drink on, Morty!",
                     "Look you little shit, I'm pretty busy here trying to solve this riddle. Go be helpful!",
                     "Dude.  Enough with the trips to Atlantis.  She's not interested anymore!",
                     ]

    def __init__(self, name, description):
        super(Rick, self).__init__(name, description)
        pg = Item("Portal Gun", "Rick's shiny and clean portal gun.  Pulsing green.");
        pg.moveable = False
        self.add_item(pg)
        self.solved_text = "After getting my %s back. I'm feeling more like myself. " % self.solved_item
        self.solved_text += "The text is getting less texty.  Maybe you should find more stuff for people."


class Beth(Person):
    solved_item = "boxed wine"

    random_dialog = ["Morty, why are we now text based?",
                     "You know what would make this a better day?  Some text based boxed wine.  Do you have some?",
                     "I swear, if Jerry hid my wine again I am going to kick him in the nuts.",
                     "I washed your sheets and socks.  I also placed a new box of tissues by your bed.  Hint, hint.",
                     ]

    def __init__(self, name, description):
        super(Beth, self).__init__(name, description)
        self.solved_text = "After getting my %s back I think I'm going to relax with a drink " % self.solved_item
        self.solved_text += "and a bath."


class Summer(Person):
    solved_item = "pants"

    random_dialog = ["So, like Morty, have you seen a pair of whit'ish leggings laying around anywhere?",
                     "I totally need to stop drinking so much water before bed.",
                     "Dude.  Did you hear they are making a Ball Fondlers 8?  That is going to be dope.",
                     "Sometimes I wish we could go back to the Road Warrior rip-off dimension again.",
                     ]

    def __init__(self, name, description):
        super(Summer, self).__init__(name, description)
        self.solved_text = "Sweet.  Now I have my %s back.  Just ignore me while I do some laundry." % self.solved_item


class Jerry(Person):
    solved_item = "coin collection"

    random_dialog = ["Got apples?  Or maybe my coin collection?",
                     "I miss Doofus Rick.  I mean, super cool Rick.",
                     "Now, are you gonna keep hating this playa or are you gonna jack my steez?",
                     'Hey, uh, 1995 called! They want their "certain year called wanting its blank back" formula back!',
                     "My shirt's on backwards?  Of course I know my shirt's on backward.  I like it this way.  I'm not stupid!",
                     ]

    def __init__(self, name, description):
        super(Jerry, self).__init__(name, description)
        self.solved_text = "Look at my %s! They have little R2D2s where Lincon's head should be!" % self.solved_item


###############################################################################
## Engine Class
###############################################################################

class Engine(object):

    def __init__(self, start_room, text_decoder):
        self.start_room = start_room.lower()
        self.rooms = {}
        self.text_decoder = text_decoder
        self.response = "No response yet"
        self.current_room = 0
        self.room_name = self.start_room
        self.room_description = "No description for Garage yet"
        self.solved = False
        self.end = "No end text yet"
        self.player = Player("Morty", "This is Morty, the character you control.")
        self.characters = {self.player.name: self.player}

    def add_room(self, room):
        self.rooms[room.name.lower()] = room

    def next_room(self, room_name):
        return self.rooms.get(room_name.lower())

    def opening_room(self):
        return self.next_room(self.start_room)

    def check_solved(self):
        solved = True
        for x in self.characters.values():
            if not x.solved():
                solved = False

        self.solved = solved
        return solved

    def digest(self, command):
        # used by web based version
        # make changes based on command return self
        # update
        # response         -- this is first, response from command
        # room_name        -- string of the room name
        # room_description -- string from current_room.enter()
        # solved           -- set this if check_solvedsolved:
        items = self.current_room.items_here
        people = self.current_room.people_here
        exits = self.current_room.exits
        cmd_object = self.text_decoder.process_input(command, items, people, exits, self.player)
        next_room_name = self.current_room.process_cmd(cmd_object, self.player)
        self.response = self.current_room.response
        self.current_room = self.next_room(next_room_name)
        self.check_solved()
        self.room_name = self.current_room.name
        self.room_description = self.current_room.enter()

        return self

    def play(self):

        current_room = self.opening_room()

        while self.check_solved() == False:
            print("-" * 80)
            current_room.enter()
            print("")
            command = input("What do you do Morty? > ")
            print("-" * 80)
            items = current_room.items_here
            people = current_room.people_here
            exits = current_room.exits
            cmd_object = self.text_decoder.process_input(command, items, people, exits, self.player)
            next_room_name = current_room.process_cmd(cmd_object, self.player)
            current_room = self.next_room(next_room_name)

        print("        ___           ")
        print("    . -^   `--,       ")
        print("   /# =========`-_    ")
        print("  /# (--====___====\  ")
        print(" /#   .- --.  . --.|  ")
        print("/##   |  * ) (   * ), ")
        print("|##   \    /\ \   / | ")
        print("|###   ---   \ ---  | ")
        print("|####      ___)    #| ")
        print("|######           ##| ")
        print(" \##### ---------- /  ")
        print("  \####           (   ")
        print("   `\###          |   ")
        print("     \###         |   ")
        print("      \##        |    ")
        print("       \###.    .)    ")
        print("        `======/      ")


    def setup_game(self):
        # Setup the Rooms
        garage = Room("Garage", "Rick's Garage with all the wacky stuff in it.")
        kitchen = Room("Kitchen", "Here is the lovely galley kitchen.  With a nice little bar for breakfast.")
        living = RoomRoom("Living", "In this room we have the couch and TV.  Hopefully we get Interdimensional Cable.")
        dining = RoomRoom("Dining", "Here is where the family can enjoy a nice meal on the large table.")
        entry = Room("Entry", "This is the entry way to the Smith's house.")
        office = Room("Office", "This is Jerry's office room. With a Titanic poster on the wall.")
        stairs = Room("Stairs",
                      "These are the stairs that connect the Entry way with the second floor.  Family photos on the wall.")
        hallway = Room("Hallway", "This is the upstairs hallway.")
        mortys = RoomRoom("Mortys", "This is Morty's Room. The floor is sticky.")
        summers = RoomRoom("Summers",
                           "This is Summer's Room. The room is mostly pink with lots of pop star related posters on the wall.")

        # Setup items
        workbench = Workbench("Workbench", "Rick's Workbench is covered with a bunch of sci-fi gadgets.")
        refrigerator = Refrigerator("Refrigerator", "The Refrigerator is a Puke Yellow Whirlpool.")
        couch = Couch("Couch", "Ordinary family couch.  Looks comfortable.")
        tv = Tv("TV", "56 inch 4k, HDR with Interdimensional Cable hooked up!")
        d_table = DTable("Dining Table", "A nice long dining room table to eat on.")
        flask = Item("Flask", "Rick's shiny Silver Flask. Feels full.")
        pants = Item("Pants", "Summer's White Leggings. But they have a bit of a stain on them.")
        boxed_wine = Item("Boxed Wine", "This box of red wine seems pretty heavy.")
        laptop = Item("Laptop", "Oh yeah. Your precious laptop.  Clear that browser history!")
        j_computer = Item("Computer", "Jerry's desktop computer")
        j_desk = Desk("Desk", "Jerry's computer desk.")
        m_desk = Desk("Desk", "Morty's computer desk.")
        s_desk = Desk("Desk", "Summer's computer desk.")
        l_bookshelf = BookShelf("Bookshelf", "The family bookshelf with various books on it.")
        j_bookshelf = BookShelf("Bookshelf", "A bookshelf in Jerry's office, with advertisement related books.")
        s_bookshelf = BookShelf("Bookshelf", "Summer's bookshelf.  Filled with mostly magazines.")
        g_bookshelf = BookShelf("Garage Shelf", "Loaded with Rick's latest gadgets and experiments.")
        m_bed = Bed("Bed", "Morty's bed.")
        s_bed = Bed("Bed", "Summer's bed.")
        cabinets = Cabinets("Kitchen Cabinets", "Just normal Kitchen Cabinets.")
        cabinets.single = False
        old_yeller = Item("Old Yeller", "A copy of the classic, Old Yeller.")
        watership = Item("Watership Down", "A copy of the classic, Watership Down.")
        cosmo = Item("Cosmopoliton magazine", "The April issue of Cosmo.  18 ways to tell if he wants you.")
        canned_fruit = Item("Canned Fruit", "A old can of mixed fruit.")
        gum = Item("Gum", "Pack of Double Bubble Gum.  Half empty.")
        cables = Item("Cables", "A bunch of random A/V cables.")
        cables.single = False
        water_bottle = Item("Water Bottle", "A red insulated water bottle.  Still cold.")
        l_bookshelf.add_item(old_yeller)
        j_bookshelf.add_item(watership)
        s_bookshelf.add_item(cosmo)
        cabinets.add_item(canned_fruit)
        couch.add_item(gum)
        j_desk.add_item(j_computer)
        j_desk.add_item(cables)
        s_desk.add_item(water_bottle)
        m_desk.add_item(flask)
        s_bed.add_item(boxed_wine)

        # Setup people
        rick = Rick("Rick", "Rick looks drunk with vomit on his lab coat.")
        beth = Beth("Beth", "Beth looks a little dazed and is searching for something.")
        jerry = Jerry("Jerry", "Jerry looks like a dip-shit as usual.")
        summer = Summer("Summer", "Summer looks vexed.  Damn it Morty, that is your sister, stop staring!")

        # Populate Rooms
        garage.add_item(workbench)
        garage.add_item(g_bookshelf)
        garage.add_person(rick)
        garage.add_exit(kitchen)
        kitchen.add_item(refrigerator)
        kitchen.add_item(cabinets)
        kitchen.add_person(beth)
        kitchen.add_exit(garage)
        kitchen.add_exit(dining)
        kitchen.add_exit(living)
        living.add_item(couch)
        living.add_item(tv)
        living.add_item(l_bookshelf)
        living.add_person(summer)
        living.add_exit(kitchen)
        living.add_exit(entry)
        dining.add_item(d_table)
        dining.add_exit(kitchen)
        dining.add_exit(entry)
        entry.add_exit(stairs)
        entry.add_exit(living)
        entry.add_exit(dining)
        stairs.add_exit(entry)
        stairs.add_exit(hallway)
        stairs.add_item(pants)
        hallway.add_exit(stairs)
        hallway.add_exit(office)
        hallway.add_exit(mortys)
        hallway.add_exit(summers)
        office.add_exit(hallway)
        office.add_person(jerry)
        office.add_item(laptop)
        office.add_item(j_bookshelf)
        office.add_item(j_desk)
        mortys.add_exit(hallway)
        mortys.add_item(m_desk)
        mortys.add_item(m_bed)
        summers.add_exit(hallway)
        summers.add_item(s_bookshelf)
        summers.add_item(s_bed)
        summers.add_item(s_desk)

        self.add_room(garage)
        self.add_room(kitchen)
        self.add_room(living)
        self.add_room(dining)
        self.add_room(entry)
        self.add_room(stairs)
        self.add_room(hallway)
        self.add_room(office)
        self.add_room(summers)
        self.add_room(mortys)

        # These are used to solve the game
        self.characters[rick.name] = rick
        self.characters[beth.name] = beth
        self.characters[jerry.name] = jerry
        self.characters[summer.name] = summer


        self.response = pretty_print([
            "You find yourself in Rick's Garage with him yelling at you. ",
            "Oh shit Morty! It looks like we got stuck in a text based game. This is not <burp> good! ",
            "We have to find a way out. I'll study the data and see if I can solve this riddle. ",
            "You run around and see what you can figure out. We seem to be in the garage. But I feel ",
            "off. I think I need a drink.  <Rick searches his lab coat>  Oh no Morty, this is worse than I ",
            "thought! I've lost my damn flask!",
        ])
        self.current_room = self.opening_room()
        self.room_name = self.current_room.name
        self.room_description = self.current_room.enter()

        self.end = pretty_print([
            "Rick appears in the room you are currently in! ",
            "You did it Morty. You solved the text based puzzle. ",
            "Who would have thought you just had to give people random shit they wanted. ",
            "What a thinker!  I guess we can take a trip to Atlantis again! ",
            "You earned it! ",
            "<Rick opens up a portal and you both step inside> ",
            "<Theme music plays> ",
        ])



#######################################################################
## TextDecode Class - attempts to decode the command prompt response
#######################################################################

class TextDecode(object):
    # This should be an interesting class
    # Could be a def as well, really
    # the point of this is to take a text input and pass
    # back a response, but can also do work from here

    text_remap = {
        "look": "look",
        "inspect": "look",
        "view": "look",
        "examine": "look",
        "investigate": "look",
        "read": "look",
        "take": "take",
        "grab": "take",
        "pick": "take",
        "get": "take",
        "talk": "talk",
        "speak": "talk",
        "move": "go",  # move item or move to a place?
        "go": "go",
        "travel": "go",
        "walk": "go",
        "run": "go",
        "give": "give",
        "place": "give",
        "drop": "give",
        "put": "give",
        "help": "help",
        "inventory": "inv"
    }

    player_remap = {
        "player": "player",
        "me":     "player",
        "myself": "player",
        "self": "player",
        "morty":  "player",
        "i":      "player",
    }

    remap_empty = ['.', '!', ',', '?']
    middle_words_skip = ['at', 'the', 'to', 'in', 'on', 'room', 'inside', 'up']
    verbs = ["look", "take", "go", "give", "help", "exit", "talk", "open", "inv"]

    # what about like "give the flask to rick"  verb noun target
    # or "take the bottle from the fridge" verb noun target
    # look works on items and people
    # take can have 1 noun or 2, take the bottle from the fridge  or take the bottle from rick
    # targets can be people or item(containers)
    # give is like take but opposite flow direction
    # go only has 1 noun, a room, some place will need to verify legal moves

    def __init__(self):
        pass

    def search_item(self, item, compare):
        if item.items_here:
            item_found = item.items_here.get(compare)
            if item_found:
                return item_found
            else:
                for x in item.items_here:  # X here has orange juice as a name.. hum, what, shouldn't it be ref
                    if item.items_here[x].is_container():
                        item_found = self.search_item(item.items_here[x], compare)
                        if item_found:
                            return item_found
                return None
        else:
            return None

    def search_items(self, items, compare):
        item_found = items.get(compare)
        if item_found:
            return item_found
        else:
            for x in items:
                if items[x].is_container():
                    item_found = self.search_item(items[x], compare)
                    if item_found:
                        return item_found
            return None

    def search_people(self, people, compare):
        for x in people:
            item_found = people[x].find_item(compare)
            if item_found:
                return item_found
        return None

    def process_input(self, cmd_string, items, people, exits, player):
        debug_text = True
        verb = None
        verb_orig = None
        noun = None
        noun_orig = None
        noun_is_person = False
        target = None
        target_orig = None
        full = cmd_string
        error_msg = None
        print_list = []
        saved_last_x = None
        saved_last_x_orig = None

        for x in self.remap_empty:
            cmd_string = cmd_string.replace(x, '')

        # Now split the string
        cmd_list = cmd_string.split()
        for x in cmd_list:
            orig = x
            x = x.lower()
            found = False
            if self.text_remap.get(x):
                x = self.text_remap.get(x)
            if self.player_remap.get(x):
                x = self.player_remap.get(x)

            if not verb:
                # check for a verb
                for y in self.verbs:
                    if y == x:
                        if verb:
                            error_msg = "Error: TextDecode found 2 verbs %s and %s " % (orig, verb)
                        else:
                            verb = x
                            verb_orig = orig
                            found = True
                        break

            if not found:

                people_name = None
                for j in people:
                    people_name_lower = people[j].name.lower()
                    if people_name_lower == x:
                        people_name = people[j]

                if x == "player":
                    people_name = x

                if people_name:
                    if noun:
                        if (verb == "take") or (verb == "give"):
                            target = x
                            target_orig = orig
                            found = True
                        else:
                            error_msg = "Error: TextDecode found 2 nouns %s and %s " % (orig, noun)
                    else:
                        noun = x
                        noun_orig = orig
                        noun_is_person = True
                        found = True

            if not found:
                z = x
                item_name = self.search_items(items, x)  # searches for item in normal room item list
                if not item_name:
                    item_name = self.search_people(people, x)  # searches for item on people in the room
                if not item_name:
                    item_name = player.find_item(x)
                if not item_name and saved_last_x:
                    y = "%s %s" % (saved_last_x, x)  # make search name longer from previous saved_last
                    z = y
                    orig = "%s %s" % (saved_last_x_orig, orig)
                    item_name = self.search_items(items, y)
                    if not item_name:
                        item_name = self.search_people(people, y)
                    if not item_name:
                        item_name = player.find_item(y)

                if item_name:
                    if noun:
                        if (verb == "take") or (verb == "give"):
                            if noun_is_person:
                                target = noun
                                target_orig = noun_orig
                                noun = z
                                noun_orig = orig
                            else:
                                target = z
                                target_orig = orig
                            found = True
                        else:
                            error_msg = "Error: TextDecode found 2 nouns %s and %s " % (orig, noun)
                    else:
                        noun = z
                        noun_orig = orig
                        found = True

            if not found:
                if verb == "go":
                    if x in exits:
                        if noun:
                            error_msg = "Error: TextDecode found 2 nouns %s and %s " % (orig, noun)
                        else:
                            noun = orig
                            noun_orig = orig
                            found = True

            if not found:
                for y in self.middle_words_skip:
                    if y == x:
                        x = None
                        found = True
                        break

            if not found:
                error_msg = "Error: TextDecode could not decode %s " % orig
                if saved_last_x:
                    saved_last_x = z
                    saved_last_x_orig = orig
                else:
                    saved_last_x = x
                    saved_last_x_orig = orig
            else:
                saved_last_x = None

            if error_msg:
                print_list.append(error_msg)

        if verb:
            if verb == "exit":
                noun = "skip"
            elif verb == "help":
                noun = "skip"
            elif verb == "inv":
                noun = "player"
            elif not noun:
                if saved_last_x:
                    noun = saved_last_x
                    noun_orig = saved_last_x_orig
                else:
                    error_msg = "Error: TextDecode %s with no noun %s " % (verb, full)
                    print_list.append(error_msg)
                    verb = "error"
        else:
            error_msg = "Error: TextDecode no verb found in %s " % full
            print_list.append(error_msg)
            verb = "error"

        if print_list:
            if debug_text and False:
                pretty_response(print_list)
                verb = "error"

        return Command(verb, verb_orig, noun, noun_orig, target, target_orig, full)



#######################################################################
## Main - add the objects and start the engine
#######################################################################

start_room = 'Garage'
a_text_decoder = TextDecode()
a_game = Engine(start_room, a_text_decoder)
a_game.setup_game()
#a_game.play()

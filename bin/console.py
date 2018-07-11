from rmgame import game_class

def print_remap(stri):
    print(stri.rstrip())


engine = game_class.a_game

stri_line = "-" * 80
size_string = "<------------------- MAKE YOUR TERMINAL THIS WIDE OR LARGER ------------------->"
print_remap(size_string)

print_remap(engine.response)
print_remap(stri_line)

while not engine.solved:
    room_title = "%s:" % engine.room_name
    print_remap(room_title)
    print_remap(engine.room_description)
    print_remap(stri_line)
    command = input("What do you do Morty? > ")
    engine.digest(command)
    print_remap(stri_line)
    print_remap(engine.response)
    print_remap(stri_line)


print_remap(engine.end)




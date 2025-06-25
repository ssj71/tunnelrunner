#!/usr/bin/env python3

#spencer and AI

#an ascii terminal game for 80x24

import time, math as m, random
from pynput import keyboard

##CONFIGURATION
REFRESHRATE_HZ = 60
NROWS = 24
NCOLS = 80
WALL = "#"

#vars
running = True #flag for quitting time
thescreen = bytearray(" ", "utf8") * (NROWS) * (NCOLS+1)
you = [12.0, 0.0] #row, col
yourvel = [0.0, 5.0] #row per sec, col per sec
camera = 0 #row offset
cavefloor = [1] * (NCOLS+1) #row change per col
caveceil = [NROWS-1] * (NCOLS+1) #row change per col
caveindex = 0 #this is the index of the oldest column that isn't shown

for i in range(NROWS-1):
    thescreen[(NCOLS+1)*(i+1)] = ord("\n")

def rowcol(r,c):
    #we have a newline as the 81st char in each row
    return (NROWS-r)*(NCOLS+1)+c

def hud():
    pass


def paint(r, c, s):
    print(f"\033[{NROWS-r};{c+1}H{s}", end="")

def paintcol(rstart, rend, c, s):
    for r in range(min(max(rstart,1),NROWS-1), min(max(rend,1),NROWS-1)):
        paint(r, c, s)

def firstcave():
    print("\033[H\033[2J", WALL*NCOLS, "\n" * (NROWS-2), WALL*NCOLS, sep="", end="", flush=True)

def cavify(advance, camerachange):
    for _ in range(advance):
        #generate the next cave section
        global caveindex, cavefloor, caveceil
        lastnew = (caveindex - 2) % (NCOLS + 1)
        newfloor = cavefloor[lastnew] + random.randint(-3, 3)
        newceil = caveceil[lastnew] + random.randint(-3, 3)
        new = (caveindex - 1) % (NCOLS + 1)
        cavefloor[new] = newfloor
        caveceil[new] = newceil
        #TODO: camera movement
        #TODO: probabilities
        for j in range(NCOLS): 
            #print each column starting with the oldest
            prev = (caveindex + j) % (NCOLS + 1)
            i = (caveindex + j + 1) % (NCOLS + 1)
            if caveceil[prev] > caveceil[i]:
                paintcol(caveceil[i], caveceil[prev], j, WALL)
            elif caveceil[prev] < caveceil[i]:
                #print walls
                paintcol(caveceil[prev], caveceil[i], j,  " ")
                pass
            #else don't print anything
            if cavefloor[prev] < cavefloor[i]:
                paintcol(cavefloor[prev], cavefloor[i]+1, j, WALL)
                pass
            elif cavefloor[prev] > cavefloor[i]:
                paintcol(cavefloor[i]+1, cavefloor[prev]+1, j, " ")
                pass
            #else don't print anything
        caveindex = (caveindex + 1) % (NCOLS + 1)
    print("", sep="", end="", flush=True)

def render():
    #print("\033[H\033[2J", thescreen.decode("utf8"), sep="", end="", flush=True)
    #cavify():
    pass

def updatestuff(dt):
    #thescreen[rowcol(m.floor(you[0]), m.floor(you[1]))] = ord(" ")
    #you[0] += yourvel[0] * dt
    #thescreen[rowcol(m.floor(you[0]), m.floor(you[1]))] = ord(">")
    you[1] += yourvel[1] * dt
    cavify(m.floor(you[1]), 0)
    you[1] %= 1.0
    pass

def on_press(key):
    """
    Function to handle key press events.
    """
    global running # Declare 'running' as global to modify it

    try:
        # Check for alphanumeric keys (wasd, space)
        if key.char:
            key_char = key.char.lower() # Convert to lowercase for case-insensitivity
            if key_char == 'w':
                print("\nW (Move Up)") # Added \n for cleaner output with period
            elif key_char == 'a':
                print("\nA (Move Left)")
            elif key_char == 's':
                print("\nS (Move Down)")
            elif key_char == 'd':
                print("\nD (Move Right)")
            elif key_char == ' ':
                print("\nSpace (Jump/Action)")
            elif key_char == 'q':
                print("\nQ pressed. Exiting.")
                running = False # Set flag to False to stop the main loop
                return False # Stop the keyboard listener
    except AttributeError:
        # Handle special keys (arrow keys, escape)
        if key == keyboard.Key.up:
            print("\nUp Arrow (Move Up)")
            yourvel[0] += 1
        elif key == keyboard.Key.down:
            print("\nDown Arrow (Move Down)")
            yourvel[0] -= 1
        elif key == keyboard.Key.left:
            print("\nLeft Arrow (Move Left)")
            yourvel[1] -= 1
        elif key == keyboard.Key.right:
            print("\nRight Arrow (Move Right)")
            yourvel[1] += 1
        elif key == keyboard.Key.esc:
            print("\nEscape pressed. Exiting.")
            running = False # Set flag to False to stop the main loop
            return False # Stop the keyboard listener

def on_release(key):
    """
    Function to handle key release events (optional).
    """
    pass

# --- Main Script Execution ---
print("Listening for WASD, Space, Arrow keys. Press 'q' or 'Escape' to exit.")

# Start the keyboard listener in a non-blocking way
# This allows the main thread to continue execution
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start() # Start the listener thread

# Main loop that prints a period every second
lasttime = time.time()
firstcave()
while running:
    now = time.time()
    updatestuff(now - lasttime)
    render()
    lasttime = now
    time.sleep(1/REFRESHRATE_HZ)

# Once 'running' becomes False (due to 'q' or 'esc' press),
# the loop exits, and we wait for the listener thread to finish.
listener.join() # Wait for the listener thread to fully stop

print("\nScript exited.") # Newline for cleaner exit message

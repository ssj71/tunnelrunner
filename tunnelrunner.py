#!/usr/bin/env python3
#spencer

#an ascii terminal game for 80x24

import time, math as m, random
from pynput import keyboard

##CONFIGURATION
REFRESHRATE_HZ = 60
NROWS = 24
NCOLS = 80
WALL = "#"
PLAYERCOL = 2

SPIKINESS = 0
TWISTINESS = 1

##vars
running = True #flag for quitting time
you = [12.0, 0.0] #row, col
yourvel = [0.0, 5.0] #row per sec, col per sec
distance = 0 #score
fuel = 4
camera = 0 #row offset
#cave stuff
cavefloor = [1] * (NCOLS+1) #row change per col
caveceil = [NROWS-1] * (NCOLS+1) #row change per col
caveindex = 0 #this is the index of the oldest column that isn't shown
middle = NROWS // 2 #this creates the optimal trajectory
headroom = NROWS // 2 - 2 #this determines how tight the cave currently is

def paint(r, c, s):
    print(f"\033[{NROWS-r};{c+1}H{s}", end="")

def paintif(r, c, s):
    if r and r < NROWS and c and c < NCOLS:
        paint(r, c, s)

#paint upwards along a column
def paintcol(rstart, rend, c, s):
    for r in range(min(max(rstart,1),NROWS-1), min(max(rend,1),NROWS)):
        paint(r, c, s)

def hud(distance, fuel):
    paint(0, 0, f"DIST:{distance:>14}")
    fuelstring = "$" * m.ceil(fuel)
    paint(0, NCOLS//2, f"FUEL:{fuelstring:>14}")
    pass

def player(dt):
    r0 = round(you[0])
    you[0] += yourvel[0] * dt
    you[1] += yourvel[1] * dt
    r1 = round(you[0])
    return r1-r0


def firstcave():
    print("\033[H\033[2J", WALL*NCOLS, "\n" * (NROWS-2), WALL*NCOLS, sep="", end="", flush=True)

def cavify(advance, camerachange):
    for _ in range(advance):
        #generate the next cave section
        global camera, caveindex, cavefloor, caveceil, headroom, middle
        caveindex = (caveindex + 1) % (NCOLS + 1)
        lastnew = (caveindex - 2) % (NCOLS + 1)
        #probabilities
        middle += random.randint(-1,1)


        targetheadroom = NROWS // 4
        err = targetheadroom - headroom
        var = round(TWISTINESS)
        if headroom < 3:
            headroom += random.randint(0,var)
        elif err > 0:
            headroom += random.randint(-var,0) + max(random.randint(0, var), random.randint(0, var))
        elif err < 0:
            headroom += min(random.randint(-var, 0), random.randint(-var,0)) + random.randint(0,var)
        else:
            headroom += random.randint(-var, 0) + random.randint(0,var)

        var = round(SPIKINESS)
        newfloor = middle - headroom - min(random.randint(0, var), random.randint(0, var))
        newceil = middle + headroom + min(random.randint(0, var), random.randint(0, var))

        newindex = (caveindex - 1) % (NCOLS + 1)
        cavefloor[newindex] = newfloor
        caveceil[newindex] = newceil

        #render
        for j in range(NCOLS): 
            #print each column starting with the oldest
            prev = (caveindex + j) % (NCOLS + 1)
            i = (caveindex + j + advance) % (NCOLS + 1)
            #ceiling
            if caveceil[prev] > caveceil[i] - camerachange and caveceil[i] - camera < NROWS:
                paintcol(caveceil[i] - camera, caveceil[prev] - camera + camerachange, j, WALL)
            elif caveceil[prev] < caveceil[i] - camerachange:
                paintcol(caveceil[prev] - camera + camerachange, caveceil[i] - camera, j,  " ")
            else:
                pass
            #floor
            if cavefloor[prev] < cavefloor[i] - camerachange:
                paintcol(cavefloor[prev] - camera + camerachange, cavefloor[i] - camera + 1, j, WALL)
            elif cavefloor[prev] > cavefloor[i] - camerachange: #camerachange = +1
                paintcol(cavefloor[i] - camera + 1, cavefloor[prev] - camera + camerachange + 1, j, " ")
            else:
                pass

    if not advance and camerachange > 0:
        for j in range(NCOLS):
            i = (caveindex + j + 1) % (NCOLS + 1)
            paintif(caveceil[i] - camera, j, WALL)
            paintif(cavefloor[i] - camera + camerachange, j, " ")
    elif not advance and camerachange < 0:
        for j in range(NCOLS):
            i = (caveindex + j + 1) % (NCOLS + 1)
            paintif(caveceil[i] - camera + camerachange , j, " ")
            paintif(cavefloor[i] - camera, j, WALL)
    print("", sep="", end="", flush=True)

def movecamera(you, camera):
    edge = 3
    if round(you[0] - camera) > NROWS - edge:
        return 1
    elif round(you[0] - camera) < edge:
        return -1
    else:
        return 0

def updatestuff(dt):
    global camera, distance
    distance += yourvel[1] * dt
    vert = player(dt)
    advance = m.floor(you[1])
    camerachange = 0
    if vert != 0:
        paint(round(you[0] - camera - vert), PLAYERCOL, " ")
        camerachange = movecamera(you, camera)
        camera += camerachange
    cavify(advance, camerachange)
    you[1] %= 1.0
    if vert:
        paint(round(you[0] - camera), PLAYERCOL, ">")
    hud(int(distance//5), fuel)

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
                yourvel[0] += 1
            elif key_char == 'a':
                print("\nA (Move Left)")
                yourvel[1] += -1
            elif key_char == 's':
                print("\nS (Move Down)")
                yourvel[0] += -1
            elif key_char == 'd':
                print("\nD (Move Right)")
                yourvel[1] += 1
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
paint(round(you[0] - camera), PLAYERCOL, ">")
while running:
    now = time.time()
    updatestuff(now - lasttime)
    lasttime = now
    time.sleep(1/REFRESHRATE_HZ)

# Once 'running' becomes False (due to 'q' or 'esc' press),
# the loop exits, and we wait for the listener thread to finish.
listener.join() # Wait for the listener thread to fully stop

print("\nScript exited.") # Newline for cleaner exit message

# DoodleJump-NEAT-AI
This project implements the NEAT (Neuroevolution of Augmenting Topologies) algorithm in the game DoodleJump.

# Dependencies
- pygame
- NEAT-Python
    - NOTE: Be aware of "pip install neat". "neat" module is different from the neat-python module. Thus, to install neat-python, please use "pip install neat-python".

# 3 important files we want you to know before you run
1. random_doodler.py: this file contains 50 randomly-controlled doodler. This is not part of the NEAT algorithm. However, it is a good control group to see if the NEAT algorithm improves its ability to play Doodle Jump.
2. neat_doodler_5_inputs.py: this file implemented input option 2 mentioned in the paper we attached to this project.
3. neat_doodler_17_inputs.py: this file implemetned input option 3 mentioned in our paper.

# How to run this project
1. Download all dependencies
2. Run the corresponding python file.
3. Watch as the neural network learns to beat DoodleJump

# TODO:

[-] Make sure that the doodler always has a platform that is reachable
[x] make the gravity and bounce scale correctly so that the game gets more difficult
[x] make sure that the doodler's sideswitching doesn't affect the collision detection
[x] make the doodler be able to switch sides of the screen from the edge
[x] create a losing screen
[x] animate legs to jump
[x] make it so that when the doodler changes the way it's facing it looks nicer
[x] change is_view_of function to work preoperly
[x] change line calcuations to be at the center of the platforms and doodlers
[x] go through NEAT branch and make sure it matches master branch
[x] make sure that doodlers aren't able to accelerate like crazy
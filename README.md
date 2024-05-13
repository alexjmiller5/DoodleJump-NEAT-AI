# DoodleJump-NEAT-AI

This repo is an AI which utilizes NEAT (Neuroevolution of Augmenting Topologies) algorithm to train and play the popular game DoodleJump.

In this repo, we built the Doodler Game from the ground up using Pygame. In addition, we also documented the process of training the AI with 3 different versions of inputs for the doodler AI.


# How to run this project
1. Download dependencies: ```pip install pygame neat-python```
3. Run the corresponding python file to see the training yourself. There are 3 options in this repo:
    1. `random_doodler.py`: This version contains 50 randomly-controlled doodler. It serves as a good control envrionment to see if the NEAT algorithm improves its ability to play Doodle Jump.
    2. `neat_doodler_5_inputs.py`: This version trains the doodler with 5 inputs: doodler's velocity in y direction, x-distances and y-distances between the doodler and the closest platform above and the distances between it and the closest platform below. This is the option 2 descripted in the paper that goes alone with this repo.
    3. `neat_doodler_17_inputs.py`: This version trains the doodler with 17 inputs: x-distances and y-distances between the doodler and the closest platform from 8 different directions (up, down, left, right, and 4 diagonal directions) and whether the doodler is moving up or down (the y-velocity of the doodler). This corresponds to option 3 in the paper.
3. Watch as the neural network learns to beat DoodleJump

# Some YouTube Demos for the traning:
If you are too lazy to run the code above, here's some pretrained video for our demo purposes:
* For 5-input: https://youtu.be/TbiUGNLxEMQ
* For 17-input: https://youtu.be/CsDxCkCBqnc

# Paper that goes with this project
[DoodleJump-NEAT-AI And A Comparative Analysis on the Importance of Inputs and Reward System](https://docs.google.com/document/d/1TV9vBYJhPeZkpovewtvGCP9XhaJxFoFu_eLgzjcz0Vw/edit?usp=sharing)

# Original NEAT paper:
[Efficient Evolution of Neural Network Topologies](https://nn.cs.utexas.edu/downloads/papers/stanley.cec02.pdf)

# TODO:

- [x] Make sure that the doodler always has a platform that is reachable
- [x] make the gravity and bounce scale correctly so that the game gets more difficult
- [x] make sure that the doodler's sideswitching doesn't affect the collision detection
- [x] make the doodler be able to switch sides of the screen from the edge
- [x] create a losing screen
- [x] animate legs to jump
- [x] make it so that when the doodler changes the way it's facing it looks nicer
- [x] change is_view_of function to work preoperly
- [x] change line calcuations to be at the center of the platforms and doodlers
- [x] go through NEAT branch and make sure it matches master branch
- [x] make sure that doodlers aren't able to accelerate like crazy

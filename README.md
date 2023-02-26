# hitman-neat
Using the NEAT and Pygame library in Python to train a hitman in a two-player shooter game.

# training method
Similar to TechWithTim's training method for his two player pong game, where each member in a population 'battles' against each other, adjusting fitnesses for each accordingly. 

# pickle files
All the "hitman#.pickle" files are the different genomes I tested with. The best hitman was the "V2" one.

# usage
To train the population, uncomment "train_ai" at the bottom of the "main.py" file (the 'FPS' variable should be around 500 for fast training)
To test the population against yourself, uncomment "test_ai" at the bottom of the same file (adjust 'FPS' varible to around 120)
To train the population against the best genome (which I put as V2), uncomment "special_training" at the bottom of the same file

# Hitman V2 neural network
![Alt text](C:/Users/ahiya/PYTHON%20PROJECTS/PycharmProjects/NEAThitman/Digraph.gv.svg)

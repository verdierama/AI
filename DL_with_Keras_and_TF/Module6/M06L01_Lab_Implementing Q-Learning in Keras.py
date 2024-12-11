#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo"  />
#     </a>
# </p>
# 

# # **Lab: Implementing Q-Learning in Keras**
# 

# Estimated time needed: **30** minutes
# 

# ## Lab Overview 
# In this lab, you will implement a Q-Learning algorithm using Keras to solve a reinforcement learning problem.
# 
# ## Learning objectives:
# By the end of this lab, you will:  
# - Implement a Q-Learning algorithm using Keras
# - Define and train a neural network to approximate the Q-values
# - Evaluate the performance of the trained Q-Learning agent
# 
# ## Prerequisites 
# - Basic knowledge of Python programming
# - Familiarity with Keras and neural networks
# - Understanding of reinforcement learning concepts
# 

# ### Step-by-Step Guide 
# 
# #### Step 1: Setting Up the Environment 
# 
# First, you will set up the environment using the OpenAI Gym library. You will use the 'CartPole-v1' environment, a common benchmark for reinforcement learning algorithms.
# 

# In[1]:


#get_ipython().run_line_magic('pip', 'install gym')


# In[3]:


#get_ipython().system('pip install --upgrade numpy==1.26.4')
#get_ipython().system('pip uninstall tensorflow -y')
#get_ipython().system('pip install tensorflow==2.16.2')


# ### Set Environment Variables 
# Sometimes, environment variables can help mitigate certain issues with TensorFlow. You can try disabling the oneDNN optimizations or CUDA.
# 

# In[4]:


import os 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' 
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 


# ### Reduce Recursion Limit 
# You can also try increasing the recursion limit, although this is generally more of a workaround than a solution.
# 

# In[5]:


import sys 
sys.setrecursionlimit(1500) 

import gym 
import numpy as np 

# Create the environment 
env = gym.make('CartPole-v1') 

# Set random seed for reproducibility 
np.random.seed(42) 
env.action_space.seed(42) 
env.observation_space.seed(42)


# #### Explanation:  
# - `gym` is a toolkit for developing and comparing reinforcement learning algorithms.
# - `CartPole-v1` is an environment where a pole is balanced on a cart, and the goal is to prevent the pole from falling over.
# - Setting random seeds ensures that you can reproduce the results.
# 

# ### Step 2: Define the Q-Learning Model 
# 
# You will define a neural network using Keras to approximate the Q-values. The network will take the state as input and output Q-values for each action.
# 

# In[6]:


# Suppress warnings for a cleaner notebook or console experience
import warnings
warnings.filterwarnings('ignore')

# Override the default warning function
def warn(*args, **kwargs):
    pass
warnings.warn = warn

# Import necessary libraries for the Q-Learning model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input  # Import Input layer
from tensorflow.keras.optimizers import Adam
import gym  # Ensure the environment library is available

# Define the model building function
def build_model(state_size, action_size): 
    model = Sequential() 
    model.add(Input(shape=(state_size,)))  # Use Input layer to specify the input shape 
    model.add(Dense(24, activation='relu')) 
    model.add(Dense(24, activation='relu')) 
    model.add(Dense(action_size, activation='linear')) 
    model.compile(loss='mse', optimizer=Adam(learning_rate=0.001)) 
    return model 

# Create the environment and set up the model
env = gym.make('CartPole-v1')
state_size = env.observation_space.shape[0] 
action_size = env.action_space.n 
model = build_model(state_size, action_size)


# #### Explanation: 
# - `Sequential` model: a linear stack of layers in Keras. 
# - `Dense` layers: fully connected layers. 
# - `input_dim`: the size of the input layer, corresponding to the state size. 
# - `activation='relu'`: Rectified Linear Unit activation function. 
# - `activation='linear'`: linear activation function for the output layer, as we are predicting continuous Q-values. 
# - `Adam` optimizer: an optimization algorithm that adjusts the learning rate based on gradients. 
# 

# #### Step 3: Implement the Q-Learning Algorithm 
# 
# Now, you will implement the Q-Learning algorithm, which involves interacting with the environment, updating the Q-values, and training the neural network. 
# 
# **Define the replay Function**
# 

# In[7]:


import random
import numpy as np
from collections import deque
import tensorflow as tf

# Define epsilon and epsilon_decay
epsilon = 1.0  # Starting with a high exploration rate
epsilon_min = 0.01  # Minimum exploration rate
epsilon_decay = 0.99  # Faster decay rate for epsilon after each episode

# Replay memory
memory = deque(maxlen=2000)

def remember(state, action, reward, next_state, done):
    """Store experience in memory."""
    memory.append((state, action, reward, next_state, done))

def replay(batch_size=64):  # Increased batch size
    """Train the model using a random sample of experiences from memory."""
    if len(memory) < batch_size:
        return  # Skip replay if there's not enough experience

    minibatch = random.sample(memory, batch_size)  # Sample a random batch from memory
    
    # Extract information for batch processing
    states = np.vstack([x[0] for x in minibatch])
    actions = np.array([x[1] for x in minibatch])
    rewards = np.array([x[2] for x in minibatch])
    next_states = np.vstack([x[3] for x in minibatch])
    dones = np.array([x[4] for x in minibatch])
    
    # Predict Q-values for the next states in batch
    q_next = model.predict(next_states)
    # Predict Q-values for the current states in batch
    q_target = model.predict(states)
    
    # Vectorized update of target values
    for i in range(batch_size):
        target = rewards[i]
        if not dones[i]:
            target += 0.95 * np.amax(q_next[i])  # Update Q value with the discounted future reward
        q_target[i][actions[i]] = target  # Update only the taken action's Q value
    
    # Train the model with the updated targets in batch
    model.fit(states, q_target, epochs=1, verbose=0)  # Train in batch mode

    # Reduce exploration rate (epsilon) after each training step
    global epsilon
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

def act(state):
    """Choose an action based on the current state and exploration rate."""
    if np.random.rand() <= epsilon:
        return random.randrange(action_size)  # Explore: choose a random action
    act_values = model.predict(state)  # Exploit: predict action based on the state
    return np.argmax(act_values[0])  # Return the action with the highest Q-value

# Define the number of episodes you want to train the model for
episodes = 10  # You can set this to any number you prefer
train_frequency = 5  # Train the model every 5 steps

for e in range(episodes):
    state, _ = env.reset()  # Unpack the tuple returned by env.reset()
    state = np.reshape(state, [1, state_size])
    for time in range(200):  # Limit to 200 time steps per episode
        action = act(state)
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        reward = reward if not done else -10
        next_state = np.reshape(next_state, [1, state_size])
        remember(state, action, reward, next_state, done)  # Store experience
        state = next_state
        
        if done:
            print(f"episode: {e+1}/{episodes}, score: {time}, e: {epsilon:.2}")
            break
        
        # Train the model every 'train_frequency' steps
        if time % train_frequency == 0:
            replay(batch_size=64)  # Call replay with larger batch size for efficiency

env.close()


# #### Step 4: Evaluate the Performance 
# 
# Finally, you will evaluate the performance of the trained Q-Learning agent.
# 

# In[8]:


for e in range(10):  

    state, _ = env.reset()  # Unpack the state from the tuple 
    state = np.reshape(state, [1, state_size])  # Reshape the state correctly 
    for time in range(500):  
        env.render()  
        action = np.argmax(model.predict(state)[0])  
        next_state, reward, terminated, truncated, _ = env.step(action)  # Unpack the five return values 
        done = terminated or truncated  # Check if the episode is done 
        next_state = np.reshape(next_state, [1, state_size])  
        state = next_state  
        if done:  
            print(f"episode: {e+1}/10, score: {time}")  
            break  

env.close() 


# #### Explanation: 
# - This loop runs 10 episodes to test the trained agent. 
# - `env.render()`: visualizes the environment. 
# - The agent chooses actions based on the trained model and interacts with the environment. 
# - The score for each episode is printed.
# 

# # Practice exercises 
# 
# ## Exercise 1: Experiment with Different Network Architectures 
# 
# ### Objective: 
# Understand how changing the architecture of the neural network affects the performance of the Q-Learning agent. 
# 
# ### Instructions: 
# 1. Modify the `build_model()` function to include a different number of neurons and layers. For example, increase the number of layers to 3 and the number of neurons in each layer to 64. 
# 2. Train the model with the modified architecture and observe the performance in terms of average score achieved over 100 episodes. 
# 3. Compare the performance with the original architecture.
# 

# In[10]:


# Write your code here
# Install gym if necessary
#get_ipython().system('pip install gym')

import gym
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Input
from keras.optimizers import Adam
from collections import deque
import random

# Initialize the environment
env = gym.make('CartPole-v1')

# Global settings
episodes = 10  # Number of episodes
batch_size = 32  # Size of the mini-batch for training
memory = deque(maxlen=2000)  # Memory buffer to store experiences

# Define state size and action size based on the environment
state_size = env.observation_space.shape[0]  # State space size from the environment
action_size = env.action_space.n  # Number of possible actions from the environment

# Define the model
def build_model(state_size, action_size):
    model = Sequential()
    model.add(Input(shape=(state_size,)))  # Explicit Input layer
    model.add(Dense(32, activation='relu'))  # Smaller hidden layers
    model.add(Dense(32, activation='relu'))
    model.add(Dense(action_size, activation='linear'))
    model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))
    return model

# Re-initialize the model with the new architecture
model = build_model(state_size, action_size)

# Placeholder for your action function (e.g., epsilon-greedy)
def act(state):
    return env.action_space.sample()  # For now, a random action is taken

# Function to remember experiences in memory
def remember(state, action, reward, next_state, done):
    memory.append((state, action, reward, next_state, done))

# Optimized function to replay experiences from memory and train the model
def replay(batch_size):
    minibatch = random.sample(memory, batch_size)
    states = np.vstack([sample[0] for sample in minibatch])
    next_states = np.vstack([sample[3] for sample in minibatch])
    targets = model.predict(states)
    target_next = model.predict(next_states)
    
    for i, (state, action, reward, next_state, done) in enumerate(minibatch):
        target = reward if done else reward + 0.95 * np.amax(target_next[i])
        targets[i][action] = target
        
    model.fit(states, targets, epochs=1, verbose=0)

# Train the model with the modified architecture
for e in range(episodes):
    state, _ = env.reset()  # Unpack the state from the tuple
    state = np.reshape(state, [1, state_size])
    for time in range(200):  # Reduced number of steps per episode
        action = act(state)
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        reward = reward if not done else -10
        next_state = np.reshape(next_state, [1, state_size])
        remember(state, action, reward, next_state, done)
        state = next_state
        
        if done:
            print(f"episode: {e+1}/{episodes}, score: {time}")
            break
        
        if len(memory) > batch_size and time % 10 == 0:  # Train every 10 steps
            replay(batch_size)  # Pass the batch size to replay()

env.close()


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# # Install gym if necessary
# !pip install gym
# 
# import gym
# import numpy as np
# from keras.models import Sequential
# from keras.layers import Dense, Input
# from keras.optimizers import Adam
# from collections import deque
# import random
# 
# # Initialize the environment
# env = gym.make('CartPole-v1')
# 
# # Global settings
# episodes = 10  # Number of episodes
# batch_size = 32  # Size of the mini-batch for training
# memory = deque(maxlen=2000)  # Memory buffer to store experiences
# 
# # Define state size and action size based on the environment
# state_size = env.observation_space.shape[0]  # State space size from the environment
# action_size = env.action_space.n  # Number of possible actions from the environment
# 
# # Define the model
# def build_model(state_size, action_size):
#     model = Sequential()
#     model.add(Input(shape=(state_size,)))  # Explicit Input layer
#     model.add(Dense(32, activation='relu'))  # Smaller hidden layers
#     model.add(Dense(32, activation='relu'))
#     model.add(Dense(action_size, activation='linear'))
#     model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))
#     return model
# 
# # Re-initialize the model with the new architecture
# model = build_model(state_size, action_size)
# 
# # Placeholder for your action function (e.g., epsilon-greedy)
# def act(state):
#     return env.action_space.sample()  # For now, a random action is taken
# 
# # Function to remember experiences in memory
# def remember(state, action, reward, next_state, done):
#     memory.append((state, action, reward, next_state, done))
# 
# # Optimized function to replay experiences from memory and train the model
# def replay(batch_size):
#     minibatch = random.sample(memory, batch_size)
#     states = np.vstack([sample[0] for sample in minibatch])
#     next_states = np.vstack([sample[3] for sample in minibatch])
#     targets = model.predict(states)
#     target_next = model.predict(next_states)
#     
#     for i, (state, action, reward, next_state, done) in enumerate(minibatch):
#         target = reward if done else reward + 0.95 * np.amax(target_next[i])
#         targets[i][action] = target
#         
#     model.fit(states, targets, epochs=1, verbose=0)
# 
# # Train the model with the modified architecture
# for e in range(episodes):
#     state, _ = env.reset()  # Unpack the state from the tuple
#     state = np.reshape(state, [1, state_size])
#     for time in range(200):  # Reduced number of steps per episode
#         action = act(state)
#         next_state, reward, terminated, truncated, _ = env.step(action)
#         done = terminated or truncated
#         reward = reward if not done else -10
#         next_state = np.reshape(next_state, [1, state_size])
#         remember(state, action, reward, next_state, done)
#         state = next_state
#         
#         if done:
#             print(f"episode: {e+1}/{episodes}, score: {time}")
#             break
#         
#         if len(memory) > batch_size and time % 10 == 0:  # Train every 10 steps
#             replay(batch_size)  # Pass the batch size to replay()
# 
# env.close()
# ```
# 
# </details>
# 

# ## Exercise 2: Implement an Adaptive Exploration Rate 
# 
# ### Objective: 
# Learn how to adapt the exploration rate (`epsilon`) based on the agent's performance to balance exploration and exploitation. 
# 
# ### Instructions: 
# 1. Modify the `epsilon` decay strategy to decrease more rapidly when the agent's performance improves significantly. 
# 2. Implement a check to reduce `epsilon` faster if the agent achieves a score greater than a certain threshold (e.g., 200) in consecutive episodes. 
# 3. Observe the effect on the learning rate and the agent's performance. 
# 

# In[11]:


# Write your code here
def adjust_epsilon(score, consecutive_success_threshold=200):
    global epsilon 

    if score >= consecutive_success_threshold: 
        epsilon = max(epsilon_min, epsilon * 0.9)  # Reduce epsilon faster if performance is good
    else: 
        epsilon = max(epsilon_min, epsilon * epsilon_decay)  # Regular epsilon decay

episodes = 2  # Set number of episodes for training

# Train the model with adaptive epsilon decay
for e in range(episodes): 
    state = env.reset()  
    state = state[0]  # Extract the first element, which is the actual state array
    state = np.reshape(state, [1, len(state)])  # Reshape state to match the expected input shape

    total_reward = 0 

    for time in range(500):  # Limit the episode to 500 time steps
        action = act(state)  # Choose action based on policy
        next_state, reward, done, truncated, _ = env.step(action)  # Unpack 5 values

        reward = reward if not done else -10  # Penalize for reaching a terminal state
        total_reward += reward  # Accumulate rewards

        next_state = np.reshape(next_state, [1, len(next_state)])  # Reshape next state (optional based on model needs)

        remember(state, action, reward, next_state, done)  # Store experience in memory
        state = next_state  # Update the current state

        if done or truncated:  # Check if the episode is done or truncated
            adjust_epsilon(total_reward)  # Adjust epsilon based on the total reward
            print(f"episode: {e}/{episodes}, score: {time}, e: {epsilon:.2}")  # Print the episode details
            break  # Break out of the loop if the episode is done or truncated

        if len(memory) > batch_size:  # Check if enough experiences are stored in memory
            replay(batch_size)  # Train the model with the stored experiences (pass batch_size here)


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# # Function to adjust epsilon based on performance
# def adjust_epsilon(score, consecutive_success_threshold=200):
#     global epsilon 
# 
#     if score >= consecutive_success_threshold: 
#         epsilon = max(epsilon_min, epsilon * 0.9)  # Reduce epsilon faster if performance is good
#     else: 
#         epsilon = max(epsilon_min, epsilon * epsilon_decay)  # Regular epsilon decay
# 
# episodes = 2  # Set number of episodes for training
# 
# # Train the model with adaptive epsilon decay
# for e in range(episodes): 
#     state = env.reset()  
#     state = state[0]  # Extract the first element, which is the actual state array
#     state = np.reshape(state, [1, len(state)])  # Reshape state to match the expected input shape
# 
#     total_reward = 0 
# 
#     for time in range(500):  # Limit the episode to 500 time steps
#         action = act(state)  # Choose action based on policy
#         next_state, reward, done, truncated, _ = env.step(action)  # Unpack 5 values
# 
#         reward = reward if not done else -10  # Penalize for reaching a terminal state
#         total_reward += reward  # Accumulate rewards
# 
#         next_state = np.reshape(next_state, [1, len(next_state)])  # Reshape next state (optional based on model needs)
# 
#         remember(state, action, reward, next_state, done)  # Store experience in memory
#         state = next_state  # Update the current state
# 
#         if done or truncated:  # Check if the episode is done or truncated
#             adjust_epsilon(total_reward)  # Adjust epsilon based on the total reward
#             print(f"episode: {e}/{episodes}, score: {time}, e: {epsilon:.2}")  # Print the episode details
#             break  # Break out of the loop if the episode is done or truncated
# 
#         if len(memory) > batch_size:  # Check if enough experiences are stored in memory
#             replay(batch_size)  # Train the model with the stored experiences (pass batch_size here)
# ```
# 
# </details>
# 

# ## Exercise 3 : Implement a Custom Reward Function 
# 
# ### Objective: 
# Understand the impact of reward shaping on training the Q-Learning agent. 
# 
# ### Instructions: 
# 1. Modify the reward function to provide more granular feedback to the agent. For example, give higher rewards for keeping the pole more vertical and closer to the center. 
# 2. Implement a reward function that rewards the agent proportionally to the angle of the pole and the distance of the cart from the center. 
# 3. Train the agent with the new reward function and compare the learning speed and stability to the original setting.
# 

# In[12]:


# Write your code here
# Define a custom reward function based on the cart position and pole angle
def custom_reward(state):
    # Extract state variables: x (cart position), x_dot (cart velocity), theta (pole angle), theta_dot (pole angular velocity)
    x, x_dot, theta, theta_dot = state
    
    # Custom reward function: Encourage the agent to keep the cart near the center and the pole upright
    reward = (1 - abs(x) / 2.4) + (1 - abs(theta) / 0.20948)
    
    return reward

episodes = 2  # Number of episodes to run

# Train the model with the custom reward function
for e in range(episodes): 
    state = env.reset()  # Reset the environment

    # Print the state structure for debugging
    print(f"State: {state}, State Type: {type(state)}")

    # Extract the state if it's a tuple and reshape if necessary
    if isinstance(state, tuple):
        state = state[0]  # Extract the first element if it's a tuple

    state = np.reshape(state, [1, state_size])  # Reshape state to match the expected input shape

    for time in range(500):  # Limit the episode to 500 time steps
        action = act(state)  # Choose an action based on the current state
        
        # Unpack 5 values returned by env.step(action)
        next_state, reward, done, truncated, _ = env.step(action)

        # Compute the custom reward based on the next state
        reward = custom_reward(next_state) if not done else -10

        # Reshape next_state if necessary
        if isinstance(next_state, tuple):
            next_state = next_state[0]  # Extract the first element if it's a tuple

        next_state = np.reshape(next_state, [1, state_size])  # Reshape next state to match input shape

        # Store the experience in memory
        remember(state, action, reward, next_state, done)
        state = next_state  # Update the current state

        if done or truncated:  # If the episode is done, break out of the loop
            print(f"episode: {e}/{episodes}, score: {time}, e: {epsilon:.2}")
            break

        if len(memory) > batch_size:  # If there are enough samples in memory, train the model
            replay(batch_size)  # Train the model with a batch of experiences


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# # Define a custom reward function based on the cart position and pole angle
# def custom_reward(state):
#     # Extract state variables: x (cart position), x_dot (cart velocity), theta (pole angle), theta_dot (pole angular velocity)
#     x, x_dot, theta, theta_dot = state
#     
#     # Custom reward function: Encourage the agent to keep the cart near the center and the pole upright
#     reward = (1 - abs(x) / 2.4) + (1 - abs(theta) / 0.20948)
#     
#     return reward
# 
# episodes = 2  # Number of episodes to run
# 
# # Train the model with the custom reward function
# for e in range(episodes): 
#     state = env.reset()  # Reset the environment
# 
#     # Print the state structure for debugging
#     print(f"State: {state}, State Type: {type(state)}")
# 
#     # Extract the state if it's a tuple and reshape if necessary
#     if isinstance(state, tuple):
#         state = state[0]  # Extract the first element if it's a tuple
# 
#     state = np.reshape(state, [1, state_size])  # Reshape state to match the expected input shape
# 
#     for time in range(500):  # Limit the episode to 500 time steps
#         action = act(state)  # Choose an action based on the current state
#         
#         # Unpack 5 values returned by env.step(action)
#         next_state, reward, done, truncated, _ = env.step(action)
# 
#         # Compute the custom reward based on the next state
#         reward = custom_reward(next_state) if not done else -10
# 
#         # Reshape next_state if necessary
#         if isinstance(next_state, tuple):
#             next_state = next_state[0]  # Extract the first element if it's a tuple
# 
#         next_state = np.reshape(next_state, [1, state_size])  # Reshape next state to match input shape
# 
#         # Store the experience in memory
#         remember(state, action, reward, next_state, done)
#         state = next_state  # Update the current state
# 
#         if done or truncated:  # If the episode is done, break out of the loop
#             print(f"episode: {e}/{episodes}, score: {time}, e: {epsilon:.2}")
#             break
# 
#         if len(memory) > batch_size:  # If there are enough samples in memory, train the model
#             replay(batch_size)  # Train the model with a batch of experiences
# 
# ```
# 
# </details>
# 

# #### Conclusion 
# 
# Congratulations on completing this lab!  In this lab, you explored various strategies to enhance the performance of the Q-Learning agent, such as experimenting with different network architectures, implementing adaptive exploration rates, and customizing the reward function. These variations help reinforce your understanding of the Q-Learning algorithm's flexibility and the impact of different hyperparameters and strategies on the learning process.  
# 

# ## Authors
# 

# Skills Network
# 

# Copyright © IBM Corporation. All rights reserved.
# 

# In[ ]:





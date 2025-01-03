#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo">
#     </a>
# </p>
# 

# <h1>Activation Functions</h1> 
# 

# <h2>Objective</h2><ul><li> How to apply different Activation functions in Neural Network.</li></ul> 
# 

# <h2>Table of Contents</h2>
# <p>In this lab, you will cover logistic regression by using PyTorch.</p>
# 
# <ul>
#     <li><a href="#Log">Logistic Function</a></li>
#     <li><a href="#Tanh">Tanh</a></li>
#     <li><a href="#Relu">Relu</a></li>
#     <li><a href="#Compare">Compare Activation Functions</a></li>
# </ul>
# <p>Estimated Time Needed: <strong>15 min</strong></p>
# 
# <hr>
# 

# We'll need the following libraries
# 

# In[1]:


# Import the libraries we need for this lab

import torch.nn as nn
import torch

import matplotlib.pyplot as plt
torch.manual_seed(2)


# <!--Empty Space for separating topics-->
# 

# <h2 id="Log">Logistic Function</h2>
# 

# Create a tensor ranging from -10 to 10: 
# 

# In[2]:


# Create a tensor

z = torch.arange(-10, 10, 0.1,).view(-1, 1)


# When you use sequential, you can create a sigmoid object: 
# 

# In[3]:


# Create a sigmoid object

sig = nn.Sigmoid()


# Apply the element-wise function Sigmoid with the object:
# 

# In[4]:


# Make a prediction of sigmoid function

yhat = sig(z)


# Plot the results: 
# 

# In[5]:


# Plot the result

plt.plot(z.detach().numpy(),yhat.detach().numpy())
plt.xlabel('z')
plt.ylabel('yhat')


# For custom modules, call the sigmoid from the torch (<code>nn.functional</code> for the old version), which applies the element-wise sigmoid from the function module and plots the results:
# 

# In[6]:


# Use the build in function to predict the result

yhat = torch.sigmoid(z)
plt.plot(z.numpy(), yhat.numpy())

plt.show()


# <!--Empty Space for separating topics-->
# 

# <h2 id="Tanh">Tanh</h2>
# 

# When you use sequential, you can create a tanh object:
# 

# In[7]:


# Create a tanh object

TANH = nn.Tanh()


# Call the object and plot it:
# 

# In[8]:


# Make the prediction using tanh object

yhat = TANH(z)
plt.plot(z.numpy(), yhat.numpy())
plt.show()


# 
# For custom modules, call the Tanh object from the torch (nn.functional for the old version), which applies the element-wise sigmoid from the function module and plots the results:
# 

# In[9]:


# Make the prediction using the build-in tanh object

yhat = torch.tanh(z)
plt.plot(z.numpy(), yhat.numpy())
plt.show()


# <!--Empty Space for separating topics-->
# 

# <h2 id="Relu">Relu</h2>
# 

# When you use sequential, you can create a Relu object: 
# 

# In[10]:


# Create a relu object and make the prediction

RELU = nn.ReLU()
yhat = RELU(z)
plt.plot(z.numpy(), yhat.numpy())


# For custom modules, call the relu object from the nn.functional, which applies the element-wise sigmoid from the function module and plots the results:
# 

# In[11]:


# Use the build-in function to make the prediction

yhat = torch.relu(z)
plt.plot(z.numpy(), yhat.numpy())
plt.show()


# <a id="ref3"></a>
# <h2> Compare Activation Functions </h2>
# 

# In[12]:


# Plot the results to compare the activation functions

x = torch.arange(-2, 2, 0.1).view(-1, 1)
plt.plot(x.numpy(), torch.relu(x).numpy(), label='relu')
plt.plot(x.numpy(), torch.sigmoid(x).numpy(), label='sigmoid')
plt.plot(x.numpy(), torch.tanh(x).numpy(), label='tanh')
plt.legend()


# <a id="ref4"></a>
# <h2> Practice </h2>
# 

# Compare the activation functions with a tensor in the range <i>(-1, 1)</i>
# 

# In[13]:


# Practice: Compare the activation functions again using a tensor in the range (-1, 1)

# Type your code here
x = torch.arange(-1, 1, 0.1).view(-1, 1)
plt.plot(x.numpy(), torch.relu(x).numpy(), label = 'relu')
plt.plot(x.numpy(), torch.sigmoid(x).numpy(), label = 'sigmoid')
plt.plot(x.numpy(), torch.tanh(x).numpy(), label = 'tanh')
plt.legend()


# Double-click <b>here</b> for the solution.
# 
# <!-- 
# x = torch.arange(-1, 1, 0.1).view(-1, 1)
# plt.plot(x.numpy(), torch.relu(x).numpy(), label = 'relu')
# plt.plot(x.numpy(), torch.sigmoid(x).numpy(), label = 'sigmoid')
# plt.plot(x.numpy(), torch.tanh(x).numpy(), label = 'tanh')
# plt.legend()
# -->
# 

# 
# <a href="https://dataplatform.cloud.ibm.com/registration/stepone?utm_source=skills_network&utm_content=in_lab_content_link&utm_id=Lab-IBMDeveloperSkillsNetwork-DL0110EN-SkillsNetwork&context=cpdaas&apps=data_science_experience%2Cwatson_machine_learning"><img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DL0110EN-SkillsNetwork/Template/module%201/images/Watson_Studio.png"></a>
# 

# <!--Empty Space for separating topics-->
# 

# <h2>About the Authors:</h2> 
# 
# <a href="https://www.linkedin.com/in/joseph-s-50398b136/">Joseph Santarcangelo</a> has a PhD in Electrical Engineering, his research focused on using machine learning, signal processing, and computer vision to determine how videos impact human cognition. Joseph has been working for IBM since he completed his PhD. 
# 

# Other contributors: <a href="https://www.linkedin.com/in/michelleccarey/">Michelle Carey</a>, <a href="https://www.linkedin.com/in/jiahui-mavis-zhou-a4537814a">Mavis Zhou</a>
# 

# <!--
# ## Change Log
# 
# |  Date (YYYY-MM-DD) |  Version | Changed By  |  Change Description |
# |---|---|---|---|
# | 2020-09-23  | 2.0  | Shubham  |  Migrated Lab to Markdown and added to course repo in GitLab |
# -->
# 

# <hr>
# 

# 
# 
# 
# ## <h3 align="center"> &#169; IBM Corporation. All rights reserved. <h3/>
# 

#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo">
#     </a>
# </p>
# 

# <h1>Simple One Hidden Layer Neural Network</h1>
# 

# <h2>Objective</h2><ul><li> How to create simple Neural Network in pytorch.</li></ul> 
# 

# <h2>Table of Contents</h2>
# <p>In this lab, you will use a single-layer neural network to classify non linearly seprable data in 1-Ddatabase.</p>
# 
# <ul>
#     <li><a href="#Model">Neural Network Module and Training Function</a></li>
#     <li><a href="#Makeup_Data">Make Some Data</a></li>
#     <li><a href="#Train">Define the Neural Network, Criterion Function, Optimizer, and Train the Model</a></li>
# </ul>
# <p>Estimated Time Needed: <strong>25 min</strong></p>
# 
# <hr>
# 

# <h2>Preparation</h2>
# 

# We'll need the following libraries
# 

# In[1]:


# Import the libraries we need for this lab

import torch 
import torch.nn as nn
from torch import sigmoid
import matplotlib.pylab as plt
import numpy as np
torch.manual_seed(0)


# Used for plotting the model
# 

# In[2]:


# The function for plotting the model

def PlotStuff(X, Y, model, epoch, leg=True):
    
    plt.plot(X.numpy(), model(X).detach().numpy(), label=('epoch ' + str(epoch)))
    plt.plot(X.numpy(), Y.numpy(), 'r')
    plt.xlabel('x')
    if leg == True:
        plt.legend()
    else:
        pass


# <!--Empty Space for separating topics-->
# 

# <h2 id="Model">Neural Network Module and Training Function</h2> 
# 

# Define the activations and the output of the first linear layer as an attribute. Note that this is not good practice. 
# 

# In[3]:


# Define the class Net

class Net(nn.Module):
    
    # Constructor
    def __init__(self, D_in, H, D_out):
        super(Net, self).__init__()
        # hidden layer 
        self.linear1 = nn.Linear(D_in, H)
        self.linear2 = nn.Linear(H, D_out)
        # Define the first linear layer as an attribute, this is not good practice
        self.a1 = None
        self.l1 = None
        self.l2=None
    
    # Prediction
    def forward(self, x):
        self.l1 = self.linear1(x)
        self.a1 = sigmoid(self.l1)
        self.l2=self.linear2(self.a1)
        yhat = sigmoid(self.linear2(self.a1))
        return yhat


# Define the training function:
# 

# In[4]:


# Define the training function

def train(Y, X, model, optimizer, criterion, epochs=1000):
    cost = []
    total=0
    for epoch in range(epochs):
        total=0
        for y, x in zip(Y, X):
            yhat = model(x)
            loss = criterion(yhat, y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            #cumulative loss 
            total+=loss.item() 
        cost.append(total)
        if epoch % 300 == 0:    
            PlotStuff(X, Y, model, epoch, leg=True)
            plt.show()
            model(X)
            plt.scatter(model.a1.detach().numpy()[:, 0], model.a1.detach().numpy()[:, 1], c=Y.numpy().reshape(-1))
            plt.title('activations')
            plt.show()
    return cost


# <!--Empty Space for separating topics-->
# 

# <h2 id="Makeup_Data">Make Some Data</h2>
# 

# In[5]:


# Make some data

X = torch.arange(-20, 20, 1).view(-1, 1).type(torch.FloatTensor)
Y = torch.zeros(X.shape[0])
Y[(X[:, 0] > -4) & (X[:, 0] < 4)] = 1.0


# <!--Empty Space for separating topics-->
# 

# <h2 id="Train">Define the Neural Network, Criterion Function, Optimizer and Train the Model</h2>
# 

# Create the Cross-Entropy loss function: 
# 

# In[6]:


# The loss function

def criterion_cross(outputs, labels):
    out = -1 * torch.mean(labels * torch.log(outputs) + (1 - labels) * torch.log(1 - outputs))
    return out


# Define the Neural Network, Optimizer, and Train the Model:
# 

# In[8]:


# Train the model
# size of input 
D_in = 1
# size of hidden layer 
H = 2
# number of outputs 
D_out = 1
# learning rate 
learning_rate = 0.1
# create the model 
model = Net(D_in, H, D_out)
#optimizer 
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
#train the model usein
cost_cross = train(Y, X, model, optimizer, criterion_cross, epochs=1000)
#plot the loss
plt.plot(cost_cross)
plt.xlabel('epoch')
plt.title('cross entropy loss')


# By examining the output of the  activation, you see by the 600th epoch that the data has been mapped to a linearly separable space.
# 

# we can make a prediction for a arbitrary one tensors 
# 

# In[9]:


x=torch.tensor([0.0])
yhat=model(x)
yhat


# we can make a prediction for some arbitrary one tensors  
# 

# In[10]:


X_=torch.tensor([[0.0],[2.0],[3.0]])
Yhat=model(X_)
Yhat


# we  can threshold the predication
# 

# In[11]:


Yhat=Yhat>0.5
Yhat


# <h3>Practice</h3>
# 

# Repeat the previous steps above by using the MSE cost or total loss: 
# 

# In[12]:


# Practice: Train the model with MSE Loss Function

# Type your code here
learning_rate = 0.1
criterion_mse=nn.MSELoss()
model=Net(D_in,H,D_out)
optimizer=torch.optim.SGD(model.parameters(), lr=learning_rate)
cost_mse=train(Y,X,model,optimizer,criterion_mse,epochs=1000)
plt.plot(cost_mse)
plt.xlabel('epoch')
plt.title('MSE loss ')


# Double-click <b>here</b> for the solution.
# 
# <!-- 
# learning_rate = 0.1
# criterion_mse=nn.MSELoss()
# model=Net(D_in,H,D_out)
# optimizer=torch.optim.SGD(model.parameters(), lr=learning_rate)
# cost_mse=train(Y,X,model,optimizer,criterion_mse,epochs=1000)
# plt.plot(cost_mse)
# plt.xlabel('epoch')
# plt.title('MSE loss ')
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
# ## <h3 align="center"> &#169; IBM Corporation. All rights reserved. <h3/>
# 

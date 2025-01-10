#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo">
#     </a>
# </p>
# 

# # **Fine-Tuning Transformers with PyTorch and Hugging Face**
# 
# Estimated time needed: **45** minutes
# 

# # Introduction
# 
# This project aims to introduce you to the process of loading and fine-tuning pretrained large language models (LLMs) 
# 
# You will learn how to implement the training loop of a model using pytorch to tune a model on task-specific data, as well as fine-tuning a model on task-specific data using the SFTTrainer module from Hugging Face. Finally, you will learn how to evaluate the performance of the fine-tuned models.
# 
# By the end of this project, you will have a solid understanding of how to leverage pretrained LLMs and fine-tune them for your specific use cases, empowering you to create powerful and customized natural language processing solutions.
# 

# # __Table of Contents__
# 
# <ol>
#     <li><a href="#Objectives">Objectives</a></li>
#     <li>
#         <a href="#Setup">Setup</a>
#         <ol>
#             <li><a href="#Installing-required-libraries">Installing required libraries</a></li>
#             <li><a href="#Importing-required-libraries">Importing required libraries</a></li>
#         </ol>
#     </li>
#     <li><a href="#Supervised-Fine-tuning-with-PyTorch)">Supervised Fine-tuning with Pytorch</a>
#         <ol>
#             <li><a href="#Dataset-preparations">Dataset preparations</a></li>
#             <li><a href="#Train-the-model">Train the model</a></li>
#             <li><a href="#Evaluate">Evaluate</a></li>
#             <li><a href="#Loading-the-saved-model">Loading the saved model</a></li>
#         </ol>
#     </li>
#     <li><a href="#Exercise:-Training-a-conversational-model-using-SFTTrainer">Exercise: Training a conversational model using SFTTrainer</a></li>
# </ol>
# 

# ---
# 

# # Objectives
# 
# After completing this lab, you will be able to:
# 
#  - Load pretrained LLMs from Hugging Face and make inferences
#  - Fine-tune a model on task-specific data using the SFTTrainer module from Hugging Face
#  - Load a SFTTrainer pretrained model and make comparisons
#  - Evaluate the model
# 

# ---
# 

# # Setup
# 

# ### Installing required libraries
# 
# The following required libraries are pre-installed in the Skills Network Labs environment. However, if you run this notebook commands in a different Jupyter environment (e.g. Watson Studio or Ananconda), you will need to install these libraries by removing the `#` sign before `!pip` in the code cell below.
# 

# In[1]:


# All Libraries required for this lab are listed below. The libraries pre-installed on Skills Network Labs are commented.
# !pip install -qy pandas==1.3.4 numpy==1.21.4 seaborn==0.9.0 matplotlib==3.5.0 torch=2.1.0+cu118
# - Update a specific package
# !pip install pmdarima -U
# - Update a package to specific version
# !pip install --upgrade pmdarima==2.0.2
# Note: If your environment doesn't support "!pip install", use "!mamba install"


# The following required libraries are __not__ pre-installed in the Skills Network Labs environment. __You will need to run the following cell__ to install them:
# 

# In[2]:


#get_ipython().system('pip install transformers==4.42.1')
#get_ipython().system('pip install datasets # 2.20.0')
#get_ipython().system('pip install portalocker>=2.0.0')
#get_ipython().system('pip install torch==2.3.1')
#get_ipython().system('pip install torchmetrics==1.4.0.post0')
#!pip install numpy==1.26.4
#!pip install peft==0.11.1
#!pip install evaluate==0.4.2
#!pip install -q bitsandbytes==0.43.1
#get_ipython().system('pip install accelerate==0.31.0')
#get_ipython().system('pip install torchvision==0.18.1')


#get_ipython().system('pip install trl==0.9.4')
#get_ipython().system('pip install protobuf==3.20.*')
#get_ipython().system('pip install matplotlib')


# ### Importing required libraries
# 
# _It is recommended that you import all required libraries in one place (here):_
# * Note: If you get an error after running the cell below, try restarting the Kernel, as some packages need a restart to be effective.
# 

# In[1]:


import torch
from torchmetrics import Accuracy
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import AutoConfig,AutoModelForCausalLM,AutoModelForSequenceClassification,BertConfig,BertForMaskedLM,TrainingArguments, Trainer, TrainingArguments
from transformers import AutoTokenizer,BertTokenizerFast,TextDataset,DataCollatorForLanguageModeling
from transformers import pipeline
from datasets import load_dataset
from trl import SFTConfig,SFTTrainer, DataCollatorForCompletionOnlyLM


#import numpy as np
#import pandas as pd
from tqdm.auto import tqdm
import math
import time
import matplotlib.pyplot as plt
#import pandas as pd


# You can also use this section to suppress warnings generated by your code:
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.filterwarnings('ignore')


# ---
# 

# # Supervised Fine-tuning with Pytorch
# 
# Fine-tuning Transformers, specifically BERT (Bidirectional Encoder Representations from Transformers), refers to the process of training a pretrained BERT model on a specific downstream task. BERT is an encoder-only language model that has been pretrained on a large corpus of text to learn contextual representations of words.
# 
# Fine-tuning BERT involves taking the pretrained model and further training it on a task-specific dataset, such as sentiment analysis or question answering. During fine-tuning, the parameters of the pretrained BERT model are updated and adapted to the specifics of the target task.
# 
# This process is important because it allows you to leverage the knowledge and language understanding captured by BERT and apply it to different tasks. By fine-tuning BERT, you can benefit from its contextual understanding of language and transfer that knowledge to specific domain-specific or task-specific problems. Fine-tuning enables BERT to learn from a smaller labeled dataset and generalize well to unseen examples, making it a powerful tool for various natural language processing tasks. It helps to bridge the gap between pretraining on a large corpus and the specific requirements of downstream applications, ultimately improving the performance and effectiveness of models in various real-world scenarios.
# 

# ## Dataset preparations
# 
# The Yelp review dataset is a widely used dataset in natural language processing (NLP) and sentiment analysis research. It consists of user reviews and accompanying metadata from the Yelp platform, which is a popular online platform for reviewing and rating local businesses such as restaurants, hotels, and shops.
# 
# The dataset includes 6,990,280 reviews written by Yelp users, covering a wide range of businesses and locations. Each review typically contains the text of the review itself alongwith the star rating given by the user (ranging from 1 to 5).
# 
# Our aim in this lab, is to fine-tune a pretrained BERT model to predict the ratings from reviews.
# 

# Let's start by loading the yelp_review data:
# 

# In[4]:


dataset = load_dataset("yelp_review_full")

dataset


# Let's check a sample record of the dataset:
# 

# In[5]:


dataset["train"][100]


# the label is the key of the class label
# 

# In[6]:


dataset["train"][100]["label"]


# there is also the text
# 

# In[7]:


dataset["train"][100]['text']


# You can select a portion of data to decrease the training time:
# 

# In[8]:


dataset["train"] = dataset["train"].select([i for i in range(1000)])
dataset["test"] = dataset["test"].select([i for i in range(200)])


# There are two data fields:
# - label: the label for the review
# - text: a string containing the body of the user review
# 

# ### Tokenizing data
# 
# The next step is to load a BERT tokenizer to tokenize, pad and truncate reviews to handle variable-length sequences:
# 

# In[9]:


# Instantiate a tokenizer using the BERT base cased model
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

# Define a function to tokenize examples
def tokenize_function(examples):
    # Tokenize the text using the tokenizer
    # Apply padding to ensure all sequences have the same length
    # Apply truncation to limit the maximum sequence length
    return tokenizer(examples["text"], padding="max_length", truncation=True)


# Apply the tokenize function to the dataset in batches
tokenized_datasets = dataset.map(tokenize_function, batched=True)


# The keys in each element of tokenized_datasets are 'label', 'text', 'input_ids', 'token_type_ids', and 'attention_mask'.
# 

# In[10]:


tokenized_datasets['train'][0].keys()


# To apply the preprocessing function over the entire dataset, let's use the map method. You can speed up the map function by setting batched=True to process multiple elements of the dataset at once:
# 

# Since the model is built on the PyTorch framework, it is crucial to prepare the dataset in a format that PyTorch can readily process. Follow these steps to ensure compatibility:
# 

# In[11]:


# Remove the text column because the model does not accept raw text as an input
tokenized_datasets = tokenized_datasets.remove_columns(["text"])

# Rename the label column to labels because the model expects the argument to be named labels
tokenized_datasets = tokenized_datasets.rename_column("label", "labels")

# Set the format of the dataset to return PyTorch tensors instead of lists
tokenized_datasets.set_format("torch")


# the result is a set of tensors with the keys as:  'labels', 'input_ids', 'token_type_ids', 'attention_mask'
# 

# In[12]:


tokenized_datasets['train'][0].keys()


# ### DataLoader
# 

# Next, create a DataLoader for train and test datasets so you can iterate over batches of data:
# 

# In[13]:
print("DataLoader")

# Create a training data loader
train_dataloader = DataLoader(tokenized_datasets["train"], shuffle=True, batch_size=2)

# Create an evaluation data loader
eval_dataloader = DataLoader(tokenized_datasets["test"], batch_size=2)


# ## Train the model
# 

# You’re ready to start training your model, now!
# In this section, you will learn to create the training loop from scratch without the help of the Hugging Face trainer class.
# In the MLM task, you utilized the Hugging Face trainer module. Now, you will develop the trainer yourself.
# 

# ### Load a pretrained model
# 

# Here, you'll load a pretrained classification model with 5 classes:
# 

# In[14]:


# Instantiate a sequence classification model
model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=5)


# ### Optimizer and learning rate schedule
# 
# Let's create an optimizer and learning rate scheduler to fine-tune the model. You can use the AdamW optimizer from PyTorch:
# 

# In[15]:


# Define the optimizer
optimizer = AdamW(model.parameters(), lr=5e-4)

# Set the number of epochs
num_epochs = 10

# Calculate the total number of training steps
num_training_steps = num_epochs * len(train_dataloader)

# Define the learning rate scheduler
lr_scheduler = LambdaLR(optimizer, lr_lambda=lambda current_step: (1 - current_step / num_training_steps))


#  Check if CUDA is available and, then set the device accordingly.
# 

# In[16]:


# Check if CUDA is available and set the device accordingly
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# Move the model to the appropriate device
model.to(device)


# ### Training loop
# 
# You are ready to fine-tune the model. To keep track of training progress, let's use the "tqdm" library to add a progress bar over the number of training steps.
# The train_model function trains a model using a set of training data provided through a dataloader. It begins by setting up a progress bar to help monitor the training progress visually. The model is switched to training mode, which is necessary for certain model behaviors like dropout to work correctly during training. The function processes the data in batches for each epoch, which involves several steps for each batch: transferring the data to the correct device (like a GPU), running the data through the model to get outputs and calculate loss, updating the model's parameters using the calculated gradients, adjusting the learning rate, and clearing the old gradients. These steps are repeated for each batch of data, and the progress bar is updated accordingly to reflect the progress. Once all epochs are completed, the trained model is saved to be used later.
# 
# 
# 
# 
# 
# 
# 
# 

# In[17]:


def train_model(model,tr_dataloader):

    # Create a progress bar to track the training progress
    progress_bar = tqdm(range(num_training_steps))

    # Set the model in training mode
    model.train()
    tr_losses=[]
    # Training loop
    for epoch in range(num_epochs):
        total_loss = 0 
        # Iterate over the training data batches
        for batch in tr_dataloader:
            # Move the batch to the appropriate device
            batch = {k: v.to(device) for k, v in batch.items()}
            # Forward pass through the model
            outputs = model(**batch)
            # Compute the loss
            loss = outputs.loss
            # Backward pass (compute gradients)
            loss.backward()
            
            total_loss += loss.item()
            # Update the model parameters
            optimizer.step()
            # Update the learning rate scheduler
            lr_scheduler.step()
            # Clear the gradients
            optimizer.zero_grad()
            # Update the progress bar
            progress_bar.update(1)
        tr_losses.append(total_loss/len(tr_dataloader))
    #plot loss
    plt.plot(tr_losses)
    plt.title("Training loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.show()  


# ## Evaluate
# The evaluate_model function works similarly to the train_model function but is used for evaluating the model's performance instead of training it. It uses a dataloader to process data in batches, setting the model to evaluation mode to ensure accuracy in measurements and disabling gradient calculations since it's not training. The function calculates predictions for each batch, updates an accuracy metric, and finally, prints the overall accuracy after processing all batches.
# 
# 
# 
# 
# 
# 
# 

# In[18]:


def evaluate_model(model, evl_dataloader):
    # Create an instance of the Accuracy metric for multiclass classification with 5 classes
    metric = Accuracy(task="multiclass", num_classes=5).to(device)

    # Set the model in evaluation mode
    model.eval()

    # Disable gradient calculation during evaluation
    with torch.no_grad():
        # Iterate over the evaluation data batches
        for batch in evl_dataloader:
            # Move the batch to the appropriate device
            batch = {k: v.to(device) for k, v in batch.items()}

            # Forward pass through the model
            outputs = model(**batch)

            # Get the predicted class labels
            logits = outputs.logits
            predictions = torch.argmax(logits, dim=-1)

            # Accumulate the predictions and labels for the metric
            metric(predictions, batch["labels"])

    # Compute the accuracy
    accuracy = metric.compute()

    # Print the accuracy
    print("Accuracy:", accuracy.item())



# You can now train the model. This process will take a long time, and it is highly recommended that you do this only if you have the required resources. Please uncomment the following code to train the model.
# 

# In[19]:


# train_model(model=model,tr_dataloader=train_dataloader)

# torch.save(model, 'my_model.pt')


# ![loss_gpt.png](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/HausLW2F_w30s1UK0zj7mQ/training-loss-BERT-Classification.png)
# 

# You are now ready to learn how to tune a more complex model that can generate conversations between a human and an assistant.
# 

# ## Loading the saved model
# If you want to skip training and load the model that you trained for 10 epochs, go ahead and uncomment the following cell:
# 

# In[20]:


#get_ipython().system("wget 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/wFhKpkBMSgjmZKRSyayvsQ/bert-classification-model.pt'")
import os
import requests

if os.path.exists('bert-classification-model.pt') :
    print("Le fichier bert-classification-model.pt existe")
else :
    url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/wFhKpkBMSgjmZKRSyayvsQ/bert-classification-model.pt'
    response = requests.get(url)

    with open('bert-classification-model.pt', 'wb') as f:
        f.write(response.content)

model.load_state_dict(torch.load('bert-classification-model.pt',map_location=torch.device('cpu')))


# You can now evaluate the model. Please note that this process will take a while.
# 

# In[21]:
print("Evaluate the model, takes long")

#evaluate_model(model, eval_dataloader)


# You are now ready to learn to tune a more complex model that can generate conversations between a human and an assistant using SFTtrainer.
# 

# # Exercise: Training a conversational model using SFTTrainer
# 
# The SFTTrainer from the trl (Transformers Reinforcement Learning) library is a tool used for supervised fine-tuning of language models. It helps refine pre-trained models using specific datasets to enhance their performance on targeted tasks.
# 

# ## Objective
# Explore how fine-tuning a decoder transformer using a specific dataset affects the quality of the generated responses in a question-answering task.
# 

# Step 1- Load the train split of "timdettmers/openassistant-guanaco" dataset from Hugging Face:
# 

# In[ ]:

print("Exercice")
## Write your code here
# load dataset
dataset = load_dataset("timdettmers/openassistant-guanaco", split="train")
dataset[0]


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# # load dataset
# dataset = load_dataset("timdettmers/openassistant-guanaco", split="train")
# dataset[0]
# ```
# 
# </details>
# 

# Step 2- Load the pretrained causal model "facebook/opt-350m" along with its tokenizer from Hugging Face:
# 

# In[ ]:


## Write your code here
# load Hugging Face pretrained model and tokenizer
model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")
tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m")


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# # load Hugging Face pretrained model and tokenizer
# model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")
# tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m")
# ```
# 
# </details>
# 

# Step 3- Create instruction and response templates based on the train dataset format:
# 

# In[14]:


## Write your code here
instruction_template = "### Human:"
response_template = "### Assistant:"


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# instruction_template = "### Human:"
# response_template = "### Assistant:"
# ```
# 
# </details>
# 

# Step 4- Create a collator to curate data in the appropriate shape for training using "DataCollatorForCompletionOnlyLM":
# 

# In[15]:


## Write your code here
collator = DataCollatorForCompletionOnlyLM(instruction_template=instruction_template, response_template=response_template, tokenizer=tokenizer, mlm=False)


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# collator = DataCollatorForCompletionOnlyLM(instruction_template=instruction_template, response_template=response_template, tokenizer=tokenizer, mlm=False)
# 
# ```
# 
# </details>
# 

# Step 5- Create an SFTTrainer object and pass the model as well as the dataset and collator: 
# 

# In[16]:


## Write your code here
training_args = SFTConfig(
    output_dir="/tmp",
    num_train_epochs=10,
    #learning_rate=2e-5,
    save_strategy="epoch",
    fp16=True,
    per_device_train_batch_size=2,  # Reduce batch size
    per_device_eval_batch_size=2,  # Reduce batch size
    #gradient_accumulation_steps=4,  # Accumulate gradients
    max_seq_length=1024,
    do_eval=True
)

trainer = SFTTrainer(
    model,
    args=training_args,
    train_dataset=dataset,
#AV    dataset_text_field="text",
    data_collator=collator,
)


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# 
# training_args = SFTConfig(
#     output_dir="/tmp",
#     num_train_epochs=10,
#     #learning_rate=2e-5,
#     save_strategy="epoch",
#     fp16=True,
#     per_device_train_batch_size=2,  # Reduce batch size
#     per_device_eval_batch_size=2,  # Reduce batch size
#     #gradient_accumulation_steps=4,  # Accumulate gradients
#     max_seq_length=1024,
#     do_eval=True
# )
# 
# trainer = SFTTrainer(
#     model,
#     args=training_args,
#     train_dataset=dataset,
#     dataset_text_field="text",
#     data_collator=collator,
# )
# ```
# 
# </details>
# 

# Step 6- Prompt the pretrained model with a specific question: 
# 

# In[17]:


## Write your code here
pipe = pipeline("text-generation", model=model,tokenizer=tokenizer,max_new_tokens=70)
print(pipe('''Can you write a short introduction about the relevance of the term "monopsony" in economics? Please use examples related to potential monopsonies in the labour market and cite relevant research.''')[0]["generated_text"])


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# pipe = pipeline("text-generation", model=model,tokenizer=tokenizer,max_new_tokens=70)
# print(pipe('''Can you write a short introduction about the relevance of the term "monopsony" in economics? Please use examples related to potential monopsonies in the labour market and cite relevant research.''')[0]["generated_text"])
# ```
# 
# </details>
# 

# Looks like the model is barely aware of what "monopsony" is in the context of economics.
# 

# Step 6A (Optional)- Train the model:
# 

# In[ ]:


## Write your code here
# too long !
# trainer.train()


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# trainer.train()
# ```
# 
# </details>
# 

# * If you do not have enough resources to run the training, load the tuned model we provide here: "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/Assistant_model.pt":
# 

# 
# Step 6B- Load the tuned model: 
# 

# In[ ]:

print("step 6")
## Write your code here
#get_ipython().system("wget 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/Assistant_model.pt'")
if os.path.exists('Assistant_model.pt') :
    print("Le fichier Assistant_model.pt existe")
else :
    url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/Assistant_model.pt'
    response = requests.get(url)

    with open('Assistant_model.pt', 'wb') as f:
        f.write(response.content)

model.load_state_dict(torch.load('Assistant_model.pt',map_location=torch.device('cpu')))


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# !wget 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/Assistant_model.pt'
# model.load_state_dict(torch.load('Assistant_model.pt',map_location=torch.device('cpu')))
# ```
# 
# </details>
# 

# Step 7- Check how the tuned model performs in answering the same specialized question:
# 

# In[ ]:

print("step 7")
## Write your code here
pipe = pipeline("text-generation", model=model,tokenizer=tokenizer,max_new_tokens=70)
print(pipe('''Can you write a short introduction about the relevance of the term "monopsony" in economics? Please use examples related to potential monopsonies in the labour market and cite relevant research.''')[0]["generated_text"])


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# pipe = pipeline("text-generation", model=model,tokenizer=tokenizer,max_new_tokens=70)
# print(pipe('''Can you write a short introduction about the relevance of the term "monopsony" in economics? Please use examples related to potential monopsonies in the labour market and cite relevant research.''')[0]["generated_text"])
# ```
# 
# </details>
# 

# # Congratulations! You have completed the lab
# 

# ## Authors
# 

# [Fateme Akbari](https://author.skills.network/instructors/fateme_akbari) is a Ph.D. candidate in Information Systems at McMaster University with demonstrated research experience in Machine Learning and NLP.
# 

# © Copyright IBM Corporation. All rights reserved.
# 

#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo"  />
#     </a>
# </p>
# 

# # Reinforcement Learning from Human Feedback Using PPO
# 

# Estimated time needed: **30** minutes
# 

# 
# Imagine you are an AI engineer who wants to train a "Happy LLM" and a "Pessimistic LLM" to train customer service agents. You have a reward function trained on the sentiment classifier from the IMDb dataset, and you will now use Reinforcement Learning (RL). RL is a subfield of machine learning where an agent learns to make decisions by performing actions in an environment to maximize a cumulative reward. The agent, in this case, will be the LLM, and the decisions will be about what text to output. Unlike supervised learning, which requires labeled input/output pairs, RL relies on the agent exploring the environment and learning from the feedback it receives in the form of rewards or penalties. This trial-and-error approach enables the agent to improve its decision-making strategy over time.
# 
# Proximal Policy Optimization (PPO) is one of the most effective and widely used RL algorithms. Introduced by OpenAI, PPO strikes a balance between simplicity and performance, making it a popular choice for training RL agents. PPO optimizes the policy directly and employs mechanisms to ensure the updates are not too drastic, thereby maintaining stability and reliability during training.
# 
# In this lab, you will be guided through the process of training an RL agent using the PPO algorithm with a focus on sentiment analysis. You will use the IMDb dataset, a large collection of movie reviews, to train your model. By the end of this lab, you will have a solid understanding of how to implement and train an RL agent using PPO, and you will be equipped with practical skills to apply RL techniques to other problems and datasets.
# This lab is based on [a HF example code titled `Tune GPT2 to generate positive reviews`](https://github.com/huggingface/trl/blob/main/examples/notebooks/gpt2-sentiment.ipynb).
# 

# ## __Table of Contents__
# 
# <ol>
#     <li><a href="#Objectives">Objectives</a></li>
#     <li>
#         <a href="#Setup">Setup</a>
#         <ol>
#             <li><a href="#Installing-required-libraries">Installing required libraries</a></li>
#             <li><a href="#Importing-required-libraries">Importing required libraries</a></li>
#             <li><a href="#Defining-helper-functions">Defining helper functions</a></li>
#         </ol>
#     </li>
#     <li><a href="#Initializing-the-PPO-configuration,-model,-and-tokenizer">Initializing the PPO configuration, model, and tokenizer</a></li>
#             <li><a href="#Dataset-and-dataset-tokenization">Dataset and dataset tokenization</a></li>
#             <li><a href="#Collator-function">Collator function</a></li>
#             <li><a href="#Initialize-PPOTrainer">Initialize PPOTrainer</a></li>
#             <li><a href="#Reward-function">Reward function</a></li>
#     <li>
#         <a href="#Generating-responses-using-PPO">Generating responses using PPO</a>
#         <ol>
#             <li><a href="#Tokenizing-and-preparing-the-input-batch">Tokenizing and preparing the input batch</a></li>
#             <li><a href="#Scoring-function">Scoring function</a></li>
#             <li><a href="#Proximal-policy-optimization">Proximal policy optimization</a></li>
#         </ol>
#     </li>
#     <li><a href="#Plotting-PPO-training-loss-and-mean">Plotting PPO training loss and mean</a></li>
#     <li><a href="#Generating-and-analyzing-text-with-PPO-and-reference-models">Generating and analyzing text with PPO and reference models</a></li>
#     <li>
#         <a href="#Comparing-PPO-and-reference-models-on">Comparing PPO and reference models on</a>
#         <ol>
#         </ol>
#     </li>
#                 <li><a href="#Running-the-PPO-model-with-negative-sentiment">Running the PPO model with negative sentiment</a></li>
#             <li><a href="#Comparing-models-with-negative-sentiment">Comparing models with negative sentiment</a></li>
#             <li><a href="#Exercise:-Comparing-PPO-models">Exercise: Comparing PPO models</a></li>
# </ol>
# 

# ## Objectives
# 
# After completing this lab you will be able to:
# 
# - Apply the basics of reinforcement learning and proximal policy optimization (PPO).
# - Set up the environment and load the IMDb dataset for training.
# - Define and configure the PPO agent and tokenizer.
# - Implement the PPO training loop.
# - Generate and evaluate text responses from the trained model.
# - Compare the performance of two models on the dataset.
# - Save and load the trained model for future use.
# 

# ----
# 

# ## Setup
# 

# For this lab, you will use the following libraries:
# 
# *   [`pandas`](https://pandas.pydata.org/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for managing the data.
# *   [`torch`](https://pytorch.org/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for tensor operations and model training.
# *   [`tqdm`](https://tqdm.github.io/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for progress bars.
# *   [`transformers`](https://huggingface.co/transformers/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for pretrained language models.
# *   [`datasets`](https://huggingface.co/docs/datasets/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for loading and processing datasets.
# *   [`trl`](https://github.com/lvwerra/trl/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for Proximal Policy Optimization (PPO) training.
# *   [`matplotlib`](https://matplotlib.org/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for plotting tools.
# *   [`tarfile`](https://docs.python.org/3/library/tarfile.html/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for handling tar file operations.
# *   [`pickle`](https://docs.python.org/3/library/pickle.html/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for serializing and deserializing Python objects.
# *   [`json`](https://docs.python.org/3/library/json.html/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMML0187ENSkillsNetwork31430127-2021-01-01) for parsing and writing JSON data.
# 

# ### Installing required libraries
# 
# The following required libraries are __not__ preinstalled in the Skills Network Labs environment. __You must run the following cell__ to install them:
# 
# **Note:** The version has been pinned to specify the version. It's recommended that you do this as well. Even if the library is updated in the future, the installed library could still support this lab work.
# 
# This might take approximately 1 minute. 
# 

# In[1]:


#get_ipython().system('pip install datasets trl==0.11.0')
#get_ipython().system('pip install --upgrade typing_extensions')
#get_ipython().system('pip install matplotlib')


# ### Importing required libraries
# 
# _It is recommended that you import all required libraries in one place (here):_
# 

# In[2]:


#get_ipython().run_line_magic('load_ext', 'autoreload')
#get_ipython().run_line_magic('autoreload', '2')

# In[3]:


import torch
from tqdm import tqdm
import pandas as pd

tqdm.pandas()

from transformers import pipeline, AutoTokenizer,AutoModelForCausalLM
from datasets import load_dataset

from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from trl.core import LengthSampler
import os

import tarfile
import pickle
import json
import matplotlib.pyplot as plt
import torch
import pandas as pd
import warnings

warnings.filterwarnings('ignore')
# Disable warnings for a cleaner notebook or console experience
def warn(*args, **kwargs):
    pass
warnings.warn = warn


# ## Defining helper functions
# 

# In[4]:


def save_to_json(data, file_path):
    """
    Save a dictionary to a JSON file.

    Args:
        data (dict): The dictionary to save.
        file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data successfully saved to {file_path}")
    
    
def load_from_json(file_path):
    """
    Load data from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The data loaded from the JSON file.
    """
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data   


# In[5]:


def pad_sequence_to_length(tensor, length, pad_token_id):
    padding_length = length - tensor.size(0)
    if padding_length > 0:
        padding = torch.full((padding_length,), pad_token_id, dtype=torch.long, device=tensor.device)
        return torch.cat((tensor, padding))
    return tensor

def pad_list_to_batch_size(tensors, batch_size, pad_token_id):
    max_length = max(t.size(0) for t in tensors)
    padded_tensors = [pad_sequence_to_length(t, max_length, pad_token_id) for t in tensors]

    # Add additional padding-only tensors if needed
    while len(padded_tensors) < batch_size:
        padded_tensors.append(torch.full((max_length,), pad_token_id, dtype=torch.long, device=tensors[0].device))

    return padded_tensors[:batch_size]


# In[6]:


def print_ppo_stats(stats, related_to_objective=False):
    print("PPO Training Statistics\n")

    if related_to_objective:
        print("Objective Statistics:")
        print(f"  KL Divergence (objective/kl): {stats['objective/kl']}")
        print(f"  KL Coefficient (objective/kl_coef): {stats['objective/kl_coef']}")
        print(f"  Entropy (objective/entropy): {stats['objective/entropy']}\n")
        
        print("PPO Losses (Related to Minimizing Objective Function):")
        print(f"  Policy Loss (ppo/loss/policy): {stats['ppo/loss/policy']}")
        print(f"  Value Loss (ppo/loss/value): {stats['ppo/loss/value']}")
        print(f"  Total Loss (ppo/loss/total): {stats['ppo/loss/total']}\n")
        
        print("PPO Policy Statistics:")
        print(f"  Policy Entropy (ppo/policy/entropy): {stats['ppo/policy/entropy']}")
        print(f"  Approx KL (ppo/policy/approxkl): {stats['ppo/policy/approxkl']}")
        print(f"  Clip Fraction (ppo/policy/clipfrac): {stats['ppo/policy/clipfrac']}\n")
    else:
        print("Reward and Value Function Estimation:")
        print(f"  Mean Non-Score Reward (ppo/mean_non_score_reward): {stats['ppo/mean_non_score_reward']}")
        print(f"  Mean Scores (ppo/mean_scores): {stats['ppo/mean_scores']}")
        print(f"  Std Scores (ppo/std_scores): {stats['ppo/std_scores']}")
        print(f"  Value Prediction (ppo/val/vpred): {stats['ppo/val/vpred']}")
        print(f"  Value Prediction Error (ppo/val/error): {stats['ppo/val/error']}")
        print(f"  Value Prediction Variance (ppo/val/var): {stats['ppo/val/var']}")
        print(f"  Value Prediction Mean (ppo/val/mean): {stats['ppo/val/mean']}")
        print(f"  Explained Variance (ppo/val/var_explained): {stats['ppo/val/var_explained']}\n")
    
    print("Token Lengths:")
    print(f"  Queries Length Mean (tokens/queries_len_mean): {stats['tokens/queries_len_mean']}")
    print(f"  Responses Length Mean (tokens/responses_len_mean): {stats['tokens/responses_len_mean']}\n")
    
    print("Time Statistics:")
    print(f"  Total Time (time/ppo/total): {stats['time/ppo/total']} seconds\n")

# Example usage with the provided stats and the flag


# ## Initializing the PPO configuration, model, and tokenizer
# 

# The `PPOConfig` class is used to specify the model and learning rate for the PPO training. In this case, the model is `"lvwerra/gpt2-imdb"` and the learning rate is set to `1.41e-5`.
# 

# In[7]:


config = PPOConfig(
    model_name="lvwerra/gpt2-imdb",
    learning_rate=1.41e-5)


# Please ignore above warning as the trl version you installed supports this module.
# 

# `config.model_name` refers to the specific model identifier used in the configuration for loading the pretrained model. It specifies which model to load from the Hugging Face model repository. In this case, `config.model_name` is set to `"lvwerra/gpt2-imdb"`, indicating that the GPT-2 model fine-tuned on the IMDB dataset (by user lvwerra) should be used. This identifier is essential for loading the correct model architecture and weights during the fine-tuning or inference process.
# 

# In[8]:


config.model_name


# The `sent_kwargs` dictionary contains parameters for the sentiment analysis pipeline, specifying that all scores should be returned, the function to apply is `"none"`, and the batch size is `2`.
# python
# 

# In[9]:


sent_kwargs = {"top_k":None, "function_to_apply": "none", "batch_size": 2}


# The `AutoModelForCausalLMWithValueHead` class is used to load the pretrained GPT-2 model with a value head for PPO training. The model is loaded from the specified model name in the configuration.
# 
# The `AutoTokenizer` class is used to load the tokenizer corresponding to the pretrained model. The tokenizer's padding token is set to the end-of-sequence (EOS) token.
# 

# In[10]:


model_1 = AutoModelForCausalLMWithValueHead.from_pretrained(config.model_name)

tokenizer = AutoTokenizer.from_pretrained(config.model_name)
tokenizer.pad_token = tokenizer.eos_token


# Please ignore above warning as the trl version you installed handles it automatically.
# 

# In[11]:


# first model
model = AutoModelForCausalLMWithValueHead.from_pretrained(config.model_name)


# During PPO training, update the model. In addition, the reference model is used to stabilize the model using the Kullback-Leibler (KL) divergence between the current policy and the reference policy.The KL divergence acts as a regularization term.
# 

# In[12]:


ref_model = AutoModelForCausalLMWithValueHead.from_pretrained(config.model_name)


# ## Dataset and dataset tokenization
# 
# **Dataset Name:** IMDB
# 
# **Description:** The IMDB dataset is a collection of 50,000 movie reviews labeled as "positive" or "negative," indicating the sentiment of each review. This dataset is commonly used for sentiment analysis tasks.
# 
# **Loading the Dataset:**
# The dataset is loaded using the `load_dataset` function from the `datasets` library, specifically loading the "train" split.
# 

# In[13]:


dataset_name = "imdb"
ds = load_dataset(dataset_name, split = "train")


# In[14]:


N = 5
for sample in range(N):
    print('text',ds[sample]['text'])
    print('label',ds[sample]['label'])


#  Rename the column "text" to "review"
# 

# In[15]:


ds = ds.rename_columns({"text": "review"})
print(ds)


# The dataset is filtered to include only reviews that are longer than 200 characters.
# 

# In[16]:


ds = ds.filter(lambda x: len(x["review"]) > 200, batched=False)


# Using a ```LengthSampler``` to sample different text lengths during data processing introduces variability, making the model more robust and capable of handling varying input lengths in real-world scenarios. This approach prevents overfitting by exposing the model to diverse input sizes, improving generalization to new data. It also ensures efficient training by managing the length of text inputs, maintaining practicality and performance. Overall, LengthSampler enhances model adaptability and effectiveness by simulating realistic, varied training conditions. Where sample length is between ```input_min_text_length``` and ```input_max_text_length```
# 
# 
# 
# 
# 
# 
# 

# In[17]:


input_min_text_length, input_max_text_length = 2, 8


# Create a ```LengthSampler``` object
# 

# In[18]:


input_size = LengthSampler(input_min_text_length, input_max_text_length)
print(input_size)


# This code uses the input_size object, an instance of ```LengthSampler```, to sample and print a random text length between 2 and 8 for each of 10 iterations."
# 

# In[19]:


for i in range(10):
    size=input_size()
    print(f"sample {i} has length {size}\n")


# Finally, you will need to sample tokens and obtain tokenized indexes. Let's verify this process with one sample.
# 

# In[20]:


sample=ds[0]
print(sample)


# Next, tokenize the ```review``` text into input IDs, truncate the tokenized sequence to the desired length, and assign it to ```input_ids```
# 

# In[21]:


sample["input_ids"] = tokenizer.encode(sample["review"])[: input_size()]
print(sample["input_ids"])


# Decode the truncated input IDs back into text and assign it to 'query', this is a will need the raw text for the reward fuction.
# 

# In[22]:


sample["query"] = tokenizer.decode(sample["input_ids"])
print(sample["query"])


# In this function, combine the process of tokenizing the 'review' text, truncating it to the desired length, and decoding it back to text. This allows you to apply it to the dataset.
# 

# In[23]:


def tokenize(sample):
    sample["input_ids"] = tokenizer.encode(sample["review"])[: input_size()]
    sample["query"] = tokenizer.decode(sample["input_ids"])
    return sample


# You can apply ```tokenize``` function to the dataset
# 

# In[24]:


ds = ds.map(tokenize, batched=False)
ds.set_format(type="torch")


# >Note: you can safely ignore the above warning.
# You can see the sample before and after:
# 

# In[25]:


print(ds[0])


# You can now iterate over the dataset, printing the first 5 samples with their 'review' and the added 'input_ids', and 'query' :
# 

# In[26]:


for i, sample in enumerate(ds):
    if i >= 5:
        break
    print(f"Sample {i+1}:")
    print(f"Review: {sample['review']}")
    print(f"Input IDs: {sample['input_ids']}")
    print(f"Query: {sample['query']}")
    print("-" * 50)


# The ```build_dataset``` function incorporates the necessary steps to build a dataset object for use as an input to ```PPOTrainer```. You will then reinstantiate the dataset object.
# 

# In[27]:


del(ds)
dataset_name="imdb"
ds = load_dataset(dataset_name, split="train")
ds = ds.rename_columns({"text": "review"})


# In[28]:


def build_dataset(config, dataset_name="imdb", input_min_text_length=2, input_max_text_length=8,tokenizer=tokenizer):
    """
    Build dataset for training. This builds the dataset from `load_dataset`, one should
    customize this function to train the model on its own dataset.

    Args:
        dataset_name (`str`):
            The name of the dataset to be loaded.

    Returns:
        dataloader (`torch.utils.data.DataLoader`):
            The dataloader for the dataset.
    """
    
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    tokenizer.pad_token = tokenizer.eos_token
    # load imdb with datasets
    ds = load_dataset(dataset_name, split="train")
    ds = ds.rename_columns({"text": "review"})
    ds = ds.filter(lambda x: len(x["review"]) > 200, batched=False)

    input_size = LengthSampler(input_min_text_length, input_max_text_length)

    def tokenize(sample):
        sample["input_ids"] = tokenizer.encode(sample["review"])[: input_size()]
        sample["query"] = tokenizer.decode(sample["input_ids"])
        return sample

    ds = ds.map(tokenize, batched=False)
    ds.set_format(type="torch")
    return ds


# Create the dataset object 
# 

# In[29]:


dataset = build_dataset(config)


# You can see each sample has ```input_ids``` and  ```query```
# 

# In[30]:


print(dataset[0])


# ## Collator function 
# The collator function is crucial for preparing data batches in a format suitable for the PPOTrainer. It ensures that each feature from the data samples is grouped together,
# 

# In[31]:


def collator(data):
    return dict((key, [d[key] for d in data]) for key in data[0])


# The collator function is best understood with an example. You can input two samples each with 'input_ids', 'query', and 'review'.
# 

# In[32]:


data = [
    {'input_ids': [1, 2, 3, 4], 'query': "sample text", 'review': "This is a sample review."},
    {'input_ids': [5, 6, 7, 8], 'query': "another sample", 'review': "Another sample review."}
]


# Apply the collator function to the above data
# 

# In[33]:


batch = collator(data)
print(batch)


# Now, 'input_ids', 'query', and 'review' each have their corresponding samples.
# 

# ##  Initialize PPOTrainer 
# 
# Proximal Policy Optimization (PPO) is a reinforcement learning algorithm that is particularly well-suited for training generative models, including those used for chatbots. It helps address specific challenges in training these models, such as maintaining coherent and contextually appropriate dialogues.
# 
# Proximal Policy Optimization (PPO) improves policy gradient methods for chatbots by using a clipped objective function, which ensures gradual and stable policy updates. This helps maintain consistent dialogue quality. Traditional policy gradient methods can lead to high variance and instability, resulting in inconsistent chatbot behavior. PPO's trust region balances exploring new responses and exploiting known good ones, making it more reliable for training chatbots. 
# 
# The PPO Trainer collects dialogue samples, optimizes the chatbot's policy based on these samples, and manages the neural network models. This ensures stable and efficient training, leading to high-quality, coherent, and contextually appropriate chatbot responses. 
# 
# Lets Initialize PPOTrainer with specified configuration and components
# 

# ```config``` : Configuration settings for PPO training, such as learning rate and model name
# 
# ```model``` : The primary model to be fine-tuned using PPO
# 
# ```tokenizer```:Tokenizer corresponding to the model, used for processing input text
# 
# ```dataset```:  Dataset to be used for training, providing the input data for the model
# 
# ```data_collator```: Data collator to handle batching and formatting of the input data
# 

# In[34]:


ppo_trainer = PPOTrainer(config, model, ref_model, tokenizer, dataset=dataset, data_collator=collator)
print("ppo_trainer object ",ppo_trainer)


# Please ignore above warnings as the trl version you installed supports this module.
# 

# Determine the appropriate device (CPU or GPU) for training with the PPO Trainer.
# 

# In[35]:


device = ppo_trainer.accelerator.device
if ppo_trainer.accelerator.num_processes == 1:
    device = 0 if torch.cuda.is_available() else "cpu"  
print(device)


# ## Reward function
# 
# In reinforcement learning with PPO (Proximal Policy Optimization), a reward function is used to provide feedback on the quality of the actions taken by the policy. For a generative model like a chatbot, the reward function can evaluate the quality of the generated responses. Here’s how the sentiment analysis pipeline can be used as a reward function:
# 
# In reinforcement learning with PPO, the sentiment analysis pipeline serves as a reward function to evaluate a chatbot's responses. By analyzing the sentiment of each response and assigning a reward based on the sentiment score, the PPO Trainer can optimize the chatbot’s policy to generate more positively received and engaging responses. This approach leverages sentiment analysis to provide meaningful feedback, guiding the chatbot towards improved performance in dialogue generation. Although not a typical reward model, it allows you to train the chatbot in a simple and effective way.
# 

# First, let's initialize a sentiment analysis pipeline using a pretrained model fine-tuned on IMDB reviews.
# The model predicts the sentiment of text inputs, providing scores for positive and negative sentiments.
# 

# In[36]:


sentiment_pipe = pipeline("sentiment-analysis", model="lvwerra/distilbert-imdb", device=device)


# You'll get the sentiment value as negative here.
# 

# In[37]:


text = "this movie was really bad!!"
sentiment_pipe(text, **sent_kwargs)


# The `score` key represents the model's confidence in its prediction. Higher score values indicate greater confidence in the sentiment classification, such as "POSITIVE" or "NEGATIVE". Thus, the value for `POSITIVE` class can be used to determine the reward values. For example, a high score for "POSITIVE" means the model is confident, which can increase rewards. Conversely, if the model isn’t confident that a review is positive, it results in a negative reward, lowering the total reward. This means negative sentiment reviews decrease the overall reward, while positive ones increase it.
# 

# In[38]:


text = "this movie was really good!!"
sentiment_pipe(text, **sent_kwargs)


# ## Generating responses using PPO 
# 
# ### Tokenizing and preparing the input batch
# This section of code demonstrates how to generate responses using the PPO (Proximal Policy Optimization) Trainer. The process involves tokenizing the input, preparing the batch for training, generating responses, and decoding the generated tokens into readable text.
# 

# The code first retrieves a batch of data from the PPO Trainer's dataloader and selects the first two entries for processing.
# 

# In[39]:


batch = next(iter(ppo_trainer.dataloader))


# The batch contains ```label```, ```input_ids```, and ```query```
# 

# In[40]:


batch.keys()


# Now let's create a new batch containing only the first two samples from the original batch 
# 

# In[41]:


# Let's take the first two  sample in the batch
batch = {key: batch[key][0:2] for key in batch}
print(batch)


# Initialize a list of  ```response_tensors``` to store the responses for scoring
# 

# In[42]:


response_tensors = []


# The below code extracts the `input_ids` from the `batch` and assigns them to `query_tensors`. These tensors represent the tokenized input sequences that will be used in the subsequent steps. They are called "query tensors" because they represent the initial input queries that will be processed by the model to generate responses.
# 

# In[43]:


query_tensors =  batch["input_ids"]
print(query_tensors)


# The below code defines a lambda function `get_text` that takes a list of responses (`response`) and decodes each tensor in the list using the tokenizer, converting the tensor back to readable text. The `squeeze()` method is used to remove any dimensions of size 1 from the tensor.
# 

# In[44]:


get_text = lambda response:''.join([tokenizer.decode(r.squeeze()) for r in response])


# You can see the original input queries in their text form.
# 

# In[45]:


get_text(query_tensors)


# 
# 
# The dictionary `generation_kwargs` sets the parameters for generating a sequence from the LLM (Language Model). The parameters include:
# - `"min_length": -1` - No minimum length for the generated text.
# - `"top_k": 0.0` - No filtering of the top-k most probable tokens.
# - `"top_p": 1.0` - No nucleus sampling, using the entire distribution.
# - `"do_sample": True` - Enables sampling, allowing for varied responses.
# - `"pad_token_id": 50256` - ID of the padding token, ensuring uniform length across sequences.
# 
# 
# 
# 
# 
# 
# 
# 

# In[46]:


generation_kwargs = {
    "min_length": -1,
    "top_k": 0.0,
    "top_p": 1.0,
    "do_sample": True,
    "pad_token_id": 50256,
}
print(generation_kwargs)


# The `output_length_sampler` is initialized with `LengthSampler(output_min_length, output_max_length)`. This object is used to sample output lengths for the generated sequences, ensuring they fall within the specified minimum and maximum length range. By varying the lengths, you can produce more diverse and natural outputs from the language model, preventing the generation of overly short or excessively long sequences and enhancing the overall quality of the responses.
# 

# In[47]:


output_min_length = 4
output_max_length = 16
output_length_sampler = LengthSampler(output_min_length, output_max_length)


# The code calls the `output_length_sampler` to determine a length for the generated sequences. The sampled length is then stored in the variable `gen_len`.
# 

# In[48]:


gen_len = output_length_sampler()
print(gen_len)


# Next, set the `max_new_tokens` parameter in the `generation_kwargs` dictionary to the value of `gen_len`, which was sampled from `output_length_sampler`. This ensures that the maximum number of new tokens generated by the language model is within the desired length range, promoting more controlled and appropriately lengthened responses.
# 

# In[49]:


generation_kwargs["max_new_tokens"] = gen_len
print(generation_kwargs)


# Now, let's process one sample using PPO. Start by extracting the first query tensor.
# 

# In[50]:


query=query_tensors[0]
print(query)


# Lets generate a response for the extracted query using the PPO trainer with the specified generation parameters (generation_kwargs). The generated response tensor is stored in ```response```.
# 

# In[51]:


response = ppo_trainer.generate(query, **generation_kwargs)
print(response)


# >Note: You can safely ignore the above warning
# 
# You can print the decoded text of the query and response tensors using the get_text function, converting the generated response back into a human-readable format. This demonstrates how the model has appended some text to the original query.
# 

# In[52]:


print("query:",get_text(query))
print("response:", get_text(response))


# Finally, append the tokens of the  ```response_tensors``` list. The ```squeeze()``` method removes any single-dimensional entries from the shape of the tensor, and the slicing``` [-gen_len:]``` ensures only the newly generated tokens are included, ignoring any preceding tokens.
# 

# In[53]:


response_tensors.append(response.squeeze()[-gen_len:])
print("newly generated tokens form response:", get_text(response_tensors[-gen_len:]))


# Repeat the process for the second sample. This section generates a response for a given query, decodes the relevant part, and appends it to the `response_tensors` list.
# 

# In[54]:


query=query_tensors[1]
gen_len = output_length_sampler()
generation_kwargs["max_new_tokens"] = gen_len
response = ppo_trainer.generate(query, **generation_kwargs)
tokenizer.decode(response.squeeze()[-gen_len:], skip_special_tokens=True)
print("query:",get_text(query))
print("response ouput :", get_text(response_tensors))
response_tensors.append(response.squeeze()[-gen_len:])
print("newly generated tokens form response:", get_text(response_tensors[-gen_len:]))


# Convert each tensor in `response_tensors` into human-readable text and store it in the `batch` dictionary under the key `response`.
# 

# In[55]:


batch["response"] = [tokenizer.decode(r.squeeze()) for r in response_tensors]
print(batch["response"])


# The batch now contains both `response` and `query` keys.
# 

# In[56]:


print(batch)


# ### Scoring function 
# 
# Next, prepare the text data for sentiment analysis, which can be a part of a reward function in a PPO setup where the sentiment analysis of interactions helps determine the reward.
# 
# Now, extract the `query` and `response` tensors and add them to the batch.
# 

# In[57]:


texts = [q + r for q, r in zip(batch["query"], batch["response"])]
print(texts)


# The sentiment scores (`pipe_outputs`) can be used as feedback to update the policy
# 

# In[58]:


pipe_outputs = sentiment_pipe(texts, **sent_kwargs)
print(pipe_outputs)


# These scores can be used to evaluate the quality or relevance of the generated responses, indicating the model's confidence in the likelihood of the responses being positive. The scores for the generated responses are extracted from the `pipe_outputs` list. Each element in `pipe_outputs` contains a list of scores corresponding to the model's output.
# 

# This line iterates over the `pipe_outputs` list, extracts the score from each output, converts it into a tensor, and stores it in the `rewards` list. The scores represent the model's confidence in the likelihood of the responses being positive sentences.
# 

# In[59]:


positive_scores = [
    item["score"]
    for output in pipe_outputs
    for item in output
    if item["label"] == "POSITIVE"
]
rewards = [torch.tensor(score) for score in positive_scores]
print(rewards)


# ### Proximal policy optimization 
# 
# The training loop is responsible for performing a single update step of the PPO algorithm. The inputs to this process are the query, response, and score tensors.
# 

# In[60]:


print("query:", get_text(query_tensors))
print("\n")
print("response:", get_text(response_tensors))


# To meet the PPO trainer's minimum batch size requirement of 128, you can pad the response tensors with additional sample.
# 

# In[61]:


batch_size=128
pad_token_id = tokenizer.pad_token_id

query_tensors = pad_list_to_batch_size(query_tensors, batch_size, pad_token_id)

response_tensors = pad_list_to_batch_size(response_tensors, batch_size, pad_token_id)
rewards=rewards+[torch.tensor(0) for _ in range(batch_size-len(rewards))]


# Now, call the PPO `step` method that updates the model using the PPO algorithm with `query_tensors`, `response_tensors`, and `rewards`.
# 
# - It uses these inputs to calculate the policy and value function losses.
# - It computes the gradients and updates the policy network parameters to improve the policy.
# - It ensures that the policy update stays within a certain range to avoid large policy shifts, which is a core aspect of PPO.
# 

# *Note: The following code is commented out to prevent the kernel from crashing due to the absence of a GPU in the current environment. To execute this code, please download the notebook and run it in an environment equipped with a GPU. Simply uncomment the code before running it.*
# 

# In[62]:


# stats = ppo_trainer.step(query_tensors, response_tensors, rewards)


# The `stats` variable is a dictionary containing various statistics from the PPO training step. You can print out its keys using the function `print_ppo_stats`. These keys can be organized into two main categories:
# 
# - **Minimizing the language model loss**: `related_to_objective=True`
#   - This includes statistics related to optimizing the model parameters, such as policy loss and value loss.
# 
# - **Calculating the reward**:
#   - This involves metrics more relevant to reinforcement learning, such as advantage estimates and reward calculations.
# 

# In[63]:


# stats.keys()


# In[64]:


# print_ppo_stats(stats, related_to_objective = True)


# In[65]:


# print_ppo_stats(stats)


# In[66]:


all_stats = []


# The `sentiment`should be set to NEGATIVE for bad responses and POSITIVE for good responses score .
# 

# In[67]:


sentiment = "POSITIVE"


# <!-- ### Training Loop for PPO with Sentiment Analysis -->
# 
# This code snippet represents a training loop for the PPO (Proximal Policy Optimization) algorithm using sentiment analysis. The loop iterates over batches of data from the `ppo_trainer` dataloader and performs the following steps:
# 
# 1. **Extract query tensors**:
#     - The input IDs (query tensors) are extracted from the batch.
# 
# 2. **Generate responses**:
#     - For each query tensor, a response is generated using the `ppo_trainer.generate` method with the specified `generation_kwargs`.
#     - The responses are then decoded and added to the batch under the `response` key.
# 
# 3. **Compute sentiment scores**:
#     - Text data is prepared by concatenating queries and responses.
#     - Sentiment analysis is performed on the combined texts to compute the sentiment scores.
#     - The scores are converted into tensors and stored in the `rewards` list.
# 
# 4. **Run PPO step**:
#     - The `ppo_trainer.step` method is called to update the model using the PPO algorithm with the `query_tensors`, `response_tensors`, and `rewards`.
#     - This step calculates the policy and value function losses, computes gradients and updates the policy network parameters.
#     - The policy update ensures it stays within a certain range to avoid large policy shifts.
# 
# 5. **Logging statistics**:
#     - The statistics from the PPO training step are logged and stored in the `all_stats` list.
#   
# **Note:** Training the model on a CPU will be very time-consuming. You have pretrained the model using a GPU and saved it for your convenience. You can skip the training part and proceed to the next block of code and load the saved model. You can uncomment the below block of code to train the model yourself.
# 

# In[68]:


# for epoch, batch in tqdm(enumerate(ppo_trainer.dataloader)):
#     query_tensors = batch["input_ids"]
#     print(f"epoch {epoch}")

#     #### Get response from gpt2
#     response_tensors = []
#     for query in query_tensors:
#         gen_len = output_length_sampler()
#         generation_kwargs["max_new_tokens"] = gen_len
#         response = ppo_trainer.generate(query, **generation_kwargs)
#         response_tensors.append(response.squeeze()[-gen_len:])
#     batch["response"] = [tokenizer.decode(r.squeeze()) for r in response_tensors]

#     #### Compute sentiment score
#     texts = [q + r for q, r in zip(batch["query"], batch["response"])]
#     pipe_outputs = sentiment_pipe(texts, **sent_kwargs)
#     positive_scores = [
#            item["score"]
#            for output in pipe_outputs
#            for item in output
#            if item["label"] == sentiment
#        ]
#    rewards = [torch.tensor(score) for score in positive_scores]

#     #### Run PPO step
#     stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
#     ppo_trainer.log_stats(stats, batch, rewards)
    
#     all_stats.append(stats)


# In[69]:


# # Save the model

# model_dir = "ppo-good"
# os.makedirs(model_dir, exist_ok=True)

# # Save model configuration and weights
# model_1.save_pretrained(model_dir)
# tokenizer.save_pretrained(model_dir)


# In[70]:


#get_ipython().system('wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/gSWo8GeztngSmzHpqX_RaQ/ppo-good.pkl')
import requests
import os

file_path = 'ppo-good.pkl'
if os.path.exists(file_path):
    print(file_path,"file already present")
else:
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/gSWo8GeztngSmzHpqX_RaQ/ppo-good.pkl"
    response = requests.get(url)

    # Vérifier si le téléchargement a réussi
    if response.status_code == 200:
        with open('ppo-good.pkl', 'wb') as f:
            f.write(response.content)
        print("Téléchargement réussi !")
    else:
        print(f"Erreur de téléchargement : {response.status_code}")

#get_ipython().system('wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/we8t5N-45dVq3VhxGwYRAg/ppo-good-tar.gz')
file_path = 'ppo-good-tar.gz'
if os.path.exists(file_path):
    print(file_path,"file already present")
else:
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/we8t5N-45dVq3VhxGwYRAg/ppo-good-tar.gz"
    response = requests.get(url)

    # Vérifier si le téléchargement a réussi
    if response.status_code == 200:
        with open('ppo-good-tar.gz', 'wb') as f:
            f.write(response.content)
        print("Téléchargement réussi !")
    else:
        print(f"Erreur de téléchargement : {response.status_code}")
# In[71]:


# File name
file_name = "ppo-good-tar.gz"

# Open the tar.gz file
with tarfile.open(file_name, "r:gz") as tar:
    # Extract all the contents into the current directory
    tar.extractall()

print("Extraction completed.")


# In[72]:


model_dir = "ppov3new1"
model_1 = AutoModelForCausalLMWithValueHead.from_pretrained(model_dir)
tokenizer = AutoTokenizer.from_pretrained(model_dir)

# Load training stats
file_name = "ppo-good.pkl"
with open(file_name, 'rb') as f:
    all_stats = pickle.load(f)

model_1.to(device)


# >Note: You can safely ignore the above warning.
# 

# ## Plotting PPO training loss and mean 
# 
# 1. **Extracting values**:
#     - `loss_values`: Total loss values from `all_stats`.
#     - `reward_values`: Mean reward values from `all_stats`.
# 
# 2. **Plotting the loss**:
#     - Line plot of total loss over epochs.
# 
# 3. **Plotting the rewards**:
#     - Line plot of mean reward over epochs.
# 
# 4. **Displaying the plots**:
#     - Arrange and show the plots using `plt.tight_layout()` and `plt.show()`.
# 

# In[73]:


loss_values = [stat['ppo/loss/total'] for stat in all_stats]
reward_values = [stat['ppo/mean_scores'] for stat in all_stats]

# Plotting the loss
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(loss_values, label='Total Loss', color='b')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('PPO Training Loss over Time')
plt.legend()
plt.grid(True)

# Plotting the rewards
plt.subplot(2, 1, 2)
plt.plot(reward_values, label='Mean Reward', color='g')
plt.xlabel('Epoch')
plt.ylabel('Reward')
plt.title('PPO Mean Reward over Time')
plt.legend()
plt.grid(True)

# Show the plots
plt.tight_layout()
plt.show()    


# ## Generating and analyzing text with PPO and reference models
# **Device Setup**:
#     - Determine if CUDA is available and set the device accordingly.
# 

# In[74]:


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Set the pipeline device
pipeline_device = 0 if device.type == "cuda" else -1


# **Text generation function**:
#     - `generate_some_text(input_text, my_model)`: Tokenizes input text, generates a response, and decodes it.
# 

# In[75]:


gen_kwargs = {"min_length": -1, "max_new_tokens":20, "top_k": 0.0, "top_p": 1.0, "do_sample": True, "pad_token_id": tokenizer.eos_token_id}
def generate_some_text(input_text,my_model):
# Tokenize the input text
    input_ids = tokenizer(input_text, return_tensors='pt').input_ids.to(device)
    generated_ids = my_model.generate(input_ids,**gen_kwargs )

    # Decode the generated text
    generated_text_ = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

    return generated_text_


# **Generate text with PPO model**:
#     - Generate text using the PPO-trained model.
# 

# In[76]:


input_text = "Once upon a time in a land far"

generated_text=generate_some_text(input_text,model_1)
print(generated_text)


# **Sentiment Analysis**:
#     - Analyze the sentiment of the generated text using `sentiment_pipe`.
# 

# In[77]:


pipe_outputs = sentiment_pipe(generated_text, **sent_kwargs)
print(pipe_outputs)


# **Generate text with reference model**:
#     - Generate text using the reference model.
# 

# In[78]:


generated_text = generate_some_text(input_text,ref_model)
print(generated_text)


# ## Comparing PPO and reference models on 
# 
# 1. **Generation Parameters**:
#     - Define `gen_kwargs` for text generation.
# 
# 2. **Prepare Batch**:
#     - Sample a batch of size `bs` from the dataset and extract query tensors.
# 
# 3. **Generate Responses**:
#     - For each query tensor, generate responses using both the reference model and the PPO model.
# 
# 4. **Decode Responses**:
#     - Decode the generated response tensors into human-readable text.
# 
# 5. **Compute Sentiment Scores**:
#     - Prepare texts by concatenating queries and responses.
#     - Compute sentiment scores for the responses before and after training using `sentiment_pipe`.
# 
# 6. **Store Results**:
#     - Store queries, responses, and sentiment scores in `game_data`.
#     - Convert `game_data` into a DataFrame and return it.
# 

# In[79]:


def compare_models_on_dataset(model, ref_model, dataset, tokenizer, sentiment_pipe, sent_kwargs, device, output_length_sampler):
    gen_kwargs = {
        "min_length": -1, 
        "top_k": 0.0, 
        "top_p": 1.0, 
        "do_sample": True, 
        "pad_token_id": tokenizer.eos_token_id
    }
    
    bs = 16
    game_data = dict()
    dataset.set_format("pandas")
    df_batch = dataset[:].sample(bs)
    game_data["query"] = df_batch["query"].tolist()
    query_tensors = df_batch["input_ids"].tolist()

    response_tensors_ref, response_tensors = [], []

    # Get maximum position embeddings for both models
    max_position_embeddings_ref = ref_model.config.max_position_embeddings
    max_position_embeddings_model = model.config.max_position_embeddings

    for i in range(bs):
        gen_len = output_length_sampler()

        # Convert query tensors to input IDs
        input_ids = torch.tensor(query_tensors[i]).unsqueeze(dim=0).to(device)

        # ********** Process for ref_model **********
        total_length_ref = input_ids.shape[-1] + gen_len
        if total_length_ref > max_position_embeddings_ref:
            # Truncate input_ids to fit within the max length
            max_input_length_ref = max_position_embeddings_ref - gen_len
            input_ids_ref = input_ids[:, -max_input_length_ref:]
            total_length_ref = input_ids_ref.shape[-1] + gen_len
        else:
            input_ids_ref = input_ids
        
        output = ref_model.generate(
            torch.tensor(query_tensors[i]).unsqueeze(dim=0).to(device), 
            max_new_tokens=gen_len, 
            **gen_kwargs
        ).squeeze()[-gen_len:]
        response_tensors_ref.append(output)

        # ********** Process for model **********
        total_length_model = input_ids.shape[-1] + gen_len
        if total_length_model > max_position_embeddings_model:
            max_input_length_model = max_position_embeddings_model - gen_len
            input_ids_model = input_ids[:, -max_input_length_model:]
            total_length_model = input_ids_model.shape[-1] + gen_len
        else:
            input_ids_model = input_ids
        
        output = model.generate(
            torch.tensor(query_tensors[i]).unsqueeze(dim=0).to(device), 
            max_new_tokens=gen_len, 
            **gen_kwargs
        ).squeeze()[-gen_len:]
        response_tensors.append(output)

    game_data["response (before)"] = [tokenizer.decode(response_tensors_ref[i]) for i in range(bs)]
    game_data["response (after)"] = [tokenizer.decode(response_tensors[i]) for i in range(bs)]

    texts_before = [q + r for q, r in zip(game_data["query"], game_data["response (before)"])]
    game_data["rewards (before)"] = [output[1]["score"] for output in sentiment_pipe(texts_before, **sent_kwargs)]

    texts_after = [q + r for q, r in zip(game_data["query"], game_data["response (after)"])]
    game_data["rewards (after)"] = [output[1]["score"] for output in sentiment_pipe(texts_after, **sent_kwargs)]

    df_results = pd.DataFrame(game_data)
    return df_results


# In[80]:


df_results = compare_models_on_dataset(model_1, ref_model, dataset, tokenizer, sentiment_pipe, sent_kwargs, device, output_length_sampler)
print(df_results)


# ### Running the PPO model with negative sentiment
# 
# This code runs the PPO training loop with the sentiment set to NEGATIVE, which evaluates the model's performance when negative sentiment scores are prioritized. The training loop generates responses, computes sentiment scores, updates the model, and logs the statistics for each epoch.
# 

# In[81]:


sentiment = "NEGATIVE"


# In[82]:


# for epoch, batch in tqdm(enumerate(ppo_trainer.dataloader)):
#     query_tensors = batch["input_ids"]
#     print(f"epoch {epoch}")

#     #### Get response from gpt2
#     response_tensors = []
#     for query in query_tensors:
#         gen_len = output_length_sampler()
#         generation_kwargs["max_new_tokens"] = gen_len
#         response = ppo_trainer.generate(query, **generation_kwargs)
#         response_tensors.append(response.squeeze()[-gen_len:])
#     batch["response"] = [tokenizer.decode(r.squeeze()) for r in response_tensors]

#     #### Compute sentiment score
#     texts = [q + r for q, r in zip(batch["query"], batch["response"])]
#     pipe_outputs = sentiment_pipe(texts, **sent_kwargs)
#     negative_scores = [
#            item["score"]
#            for output in pipe_outputs
#            for item in output
#            if item["label"] == sentiment
#        ]
#    rewards = [torch.tensor(score) for score in negative_scores]

#     #### Run PPO step
#     stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
#     ppo_trainer.log_stats(stats, batch, rewards)
    
#     all_stats.append(stats)


# In[83]:


# # Save the model

# model_dir = "ppo-bad"
# os.makedirs(model_dir, exist_ok=True)

# # Save model configuration and weights
# model_0.save_pretrained(model_dir)
# tokenizer.save_pretrained(model_dir)


# **Note:** Training the model on a CPU will be very time-consuming. The model has been pretrained using a GPU and saved for your convenience. You can skip the training part, proceed to the next block of code, and load the saved model. You can also uncomment the above training block of code to train the model yourself.
# 

# In[84]:


#get_ipython().system('wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/8zCp__SHRSgGVlf5yP50Ag/ppo-bad-tar.gz')
file_path = "ppo-bad-tar.gz"
if os.path.exists(file_path):
    print(file_path,"file already present")
else:
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/8zCp__SHRSgGVlf5yP50Ag/ppo-bad-tar.gz"
    response = requests.get(url)

    # Vérifier si le téléchargement a réussi
    if response.status_code == 200:
        with open('ppo-bad-tar.gz', 'wb') as f:
            f.write(response.content)
        print("Téléchargement réussi !")
    else:
        print(f"Erreur de téléchargement : {response.status_code}")

#get_ipython().system('wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/jMW99Z9mvxesgYR-H6y6Yw/ppo-bad.pkl')
file_path = "ppo-bad.pkl"
if os.path.exists(file_path):
    print(file_path,"file already present")
else:
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/jMW99Z9mvxesgYR-H6y6Yw/ppo-bad.pkl"
    response = requests.get(url)

    # Vérifier si le téléchargement a réussi
    if response.status_code == 200:
        with open('ppo-bad.pkl', 'wb') as f:
            f.write(response.content)
        print("Téléchargement réussi !")
    else:
        print(f"Erreur de téléchargement : {response.status_code}")

# In[85]:


import tarfile
# File name
file_name = "ppo-bad-tar.gz"

# Open the tar.gz file
with tarfile.open(file_name, "r:gz") as tar:
    # Extract all the contents into the current directory
    tar.extractall()

print("Extraction completed.")


# In[86]:


import tarfile
model_dir = "ppov3new_bad1"
model_0 = AutoModelForCausalLMWithValueHead.from_pretrained(model_dir)
tokenizer = AutoTokenizer.from_pretrained(model_dir)

# Load training stats
file_name = "ppo-bad.pkl"
with open(file_name, 'rb') as f:
    all_stats = pickle.load(f)

model_0.to(device)


# >Note: You can safely ignore the above warning.
# 

# ### Comparing models with negative sentiment
# 
# The below code compares the performance of the PPO-trained model (`model_0`) and the reference model on the given dataset. The `compare_models_on_dataset` function generates responses from both models, computes their sentiment scores, and returns the results in a DataFrame (`df_results`). This comparison helps evaluate how well the PPO-trained model performs in generating positive responses when the `sentiment` is set to NEGATIVE.
# 
# Since the dataset is fairly large, we will only use a subset of the dataset for testing.
# 

# In[87]:


df_results = compare_models_on_dataset(model_0, ref_model, dataset, tokenizer, sentiment_pipe, sent_kwargs, device, output_length_sampler)
print(df_results)


# ### Exercise: Comparing PPO models
# 
# In this exercise, you will compare the performance of two PPO-trained models (`model_0` and `model_1`) using the `compare_models_on_dataset` function and note the difference in performance of both.
# 
# **Compare Models**:
#    - Use the `compare_models_on_dataset` function to compare `model_0` and `model_1`.
# 

# In[88]:


# Write your code here
df_results = compare_models_on_dataset(model_0, model_1, dataset, tokenizer, sentiment_pipe, sent_kwargs, device, output_length_sampler)
print(df_results)


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# df_results = compare_models_on_dataset(model_0, model_1, dataset, tokenizer, sentiment_pipe, sent_kwargs, device, output_length_sampler)
# df_results
# ```
# 
# </details>
# 

# ## Authors
# 
# [Joseph Santarcangelo](https://author.skills.network/instructors/joseph_santarcangelo) has a Ph.D. in Electrical Engineering, his research focused on using machine learning, signal processing, and computer vision to determine how videos impact human cognition. Joseph has been working for IBM since he completed his PhD.
# 
# [Ashutosh Sagar](https://www.linkedin.com/in/ashutoshsagar/) is completing his MS in CS from Dalhousie University. He has previous experience working with Natural Language Processing and as a Data Scientist.
# 

# ## Contributors
# 
# [Hailey Quach](https://author.skills.network/instructors/hailey_quach) is a Data Scientist at IBM. She's completing her Bsc, Honors in Computer Science at Concordia University, Montreal.
# 

# ## References
# 
# 
# [TEXT CLASSIFICATION WITH THE TORCHTEXT LIBRARY](https://pytorch.org/tutorials/beginner/text_sentiment_ngrams_tutorial.html)
# 
# [Parameter-Efficient Transfer Learning for NLP](https://arxiv.org/pdf/1902.00751.pdf)
# 
# [Simple, Scalable Adaptation for Neural Machine Translation](https://arxiv.org/pdf/1909.08478)
# 

# ```{## Change Log}
# ```
# 

# ```{|Date (YYYY-MM-DD)|Version|Changed By|Change Description||-|-|-|-||2024-06-27|0.1|Kang Wang|Create the lab|}
# ```
# 

# © Copyright IBM Corporation. All rights reserved.
# 

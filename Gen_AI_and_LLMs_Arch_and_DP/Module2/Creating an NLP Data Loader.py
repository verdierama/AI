# jupyter nbconvert --to script "Creating an NLP Data Loader.ipynb"
#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo">
#     </a>
# </p>
# 

# # Creating an NLP Data Loader 
# 

# Estimated time needed: **60** minutes
# 

# As an AI engineer working on a cutting-edge language translation project, you are tasked with bridging the communication gap between speakers of different languages. Translating languages is no small feat, especially given the intricacies, nuances, and cultural contexts embedded within them. Central to the success of this endeavor is the data - large corpora of bilingual sentences that serve as the bedrock of your models.
# 
# ![Sample Image](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-AI0205EN-SkillsNetwork/Screenshot%202023-10-24%20at%209.54.36%E2%80%AFAM.png)
# In PyTorch, the data loader plays an indispensable role in managing this vast amount of data. For natural language processing (NLP) tasks like yours, data often comes in variable lengths due to differing sentence structures and lengths across languages. The data loader efficiently batches these variable-length sequences, ensuring that your models are trained on diverse examples in every iteration. This batching is crucial for harnessing the power of parallel computation on GPUs, thus expediting the training process.
# 
# Furthermore, the data loader aids in shuffling the data set, which is vital for preventing models from memorizing the sequence of training data and promoting better generalization. Especially for NLP tasks, where data might be ordered or clustered by topics, shuffling ensures that the model remains robust and doesn't develop biases based on the order of input.
# 
# Lastly, in the world of NLP, preprocessing steps such as tokenization, padding, and numericalization are paramount. The data loader in PyTorch provides hooks that allow us to seamlessly integrate these preprocessing steps, ensuring that the raw textual data is transformed into a format that's amenable for deep learning models.
# In PyTorch, the data loader plays an indispensable role in managing this vast amount of data.
# 
# In this lab, you will cover the whole process of loading and collating text data using PyTorch.
# 
# 

# # __Table of Contents__
# 
# <ol>
#     <li>
#         <a href="#Setup">Setup</a>
#         <ol>
#             <li><a href="#Installing-required-libraries">Installing required libraries</a></li>
#             <li><a href="#Importing-required-libraries">Importing required libraries</a></li>
#         </ol>
#     </li>
#     <li>
#         <a href="#Data-set">Data set</a>
#         <ol>
#             <li><a href="#Data-loader">Data loader</a></li>
#         </ol>
#     </li>
#     <li><a href="#Custom-data-set-and-data-loader-in-PyTorch">Custom data set and data loader in PyTorch</a>
#         <ol>
#             <li><a href="#Creating-tensors-for-custom-data-set">Creating tensors for custom data set</a></li>
#             <li><a href="#Custom-collate-function">Custom collate function</a></li>
#         </ol>
#     </li>
#     <li><a href="#Exercise">Exercise</a>
#     </li>
#     <li><a href="#[Optional]-Data-loader-for-German-English-translation-task">[Optional] Data loader for German-English translation task</a>
#          <ol>
#             <li><a href="#Translation-data-set">Translation data set</a></li>
#             <li><a href="#Tokenizer-setup">Tokenizer setup</a></li>
#             <li><a href="#Special-symbols">Special symbols</a></li>
#             <li><a href="#Tokens-to-indices-transformation-(Vocab)">Tokens to indices transformation (Vocab)</a></li>
#         </ol>
#     </li>
#     <li><a href="#Processing-data-in-batches">Processing data in batches</a></li>
# </ol>
# 

# # Setup
# ## Installing required libraries
# 

# In[6]:


#get_ipython().system('pip install nltk')
#get_ipython().system('pip install transformers')
#get_ipython().system('pip install sentencepiece')
#get_ipython().system('pip install spacy')
#get_ipython().system('pip install numpy==1.24')
#get_ipython().system('python -m spacy download en_core_web_sm')
#get_ipython().system('python -m spacy download de_core_news_sm')
#get_ipython().system('pip install torch==2.0.1 torchtext==0.15.2')
#get_ipython().system('pip install portalocker')
#get_ipython().system('pip install numpy pandas')
#get_ipython().system('pip install numpy scikit-learn')


# You can check the installed version of each package to make sure you have set the right environment.
# 

# ## Importing required libraries
# 

# In[7]:


import torchtext
print(torchtext.__version__)


# In[8]:


import pandas as pd
from torch.utils.data import Dataset, DataLoader
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
from torchtext.datasets import multi30k, Multi30k
from typing import Iterable, List
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader
from torchdata.datapipes.iter import IterableWrapper, Mapper
import torchtext

import torch
import torch.nn as nn
import torch.optim as optim

import numpy as np
import random


# ## **Data set**
# 
# A data set in **PyTorch** is an object that represents a collection of data samples. Each data sample typically consists of one or more input features and their corresponding target labels. You can also use your data set to transform your data as needed.
# 
# ## **Data loader**
# 
# A data loader in **PyTorch** is responsible for efficiently loading and batching data from a data set. It abstracts away the process of iterating over a data set, shuffling, and dividing it into batches for training. In NLP applications, the data loader is used to process and transform your text data, rather than just the data set.
# 
# Data loaders have several key parameters, including the data set to load from, batch size (determining how many samples per batch), shuffle (whether to shuffle the data for each epoch), and more. Data loaders also provide an iterator interface, making it easy to iterate over batches of data during training.
# 
# Now, you may ask, '**What is an iterator?**'
# 
# An iterator is an object that can be looped over. It contains elements that can be iterated through and typically includes two methods, `__iter__()` and `__next__()`. When there are no more elements to iterate over, it raises a **`StopIteration`** exception.
# 
# Iterators are commonly used to traverse large data sets without loading all elements into memory simultaneously, making the process more memory-efficient. In PyTorch, not all data sets are iterators, but all data loaders are.
# 
# In PyTorch, the data loader processes data in batches, loading and processing one batch at a time into memory efficiently. The batch size, which you specify when creating the data loader, determines how many samples are processed together in each batch. The data loader's purpose is to convert input data and labels into batches of tensors with the same shape for deep learning models to interpret.
# 
# Finally, a data loader can be used for tasks such as tokenizing, sequencing, converting your samples to the same size, and transforming your data into tensors that your model can understand.
# 
# --- 
# 
# 

# ## **Custom data set and data loader in PyTorch**
# In this code snippet, you will see how to create a custom data set and use the DataLoader class in PyTorch. The data set consists of a list of random sentences, and the objective is to create batches of sentences for further processing, such as training a neural network model.
# 
# You will begin by defining a custom data set called CustomDataset. This data set inherits from the `torch.utils.data.Dataset` class and is initialized with a list of sentences. The data set comprises two essential methods:
# 
# - __init__(self, sentences): Initializes the data set with a list of sentences.
# - __getitem__(self, idx): Retrieves an item (in this case, a sentence) at a specific index, idx.
# 
# Next, you create an instance of your custom data set (custom_dataset) by passing in the list of sentences. Additionally, you can specify a batch size (batch_size), which determines how many sentences will be grouped together in each batch during data loading.
# 
# You will then create a DataLoader (dataloader) by providing your custom data set and batch size to the torch.utils.data.DataLoader class. Furthermore, you set shuffle=True, indicating that the sentences will be randomly shuffled before being divided into batches. This shuffling is particularly useful for training deep learning models, as it prevents the model from learning patterns based on the order of the data.
# 
# Finally, you iterate through the DataLoader to demonstrate how data is loaded in batches. In this code, you will see that batch size is set to 2, meaning that each batch will contain two sentences. The DataLoader efficiently manages the loading of data in batches, making it suitable for training deep learning models.
# 
# During iteration, the sentences in each batch are printed to illustrate how the DataLoader groups and presents the data. This code snippet provides a fundamental example of how to set up a custom data set and data loader in PyTorch, which is a common practice in deep learning workflows.
# 

# In[48]:


sentences = [
    "If you want to know what a man's like, take a good look at how he treats his inferiors, not his equals.",
    "Fame's a fickle friend, Harry.",
    "It is our choices, Harry, that show what we truly are, far more than our abilities.",
    "Soon we must all face the choice between what is right and what is easy.",
    "Youth can not know how age thinks and feels. But old men are guilty if they forget what it was to be young.",
    "You are awesome!"
]

# Define a custom dataset
class CustomDataset(Dataset):
    def __init__(self, sentences):
        self.sentences = sentences

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        return self.sentences[idx]

# Create an instance of your custom dataset
custom_dataset = CustomDataset(sentences)

# Define batch size
batch_size = 2

# Create a DataLoader
dataloader = DataLoader(custom_dataset, batch_size=batch_size, shuffle=True)

# Iterate through the DataLoader
for batch in dataloader:
    print(batch)


# As shown above, the data is organized into batches of 2 sentences each. It's important to note that deep learning models can only comprehend numerical data, and words are meaningless to them. Therefore, your next step is to convert these sentences into tensors. Let's see how to do this.
# 

# ### Creating tensors for custom data set
# 
# In this code example, you will see the creation of a custom data set for natural language processing (NLP) tasks using PyTorch. The data set consists of a list of sentences, and your goal is to preprocess these sentences, tokenize them, and convert them into tensors of token indices for use in NLP models. Let's break down the code step by step.
# 
# The sentences and the CustomDataset class are used in the same way as in the previous code snippet. The changes made to the CustomDataset class are as follows:
# 
# - __init__: The constructor takes a list of sentences, a tokenizer function, and a vocabulary (vocab) as input.
# - __len__: This method returns the total number of samples in the data set.
# - __getitem__: This method is responsible for processing a single sample. It tokenizes the sentence using the provided tokenizer and then converts the tokens into tensor indices using the vocabulary.
# 
# You can define a tokenizer using the `get_tokenizer` function with the `basic_english` option. Tokenization is the process of splitting a text into individual tokens or words. Next, you build a vocabulary from the sentences. You use the `build_vocab_from_iterator` function to construct the vocabulary from the tokenized sentences.
# 
# You can create an instance of your custom data set, passing in the sentences, tokenizer, and vocabulary. Finally, you print the length of the custom data set and sample items from the data set for illustration.
# 

# In[49]:


sentences = [
    "If you want to know what a man's like, take a good look at how he treats his inferiors, not his equals.",
    "Fame's a fickle friend, Harry.",
    "It is our choices, Harry, that show what we truly are, far more than our abilities.",
    "Soon we must all face the choice between what is right and what is easy.",
    "Youth can not know how age thinks and feels. But old men are guilty if they forget what it was to be young.",
    "You are awesome!"
]

# Define a custom data set
class CustomDataset(Dataset):
    def __init__(self, sentences, tokenizer, vocab):
        self.sentences = sentences
        self.tokenizer = tokenizer
        self.vocab = vocab

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        tokens = self.tokenizer(self.sentences[idx])
        # Convert tokens to tensor indices using vocab
        tensor_indices = [self.vocab[token] for token in tokens]
        return torch.tensor(tensor_indices)

# Tokenizer
tokenizer = get_tokenizer("basic_english")

# Build vocabulary
vocab = build_vocab_from_iterator(map(tokenizer, sentences))

# Create an instance of your custom data set
custom_dataset = CustomDataset(sentences, tokenizer, vocab)

print("Custom Dataset Length:", len(custom_dataset))
print("Sample Items:")
for i in range(6):
    sample_item = custom_dataset[i]
    print(f"Item {i + 1}: {sample_item}")


# Please go ahead and uncomment the following code to apply the data loader and observe the results:
# 

# In[50]:


"""
# Create an instance of your custom data set
custom_dataset = CustomDataset(sentences, tokenizer, vocab)

# Define batch size
batch_size = 2

# Create a data loader
#dataloader = DataLoader(custom_dataset, batch_size=batch_size, shuffle=True)

# Iterate through the data loader
for batch in dataloader:
    print(batch)
"""


# You will encounter an error when attempting to create batches for the tensors. This error arises because the tensor batches have unequal lengths. The data loader is using the default `collate_function`, which requires tensors to have equal lengths. You can define your own `collate_function` and pass the data into it to establish your own rules. Typically, to address the issue of unequal tensor lengths, you employ data padding. This will be demonstrated in the following section.
# 

# ### Custom collate function
# 
# A collate function is employed in the context of data loading and batching in machine learning, particularly when dealing with variable-length data, such as sequences (e.g., text, time series, sequences of events). Its primary purpose is to prepare and format individual data samples (examples) into batches that can be efficiently processed by machine learning models.
# 
# You will begin by defining a custom collate function named `collate_fn`. This function plays a crucial role when handling sequences of varying lengths, such as sentences in NLP. Its purpose is to pad sequences within a batch to have equal lengths, which is a common preprocessing step in NLP tasks.
# 
# `pad_sequence`: This function is a part of PyTorch and is utilized to pad sequences in a batch, ensuring uniform length. It takes a batch of sequences as input and pads them to match the length of the longest sequence. The `padding_value=0` argument specifies the value to use for padding.
# 

# In[51]:


# Create a custom collate function
def collate_fn(batch):
    # Pad sequences within the batch to have equal lengths
    padded_batch = pad_sequence(batch, batch_first=True, padding_value=0)
    return padded_batch


# In the above cell, when padding the sequences, you set `batch_first=True`. When `batch_first=True`, output will be in [batch_size x seq_len] shape, otherwise it will be in [seq_len x batch_size] shape. Some models accept input with [batch_size x seq_len] shape while some other models need the input to be of [seq_len x batch_size] shape. Keep in mind that this parameter takes care of putting the input in the desired shape. 
# 
# Let's see how it actually affects the shape of curated batches. First, you create a data loader from a collate function with `batch_first=True`:
# 

# In[52]:


# Create a data loader with the custom collate function with batch_first=True,
dataloader = DataLoader(custom_dataset, batch_size=batch_size, collate_fn=collate_fn)

# Iterate through the data loader
for batch in dataloader: 
    for row in batch:
        for idx in row:
            words = [vocab.get_itos()[idx] for idx in row]
        print(words)
       


# Looking into the result, you can see that the first dimension is the batch. For example, first batch is the first sentence: "['if', 'you', 'want', 'to', 'know', 'what', 'a', 'man', "'", 's', 'like', ',', 'take', 'a', 'good', 'look', 'at', 'how', 'he', 'treats', 'his', 'inferiors', ',', 'not', 'his', 'equals', '.']". 
# 
# Now, you can try `batch_first=False` which is the DEFAULT value:
# 

# In[53]:


# Create a custom collate function
def collate_fn_bfFALSE(batch):
    # Pad sequences within the batch to have equal lengths
    padded_batch = pad_sequence(batch, padding_value=0)
    return padded_batch


# Now, you look into the curated data:
# 

# In[54]:


# Create a data loader with the custom collate function with batch_first=True,
dataloader_bfFALSE = DataLoader(custom_dataset, batch_size=batch_size, collate_fn=collate_fn_bfFALSE)

# Iterate through the data loader
for seq in dataloader_bfFALSE:
    for row in seq:
        #print(row)
        words = [vocab.get_itos()[idx] for idx in row]
        print(words)


# It can be seen that the first dimension is now the sequence instead of batch, which means sentences will break so that each row includes a token from each sequence. For example the first row, (['if', 'fame']), includes the first tokens of all the sequences in that batch. You need to be aware of this standard to avoid any confusion when working with recurrent neural networks (RNNs) and transformers.
# 

# In[55]:


# Iterate through the data loader with batch_first = TRUE
for batch in dataloader:    
    print(batch)
    print("Length of sequences in the batch:",batch.shape[1])


# You will see that each batch has a fixed size for all the sequences within the batch.
# 
# You also have the option to utilize the collate function for tasks such as tokenization, converting tokenized indices, and transforming the result into a tensor. It's important to note that the original data set remains untouched by these transformations.
# 

# In[56]:


# Define a custom data set
class CustomDataset(Dataset):
    def __init__(self, sentences):
        self.sentences = sentences

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        return self.sentences[idx]


# In[57]:


custom_dataset=CustomDataset(sentences)


# You have the raw text:
# 

# In[58]:


custom_dataset[0]


# You create the new ```collate_fn```
# 

# In[59]:


def collate_fn(batch):
    # Tokenize each sample in the batch using the specified tokenizer
    tensor_batch = []
    for sample in batch:
        tokens = tokenizer(sample)
        # Convert tokens to vocabulary indices and create a tensor for each sample
        tensor_batch.append(torch.tensor([vocab[token] for token in tokens]))

    # Pad sequences within the batch to have equal lengths using pad_sequence
    # batch_first=True ensures that the tensors have shape (batch_size, max_sequence_length)
    padded_batch = pad_sequence(tensor_batch, batch_first=True)
    
    # Return the padded batch
    return padded_batch


# Create a data loader with the custom collate function.
# 

# In[60]:


# Create a data loader for the custom dataset
dataloader = DataLoader(
    dataset=custom_dataset,   # Custom PyTorch Dataset containing your data
    batch_size=batch_size,     # Number of samples in each mini-batch
    shuffle=True,              # Shuffle the data at the beginning of each epoch
    collate_fn=collate_fn      # Custom collate function for processing batches
)


# You will see that the result is a tensor of the same shape for each sample in the batch.
# 

# In[61]:


for batch in dataloader:
    print(batch)
    print("shape of sample",len(batch))


# As a result, batches of tensors with equal lengths have been successfully created.
# 

# ## Exercise
# 

# Create a data loader with a collate function that processes batches of French text (provided below). Sort the data set on sequences length. Then tokenize, numericalize and pad the sequences. Sorting the sequences will minimize the number of `<PAD>`tokens added to the sequences, which enhances the model's performance. Prepare the data in batches of size 4 and print them.
# 

# In[68]:


corpus = [
    "Ceci est une phrase.",
    "C'est un autre exemple de phrase.",
    "Voici une troisième phrase.",
    "Il fait beau aujourd'hui.",
    "J'aime beaucoup la cuisine française.",
    "Quel est ton plat préféré ?",
    "Je t'adore.",
    "Bon appétit !",
    "Je suis en train d'apprendre le français.",
    "Nous devons partir tôt demain matin.",
    "Je suis heureux.",
    "Le film était vraiment captivant !",
    "Je suis là.",
    "Je ne sais pas.",
    "Je suis fatigué après une longue journée de travail.",
    "Est-ce que tu as des projets pour le week-end ?",
    "Je vais chez le médecin cet après-midi.",
    "La musique adoucit les mœurs.",
    "Je dois acheter du pain et du lait.",
    "Il y a beaucoup de monde dans cette ville.",
    "Merci beaucoup !",
    "Au revoir !",
    "Je suis ravi de vous rencontrer enfin !",
    "Les vacances sont toujours trop courtes.",
    "Je suis en retard.",
    "Félicitations pour ton nouveau travail !",
    "Je suis désolé, je ne peux pas venir à la réunion.",
    "À quelle heure est le prochain train ?",
    "Bonjour !",
    "C'est génial !"
]
#get_ipython().system('python -m spacy download fr_core_news_sm')
tokenizer = get_tokenizer('spacy', language='fr_core_news_sm')
vocab = build_vocab_from_iterator(map(tokenizer, corpus))

sorted_data = sorted(corpus, key=lambda x: len(tokenizer(x)))
print(sorted_data)
dataloader = DataLoader(sorted_data, batch_size=4, shuffle=False, collate_fn=collate_fn)

for batch in dataloader:
    print(batch)
    print("shape of sample",len(batch))


# <details><summary>Click here for the solution</summary>
# 
# ```python
# 
# def collate_fn_fr(batch):
#     # Pad sequences within the batch to have equal lengths
#     tensor_batch=[]
#     for sample in batch:
#         tokens = tokenizer(sample)
#         tensor_batch.append(torch.tensor([vocab[token] for token in tokens]))
#          
#     padded_batch = pad_sequence(tensor_batch,batch_first=True)
#     return padded_batch
# 
# # Build tokenizer
# tokenizer = get_tokenizer('spacy', language='fr_core_news_sm')
# 
# # Build vocabulary
# vocab = build_vocab_from_iterator(map(tokenizer, corpus))
# 
# # Sort sentences based on their length
# sorted_data = sorted(corpus, key=lambda x: len(tokenizer(x)))
# #print(sorted_data)
# dataloader = DataLoader(sorted_data, batch_size=4, shuffle=False, collate_fn=collate_fn_fr)
# 
# ```
# </details>
# 
# 

# <details><summary>Click here for the solution</summary>
# 
# ```python
# for batch in dataloader:
#     print(batch)
# 
# ```
# </details>
# 

# ## [Optional] Data loader for German-English translation task
# 

# This section sets the stage for German-English machine translation using the torchtext and spaCy libraries. It adjusts data set URLs for the Multi30k data set, configures tokenizers for both languages, and establishes vocabularies with special tokens. This foundation is crucial for building and training effective translation models.
# 
# - **Data set configuration and language definition**
#   - Default URLs for the Multi30k dataset are modified to fix broken links.
#   - Source (`de` for German) and target (`en` for English) languages are defined.
# 
# - **Tokenizer setup**
#   - Tokenizers for both languages are set up using `spaCy`.
# 
# - **Token generation**
#   - A helper function, `yield_tokens`, is created to generate tokens from the data set
# 
# - **Special symbols**
#   - Special symbols (e.g., `<unk>`, `<pad>`) and their indices are defined.
# 
# - **Vocabulary building**
#   - Vocabularies for both source and target languages are built from the **training** data of the Multi30k dataset converting tokens to unique indices (numbers)
# 
# - **Default token handling**
#   - A default index (`UNK_IDX`) is set for tokens not found in the vocabulary.
# 

# ### Translation data set
# In this section, you fetch a language translation data set called Multi30k. You will modify its default training and validation URLs, and then retrieve and print the first pair of German-English sentences from the training set. First, you will override the default URLs:
# 

# In[69]:


# You would modify the URLs for the data set since the links to the original data set are broken

multi30k.URL["train"] = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-AI0205EN-SkillsNetwork/training.tar.gz"
multi30k.URL["valid"] = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-AI0205EN-SkillsNetwork/validation.tar.gz"


# Define the source language as German ('de') and target language as English ('en'). In Python, global variables are variables defined outside of a function, accessible both inside and outside of functions. They are often written in all caps as a convention to indicate they are constant, global nature and to differentiate them from regular variables.
# 

# In[70]:


SRC_LANGUAGE = 'de'
TGT_LANGUAGE = 'en'


# Initialize the training data iterator for the Multi30k dataset with the specified source and target languages:
# 

# In[71]:


train_iter = Multi30k(split='train', language_pair=(SRC_LANGUAGE, TGT_LANGUAGE))


# Create an iterator for the training data set:
# 

# In[72]:


data_set = iter(train_iter)


# You can print out the first five pairs of source and target sentences from the training data set:
# 

# In[73]:


for n in range(5):
    # Getting the next pair of source and target sentences from the training data set
    src, tgt = next(data_set)

    # Printing the source (German) and target (English) sentences
    print(f"sample {str(n+1)}")
    print(f"Source ({SRC_LANGUAGE}): {src}\nTarget ({TGT_LANGUAGE}): {tgt}")


# ### Tokenizer setup
# 
# The tokenizer, set up using spaCy, breaks down text into smaller units or tokens, facilitating precise language processing and ensuring that words and punctuations are appropriately segmented for the translation task. Let's use the following example samples:
# 

# In[74]:


german, english = next(data_set)
print(f"Source German ({SRC_LANGUAGE}): {german}\nTarget English  ({TGT_LANGUAGE}): { english }")


# Import the```get_tokenizer``` utility function from ```torchtext``` to obtain tokenizers for language processing:
# 

# In[75]:


from torchtext.data.utils import get_tokenizer


# Initialize the German and English tokenizers using spaCy's 'de_core_news_sm' model:
# 

# In[76]:


# Making a placeholder dict to store both tokenizers
token_transform = {}

token_transform[SRC_LANGUAGE] = get_tokenizer('spacy', language='de_core_news_sm')
token_transform[TGT_LANGUAGE] = get_tokenizer('spacy', language='en_core_web_sm')


# The line ```token_transform['de'](german)``` will tokenize the German string (or text) using the previously defined ```token_transform['de']``` for the German language.
# 

# In[77]:


token_transform['de'](german)


# The same thing for English:
# 

# In[78]:


token_transform['en'](english)


# ### Special symbols
# In a typical NLP  context, the tokens `['<unk>', '<pad>', '<bos>', '<eos>']` have specific meanings:
# 
# 1. `<unk>`: This token represents "unknown" or "out-of-vocabulary" words. It is used when a word in the input text is not found in the vocabulary or when dealing with words that are rare or unseen during training. When the model encounters an unknown word, it replaces it with the `<unk>` token.
# 
# 2. `<pad>`: This token represents padding. In sequences of text data, such as sentences or documents, sequences may have different lengths. To create batches of data with uniform dimensions, shorter sequences are often padded with this `<pad>` token to match the length of the longest sequence in the batch.
# 
# 3. `<bos>`: This token represents the "beginning of sequence." It is used to indicate the start of a sentence or sequence of tokens. It helps the model understand the beginning of a text sequence.
# 
# 4. `<eos>`: This token represents the "end of sequence." It is used to indicate the end of a sentence or sequence of tokens. It helps the model recognize the end of a text sequence.
# 
#  Define special symbols and indices
# 

# In[79]:


# Define special symbols and indices
UNK_IDX, PAD_IDX, BOS_IDX, EOS_IDX = 0, 1, 2, 3
# Make sure the tokens are in order of their indices to properly insert them in vocab
special_symbols = ['<unk>', '<pad>', '<bos>', '<eos>']


# ## Tokens to indices transformation (Vocab)
# The code initializes a dictionary vocab_transform and then builds vocabularies for both German (de) and English (en) languages from the ```train_iter dataset``` using the helper ```function yield_tokens```. These vocabularies are then stored in the vocab_transform dictionary. The vocabularies are built with certain constraints like a minimum frequency for tokens and the inclusion of special symbols at the beginning.
# 
# Initialize a dictionary to store vocabularies for the two languages:
# 

# In[80]:


#place holder dict for 'en' and 'de' vocab transforms
vocab_transform = {}


# You will create a yield_tokens function that processes a given data set iterator (data_iter), and for each sample, tokenizes the data for the specified language (language). It uses a predefined mapping (token_transform) of languages to their corresponding tokenizers.
# 

# In[81]:


def yield_tokens(data_iter: Iterable, language: str) -> List[str]:
    # Define a mapping to associate the source and target languages
    # with their respective positions in the data samples.
    language_index = {SRC_LANGUAGE: 0, TGT_LANGUAGE: 1}

    # Iterate over each data sample in the provided dataset iterator
    for data_sample in data_iter:
        # Tokenize the data sample corresponding to the specified language
        # and yield the resulting tokens.
        yield token_transform[language](data_sample[language_index[language]])


# You build and store the German and English vocabularies from the **training** data set only. You can use the helper function ```yield_tokens``` to tokenize data. Include tokens that appear at least once (min_freq=1) and add special symbols (like <pad>, <unk>, etc.) at the beginning of the vocabulary:
# 

# In[82]:


for ln in [SRC_LANGUAGE, TGT_LANGUAGE]:
    # Training data iterator
    train_iterator = Multi30k(split='train', language_pair=(SRC_LANGUAGE, TGT_LANGUAGE))
    #To decrease the number of padding tokens, you sort data on the source length to batch similar-length sequences together
    sorted_dataset = sorted(train_iterator, key=lambda x: len(x[0].split()))
    # Create torchtext's Vocab object
    vocab_transform[ln] = build_vocab_from_iterator(yield_tokens(sorted_dataset, ln),
                                                    min_freq=1,
                                                    specials=special_symbols,
                                                    special_first=True)


#  Set ```UNK_IDX``` as the default index. This index is returned when the token is not found.
# 

# In[83]:


# If not set, it throws ``RuntimeError`` when the queried token is not found in the Vocabulary.
for ln in [SRC_LANGUAGE, TGT_LANGUAGE]:
  vocab_transform[ln].set_default_index(UNK_IDX)


# You take the  English/German text string, tokenize it into words or subwords, and then convert these tokens into their corresponding indices from the vocabulary, resulting in a sequence of integers seq_en that can be used for further processing in a model.
# 

# In[84]:


seq_en=vocab_transform['en'](token_transform['en'](english))
print(f"English text string: {english}\n English sequence: {seq_en}")

seq_de=vocab_transform['de'](token_transform['de'](german))
print(f"German text string: {german}\n German sequence: {seq_de}")


# In[85]:


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ```tensor_transform_s``` function adds a beginning-of-sequence (BOS) token at the start, flips the sequence to reverse the order of token IDs and adds an end-of-sequence (EOS) token at the end of a given sequence of token IDs, then returns the concatenated result as a PyTorch tensor, this will be used as an input to our model:
# 
# ```tensor_transform_t``` function does the similar operations except the flip operation. It is a good practice to reverse the order of source sentence in order for the LSTM to perform better.
# 

# In[86]:


# function to add BOS/EOS, flip source sentence and create tensor for input sequence indices
def tensor_transform_s(token_ids: List[int]):
    return torch.cat((torch.tensor([BOS_IDX]),
                      torch.flip(torch.tensor(token_ids), dims=(0,)),
                      torch.tensor([EOS_IDX])))

# function to add BOS/EOS and create tensor for input sequence indices
def tensor_transform_t(token_ids: List[int]):
    return torch.cat((torch.tensor([BOS_IDX]),
                      torch.tensor(token_ids),
                      torch.tensor([EOS_IDX])))


# In[87]:


seq_en=tensor_transform_s(seq_en)
seq_en


# In[88]:


seq_de=tensor_transform_t(seq_de)
seq_de


# Now that you have defined the transform function, you create a ```sequestial_transforms``` function to put all the transformations together in the correct order.
# 
# 

# In[89]:


# helper function to club together sequential operations
def sequential_transforms(*transforms):
    def func(txt_input):
        for transform in transforms:
            txt_input = transform(txt_input)
        return txt_input
    return func

# ``src`` and ``tgt`` language text transforms to convert raw strings into tensors indices
text_transform = {}

text_transform[SRC_LANGUAGE] = sequential_transforms(token_transform[SRC_LANGUAGE], #Tokenization
                                            vocab_transform[SRC_LANGUAGE], #Numericalization
                                            tensor_transform_s) # Add BOS/EOS and create tensor

text_transform[TGT_LANGUAGE] = sequential_transforms(token_transform[TGT_LANGUAGE], #Tokenization
                                            vocab_transform[TGT_LANGUAGE], #Numericalization
                                            tensor_transform_t) # Add BOS/EOS and create tensor


# ## Processing data in batches
# The collate_fn function builds upon the utilities you established earlier. It performs the text_transform to a batch of raw data. Furthermore, it ensures consistent sequence lengths within the batch through padding. This transformation readies the data for input to a transformer model designed for language translation tasks.
# 

# In[90]:


# function to collate data samples into batch tensors
def collate_fn(batch):
    src_batch, tgt_batch = [], []
    for src_sample, tgt_sample in batch:
        src_sequences = text_transform[SRC_LANGUAGE](src_sample.rstrip("\n"))
        src_sequences = torch.tensor(src_sequences, dtype=torch.int64)
        tgt_sequences = text_transform[TGT_LANGUAGE](tgt_sample.rstrip("\n"))
        tgt_sequences = torch.tensor(tgt_sequences, dtype=torch.int64)
        src_batch.append(src_sequences)
        tgt_batch.append(tgt_sequences)

    src_batch = pad_sequence(src_batch, padding_value=PAD_IDX,batch_first=True)
    tgt_batch = pad_sequence(tgt_batch, padding_value=PAD_IDX,batch_first=True)
    
    return src_batch.to(device), tgt_batch.to(device)


# You establish a training data iterator using the Multi30k data set and configure a data loader with a batch size of 4. This leverages the predefined collate_fn to efficiently curate and ready batches for training your transformer model. Your primary aim is to delve deeper into the intricacies of the RNN encoder and decoder components.
# 

# In[91]:


BATCH_SIZE = 4

train_iterator = Multi30k(split='train', language_pair=(SRC_LANGUAGE, TGT_LANGUAGE))
sorted_train_iterator = sorted(train_iterator, key=lambda x: len(x[0].split()))
train_dataloader = DataLoader(sorted_train_iterator, batch_size=BATCH_SIZE, collate_fn=collate_fn,drop_last=True)

valid_iterator = Multi30k(split='valid', language_pair=(SRC_LANGUAGE, TGT_LANGUAGE))
sorted_valid_dataloader = sorted(valid_iterator, key=lambda x: len(x[0].split()))
valid_dataloader = DataLoader(sorted_valid_dataloader, batch_size=BATCH_SIZE, collate_fn=collate_fn,drop_last=True)


src, trg = next(iter(train_dataloader))
src,trg


# # Congratulations! You have completed the lab.
# 

# ## Authors
# 

# [Joseph Santarcangelo](https://www.linkedin.com/in/joseph-s-50398b136/) has a Ph.D. in Electrical Engineering, his research focused on using machine learning, signal processing, and computer vision to determine how videos impact human cognition. Joseph has been working for IBM since he completed his PhD.
# 
# [Roodra Kanwar](https://www.linkedin.com/in/roodrakanwar/) is completing his MS in CS specializing in big data from Simon Fraser University. He has previous experience working with machine learning and as a data engineer.
# 
# [Fateme Akbari](https://www.linkedin.com/in/fatemeakbari/) is a PhD candidate in Information Systems at McMaster University with demonstrated research experience in Machine Learning and NLP.
# 

# 
# © Copyright IBM Corporation. All rights reserved.
# 

# ```{## Change Log}
# ```
# 

# ```{|Date (YYYY-MM-DD)|Version|Changed By|Change Description|}
# ```
# ```{|-|-|-|-|}
# ```
# ```{|2023-10-24|0.1|Roodra|Created Lab Template|}
# ```
# 

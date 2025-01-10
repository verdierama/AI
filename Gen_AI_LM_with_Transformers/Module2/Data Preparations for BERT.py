#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo"  />
#     </a>
# </p>
# 

# # **Data Loading and Text Processing for BERT**
# 

# Estimated time needed: **45** minutes
# (When using the pre-trained model provided)
# 

# In this hands-on lab, you will learn essential techniques and steps to prepare your data for training BERT models effectively. BERT (Bidirectional Encoder Representations from Transformers) has revolutionized natural language processing tasks by capturing contextual information from both left and right contexts. To harness the power of BERT, you will cover various topics, including random sample selection, tokenization, vocabulary building, text masking, and data preparation for masked language model (MLM) and next sentence prediction (NSP) tasks. By the end of this project, you will have the skills to preprocess your data and create training-ready inputs for BERT models. Let's dive in and get started!
# 

# ## __Table of contents__
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
#     <li>
#         <a href="#Tokenization-and-vocabulary-building">Tokenization and vocabulary building</a>
#         <ol>
#             <li><a href="#Tokenization">Tokenization</a></li>
#             <li><a href="#Vocabulary-building">Vocabulary building</a></li>
#         </ol>
#     </li>
#     <li>
#         <a href="#Text-masking-and-data-preparation-for-BERT">Text masking and data preparation for BERT</a>
#         <ol>
#             <li><a href="#Text-masking">Text masking</a></li>
#             <li><a href="#Data-preparation-for-MLM">Data preparation for MLM</a></li>
#             <li><a href="#Data-preparation-for-NSP">Data preparation for NSP</a></li>
#             <li><a href="#Finalizing-BERT-inputs">Finalizing BERT inputs</a></li>
#         </ol>
#     </li>
#     <li>
#         <a href="#Preparing-the-dataset">Preparing the dataset</a>
#     </li>
#     <li>
#         <a href="#Exercises">Exercises</a>
#         <ol>
#             <li><a href="#Exercise-1---Initializing-the-BERTTokenizer">Exercise 1 - Initializing the BERTTokenizer</a></li>
#             <li><a href="#Exercise-2---Tokenizing-the-dataset">Exercise 2 - Tokenizing the dataset</a></li>
#             <li><a href="#Exercise-3---Building-the-vocabulary-with-special-tokens">Exercise 3 - Building the vocabulary with special tokens</a></li>
#         </ol>
#     </li>
# </ol>
# 

# ## Objectives
# 
# After completing this lab, you will be able to:
# 
# - Understand the process of random sample selection and tokenization
# - Apply tokenization techniques and build a vocabulary for text processing
# - Implement text masking and prepare data specifically for BERT models
# - Gain proficiency in text masking to create masked language model (MLM) training data
# - Prepare data for next sentence prediction (NSP) training
# 

# ----
# 

# ## Setup
# 

# ### Installing required libraries
# 
# The following required libraries are __not__ pre-installed in the Skills Network Labs environment. __You will need to run the following cell__ to install them:
# 

# In[1]:


#get_ipython().system(" pip install 'portalocker>=2.0.0'")
#get_ipython().system(" pip install 'torchtext==0.16.0'")
#get_ipython().system(' pip install transformers==4.39.1')
#get_ipython().system(' pip install pandas')


# ### Importing required libraries
# 

# 
# In this section, you will import the necessary libraries and modules to prepare your dataset for training with PyTorch. The focus is on text processing and creating data loaders that will be used for training your models.
# 
# - **DataLoader**: A PyTorch utility that allows you to load data in batches, making it easier to manage large datasets during training.
# - **build_vocab_from_iterator**: A function from `torchtext.vocab` that creates a vocabulary object from an iterator. The vocabulary is crucial for text processing, as it maps tokens (words) to integers.
# - **Vocab**: Represents the vocabulary, a mapping of tokens to indices. This is used to convert text data into a numerical form that the model can understand.
# - **Tensor, torch, nn, Transformer**: Core PyTorch modules and classes for tensors (the fundamental data structure in PyTorch), neural network layers, and the Transformer model architecture.
# - **get_tokenizer**: A function from `torchtext.data.utils` that returns a tokenizer to convert text strings into token lists.
# - **pad_sequence**: A utility from `torch.nn.utils.rnn` that pads sequences to the same length, a common requirement for batch processing in models that deal with variable-length sequences.
# 
# This setup is essential for processing text data, converting it into numerical format, and preparing batches of data for training neural networks, particularly for tasks like sequence modeling and classification.
# 

# In[2]:


import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchtext.vocab import build_vocab_from_iterator
from torchtext.vocab import Vocab
from torch import Tensor
from torch.nn import Transformer
from torchtext.data.utils import get_tokenizer
from torch.nn.utils.rnn import pad_sequence
from itertools import chain
from itertools import islice
from torchtext.datasets import IMDB
from copy import deepcopy
import random
import csv
import json
from tqdm import tqdm
import pandas as pd

# You can also use this section to suppress warnings generated by your code:
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.filterwarnings('ignore')


# ## Tokenization and vocabulary building
# 
# In this section, you will define functions and set up necessary components for text processing, crucial for preparing your dataset for model training.
# 

# ### Tokenization
# - The `tokenizer` is initialized to tokenize text using basic English tokenization rules, converting text samples into lists of tokens.
# - `yield_tokens` is a generator function that iterates through the data, yielding tokenized versions of the text samples. This function facilitates vocabulary building by providing a stream of tokens.
# - `word_dict` defines special tokens used in text processing, such as padding `[PAD]`, class `[CLS]`, separator `[SEP]`, mask `[MASK]`, and unknown `[UNK]` tokens, with their corresponding indices.
# - Special symbols and their indices are explicitly defined for clarity and used throughout data preparation.
# - `text_to_index` and `index_to_en` functions are utility converters. The former converts text into a list of numerical indices based on the vocabulary, and the latter reverses this process, translating a sequence of indices back into readable English text.
# 
# - **`CLS` (Classification Token)**: This token serves as the Start of Sentence (SOS) marker. It represents the overall meaning of the entire sentence. Commonly used in tasks that require understanding the entire input, like classification.
# 
# - **`SEP` (Separator Token)**: Used as the End of Sentence (EOS) marker. It also acts as a delimiter in scenarios where a model needs to understand and differentiate between multiple sentences, like in question-answering or sentence-pair tasks.
# 
# - **`PAD` (Padding Token)**: This token is added to sequences to ensure all inputs are of equal length. During training, it's important to note that the `[PAD]` token, typically with an ID of 0, does not contribute to the gradient calculations.
# 
# - **`MASK` (Masked Token)**: Utilized for word replacement in tasks like masked language modeling. It allows models to predict the identity of masked-out words, facilitating learning of bidirectional representations.
# 
# - **`UNK` (Unknown Token)**: Acts as a placeholder for words that are not found in the tokenizer's vocabulary. This token replaces any unknown or out-of-vocabulary item in the input data.
# 
# These components are foundational for preprocessing text data, ensuring it is in the correct format for model training, including tokenization, numerical conversion, and handling special tokens necessary for models like BERT.
# 

# In[3]:


tokenizer = get_tokenizer("basic_english")

def yield_tokens(data_iter):
    for label, data_sample in data_iter:
        yield tokenizer(data_sample)

# Define special symbols and indices
PAD_IDX,CLS_IDX, SEP_IDX,  MASK_IDX,UNK_IDX= 0, 1, 2, 3, 4

# Make sure the tokens are in order of their indices to properly insert them in vocab
special_symbols = ['[PAD]','[CLS]', '[SEP]','[MASK]','[UNK]']


# ### Vocabulary building
# This section focuses on building the vocabulary from the IMDB dataset.
# - You can utilize the `IMDB` dataset from `torchtext.datasets`, splitting it into training and testing sets.
# - The vocabulary is built using the `build_vocab_from_iterator` function, incorporating special symbols (`[PAD]`, `[CLS]`, `[SEP]`, `[MASK]`, `[UNK]`) at the beginning.
# - The `UNK_IDX` is set as the default index for unknown words, and the total vocabulary size is printed.
# 
# 

# In[4]:


#create data splits
train_iter, test_iter = IMDB(split=('train', 'test'))
all_data_iter = chain(train_iter, test_iter)
#check tokenizer
# list(yield_tokens(all_data_iter))[5][:20]
fifth_item_tokens = next(islice(yield_tokens(all_data_iter), 5, None))
print(fifth_item_tokens[:20])


# In[5]:


#create vocab : vocab is only built using train data
vocab=build_vocab_from_iterator(yield_tokens(all_data_iter),specials=special_symbols,special_first=True)

vocab.set_default_index(UNK_IDX)
VOCAB_SIZE=len(vocab)
print(VOCAB_SIZE)


# 
# Now, create functions that transform token indices to token texts and vice versa. You will use them later on.
# 

# In[6]:


text_to_index=lambda text: [vocab(token) for token in tokenizer(text)]
index_to_en = lambda seq_en: " ".join([vocab.get_itos()[index] for index in seq_en])


# Let's check the mappings:
# 

# In[7]:


seq_en = [0, 1, 2, 3, 4, 5, 6]  # Example input sequence
english_sentence = index_to_en(seq_en)
seq2=[6,16,26131]
english_sentence = index_to_en(seq2)

print(english_sentence)

text = "I've seen R-rated films with male nudity. Nowhere, because they don't exist."  # Example input text
text_to_index = lambda text: [vocab[token] for token in tokenizer(text)]
index_sequence = text_to_index(text)

print(index_sequence)


# ## Text masking and data preparation for BERT
# 
# This section introduces functions for preparing data for BERT's Masked Language Model (MLM) and Next Sentence Prediction (NSP) tasks, crucial steps for fine-tuning BERT for specific NLP tasks.
# 

# ### Text masking
# 
# The `Masking` function applies BERT's MLM strategy, deciding whether each token in a sequence should be masked, left unchanged, or replaced with a random token. This process is essential for training the model to predict masked words based on their context.
# 

# First, define a function that returns random 0/1 from bernouli distribution for random sampling.
# 

# In[8]:


def bernoulli_true_false(p):
    # Create a Bernoulli distribution with probability p
    bernoulli_dist = torch.distributions.Bernoulli(torch.tensor([p]))
    # Sample from this distribution and convert 1 to True and 0 to False
    return bernoulli_dist.sample().item() == 1


# Now, define the masking function:
# 

# In[9]:


def Masking(token):
    # Decide whether to mask this token (20% chance)
    mask = bernoulli_true_false(0.2)

    # If mask is False, immediately return with '[PAD]' label
    if not mask:
        return token, '[PAD]'

    # If mask is True, proceed with further operations
    # Randomly decide on an operation (50% chance each)
    random_opp = bernoulli_true_false(0.5)
    random_swich = bernoulli_true_false(0.5)

    # Case 1: If mask, random_opp, and random_swich are True
    if mask and random_opp and random_swich:
        # Replace the token with '[MASK]' and set label to a random token
        mask_label = index_to_en(torch.randint(0, VOCAB_SIZE, (1,)))
        token_ = '[MASK]'

    # Case 2: If mask and random_opp are True, but random_swich is False
    elif mask and random_opp and not random_swich:
        # Leave the token unchanged and set label to the same token
        token_ = token
        mask_label = token

    # Case 3: If mask is True, but random_opp is False
    else:
        # Replace the token with '[MASK]' and set label to the original token
        token_ = '[MASK]'
        mask_label = token

    return token_, mask_label


# Let's check how the random masking startegy works:
# 

# In[10]:


torch.manual_seed(100)
for l in range(10):
  token="apple"
  token_,label=Masking(token)
  if token==token_ and label=="[PAD]":
    print(token_,label,f"\t Actual token *{token}* is left unchanged")
  elif token_=="[MASK]" and label==token:
    print(token_,label,f"\t Actual token *{token}* is masked with '{token_}'")
  else:
    print(token_,label,f"\t Actual token *{token}* is replaced with random token #{label}#")


# ### Data preparation for MLM
# 
# `prepare_for_mlm` prepares tokenized text for MLM training by applying the masking strategy. It returns sequences of masked tokens along with their corresponding labels, optionally including the original (raw) tokens for reference.
# 

# In[11]:


def prepare_for_mlm(tokens, include_raw_tokens=False):
    """
    Prepares tokenized text for BERT's Masked Language Model (MLM) training.

    """
    bert_input = []  # List to store sentences processed for BERT's MLM
    bert_label = []  # List to store labels for each token (mask, random, or unchanged)
    raw_tokens_list = []  # List to store raw tokens if needed
    current_bert_input = []
    current_bert_label = []
    current_raw_tokens = []

    for token in tokens:
        # Apply BERT's MLM masking strategy to the token
        masked_token, mask_label = Masking(token)

        # Append the processed token and its label to the current sentence and label list
        current_bert_input.append(masked_token)
        current_bert_label.append(mask_label)

        # If raw tokens are to be included, append the original token to the current raw tokens list
        if include_raw_tokens:
            current_raw_tokens.append(token)

        # Check if the token is a sentence delimiter (., ?, !)
        if token in ['.', '?', '!']:
            # If current sentence has more than two tokens, consider it a valid sentence
            if len(current_bert_input) > 2:
                bert_input.append(current_bert_input)
                bert_label.append(current_bert_label)
                # If including raw tokens, add the current list of raw tokens to the raw tokens list
                if include_raw_tokens:
                    raw_tokens_list.append(current_raw_tokens)

                # Reset the lists for the next sentence
                current_bert_input = []
                current_bert_label = []
                current_raw_tokens = []
            else:
                # If the current sentence is too short, discard it and reset lists
                current_bert_input = []
                current_bert_label = []
                current_raw_tokens = []

    # Add any remaining tokens as a sentence if there are any
    if current_bert_input:
        bert_input.append(current_bert_input)
        bert_label.append(current_bert_label)
        if include_raw_tokens:
            raw_tokens_list.append(current_raw_tokens)

    # Return the prepared lists for BERT's MLM training
    return (bert_input, bert_label, raw_tokens_list) if include_raw_tokens else (bert_input, bert_label)


# Now, let's check how MLM preparations transform the raw input into the input ready for training:
# 

# In[12]:


torch.manual_seed(100)
original_input="The sun sets behind the distant mountains."
tokens=tokenizer(original_input)
bert_input, bert_label= prepare_for_mlm(tokens, include_raw_tokens=False)
print("Without raw tokens: \t ","\n \t original_input is: \t ", original_input,"\n \t bert_input is: \t ", bert_input,"\n \t bert_label is: \t ", bert_label)
print("-"*200)
torch.manual_seed(100)
bert_input, bert_label, raw_tokens_list= prepare_for_mlm(tokens, include_raw_tokens=True)
print("With raw tokens: \t ","\n \t original_input is: \t ", original_input,"\n \t bert_input is: \t ", bert_input,"\n \t bert_label is: \t ", bert_label,"\n \t raw_tokens_list is: \t ", raw_tokens_list)


# Therefore, each token in a sentence is labeled, depending on the masking operation that is applied on that token. In this example, the first "the" is **masked**, therefore, bert_input is [MASK] and its bert_label is 'The'. Tokens 'sun', 'sets', 'behind' and the last 'the' are not changed, so their corresponding labels are [PAD]. "distant" is **masked and replaced with a random token**, therefore, bert_input is [MASK] and its bert_label is 'human-scaled'. Finally, 'mountains' and '.' are **unchanged** so their corresponding labels are [PAD].
# 

# ### Data preparation for NSP
# 
# `process_for_nsp` prepares data for the NSP task by creating pairs of sentences. It labels these pairs to indicate whether the second sentence is the subsequent sentence in the original text, facilitating the model's learning of sentence relationships.
# 

# In[13]:


def process_for_nsp(input_sentences, input_masked_labels):
    """
    Prepares data for Next Sentence Prediction (NSP) task in BERT training.

    Args:
    input_sentences (list): List of tokenized sentences.
    input_masked_labels (list): Corresponding list of masked labels for the sentences.

    Returns:
    bert_input (list): List of sentence pairs for BERT input.
    bert_label (list): List of masked labels for the sentence pairs.
    is_next (list): Binary label list where 1 indicates 'next sentence' and 0 indicates 'not next sentence'.
    """
    if len(input_sentences) < 2:
       raise ValueError("must have two same number of items.")


    # Verify that both input lists are of the same length and have a sufficient number of sentences
    if len(input_sentences) != len(input_masked_labels):
        raise ValueError("Both lists must have the same number of items.")

    bert_input = []
    bert_label = []
    is_next = []

    available_indices = list(range(len(input_sentences)))

    while len(available_indices) >= 2:
        if random.random() < 0.5:
            # Choose two consecutive sentences to simulate the 'next sentence' scenario
            index = random.choice(available_indices[:-1])  # Exclude the last index
            # append list and add  '[CLS]' and  '[SEP]' tokens
            bert_input.append([['[CLS]']+input_sentences[index]+ ['[SEP]'],input_sentences[index + 1]+ ['[SEP]']])
            bert_label.append([['[PAD]']+input_masked_labels[index]+['[PAD]'], input_masked_labels[index + 1]+ ['[PAD]']])
            is_next.append(1)  # Label 1 indicates these sentences are consecutive

            # Remove the used indices
            available_indices.remove(index)
            if index + 1 in available_indices:
                available_indices.remove(index + 1)
        else:
            # Choose two random distinct sentences to simulate the 'not next sentence' scenario
            indices = random.sample(available_indices, 2)
            bert_input.append([['[CLS]']+input_sentences[indices[0]]+['[SEP]'],input_sentences[indices[1]]+ ['[SEP]']])
            bert_label.append([['[PAD]']+input_masked_labels[indices[0]]+['[PAD]'], input_masked_labels[indices[1]]+['[PAD]']])
            is_next.append(0)  # Label 0 indicates these sentences are not consecutive

            # Remove the used indices
            available_indices.remove(indices[0])
            available_indices.remove(indices[1])



    return bert_input, bert_label, is_next


# Let's look into some sample input sentences and create NSP pairs:
# 

# In[14]:


#flatten the tensor
flatten = lambda l: [item for sublist in l for item in sublist]
# Sample input sentences
input_sentences = [["i", "love", "apples"], ["she", "enjoys", "reading", "books"], ["he", "likes", "playing", "guitar"]]
# Create masked labels for the sentences
input_masked_labels=[]
for sentence in input_sentences:
  _, current_masked_label= prepare_for_mlm(sentence, include_raw_tokens=False)
  input_masked_labels.append(flatten(current_masked_label))
# Create NSP pairs and labels
random.seed(100)
bert_input, bert_label, is_next = process_for_nsp(input_sentences, input_masked_labels)

# Print the output
print("BERT Input:")
for pair in bert_input:
    print(pair)
print("BERT Label:")
for pair in bert_label:
    print(pair)
print("Is Next: ", is_next)
print("-"*200)
random.seed(1000)
bert_input, bert_label, is_next = process_for_nsp(input_sentences, input_masked_labels)

# Print the output
print("BERT Input:")
for pair in bert_input:
    print(pair)
print("BERT Label:")
for pair in bert_label:
    print(pair)
print("Is Next: ", is_next)


# These two examples demonstrate how sentence pairs are randomly created from the sentence bank and labeled for NSP task. Special symbols [CLS] and [SEP] are first added to the input sentences. BERT label is created using the `prepare_for_mlm` function. In the first example, the second sentence follows the first sentence. Therefore, `Is Next` is 1. In the second example, the second sentence does not follow the first sentence. So, `Is Next` is 0. 
# 

# ### Finalizing BERT inputs
# 
# `prepare_bert_final_inputs` consolidates the prepared data for MLM and NSP into a format suitable for BERT training, including converting tokens to indices, padding sequences for uniform length, and generating segment labels to distinguish between pairs of sentences. This function is the final step in preparing data for BERT, ensuring it is in the correct format for effective model training.
# 

# In[15]:


def prepare_bert_final_inputs(bert_inputs, bert_labels, is_nexts,to_tenor=True):
    """
    Prepare the final input lists for BERT training.
    """
    def zero_pad_list_pair(pair_, pad='[PAD]'):
        pair=deepcopy(pair_)
        max_len = max(len(pair[0]), len(pair[1]))
        #append [PAD] to each sentence in the pair till the maximum length reaches
        pair[0].extend([pad] * (max_len - len(pair[0])))
        pair[1].extend([pad] * (max_len - len(pair[1])))
        return pair[0], pair[1]

    #flatten the tensor
    flatten = lambda l: [item for sublist in l for item in sublist]
    #transform tokens to vocab indices
    tokens_to_index=lambda tokens: [vocab[token] for token in tokens]

    bert_inputs_final, bert_labels_final, segment_labels_final, is_nexts_final = [], [], [], []

    for bert_input, bert_label,is_next in zip(bert_inputs, bert_labels,is_nexts):
        # Create segment labels for each pair of sentences
        segment_label = [[1] * len(bert_input[0]), [2] * len(bert_input[1])]

        # Zero-pad the bert_input and bert_label and segment_label
        bert_input_padded = zero_pad_list_pair(bert_input)
        bert_label_padded = zero_pad_list_pair(bert_label)
        segment_label_padded = zero_pad_list_pair(segment_label,pad=0)

        #convert to tensors
        if to_tenor:

            # Flatten the padded inputs and labels, transform tokens to their corresponding vocab indices, and convert them to tensors
            bert_inputs_final.append(torch.tensor(tokens_to_index(flatten(bert_input_padded)),dtype=torch.int64))
            #bert_labels_final.append(torch.tensor(tokens_to_index(flatten(bert_label_padded)),dtype=torch.int64))
            bert_labels_final.append(torch.tensor(tokens_to_index(flatten(bert_label_padded)),dtype=torch.int64))
            segment_labels_final.append(torch.tensor(flatten(segment_label_padded),dtype=torch.int64))
            is_nexts_final.append(is_next)

        else:
          # Flatten the padded inputs and labels
            bert_inputs_final.append(flatten(bert_input_padded))
            bert_labels_final.append(flatten(bert_label_padded))
            segment_labels_final.append(flatten(segment_label_padded))
            is_nexts_final.append(is_next)

    return bert_inputs_final, bert_labels_final, segment_labels_final, is_nexts_final


# You can check the results using the `bert_input`, `bert_label` and `is_next` from previous example:
# 

# In[16]:


bert_inputs_final, bert_labels_final, segment_labels_final, is_nexts_final=prepare_bert_final_inputs(bert_input, bert_label, is_next,to_tenor=True)
torch.set_printoptions(linewidth=10000)# this assures that whole output is printed in one line
print("input:\t\t",bert_input,"\ninputs_final:\t",bert_inputs_final,"\nbert labels final:\t",bert_labels_final,"\nsegment labels final:\t",segment_labels_final,"\nis nexts final:\t",is_nexts_final)


# Sentences are zero-padded and each token is mapped to its vocab index(`[CLS]`>>1, `he`>>33, ..., `[SEP]`>>2,`[PAD]`>>0])
# 

# Mask labels are also padded and mapped to vocab indices. In this case, all tokens are **unchanged** except the token, `he` which is masked:
# 

# In[17]:


print("input:\t\t",bert_input,"\nmask_label:\t",bert_label, "\nlabels_final: \t",bert_labels_final)


# Finally, segment labels are created, where tokens of the first sentence are labeled with 1, tokens of the second sentence are labeled with 2 and zero-paddings are labeled with 0.  
# 

# In[18]:


print("\ninputs_final:\t",bert_inputs_final,"\nsegment_labels:\t",segment_labels_final)


# ## Preparing the dataset
# 
# - A CSV file is created to store the data set prepared for BERT training and testing. Each row contains the original text, BERT inputs, labels, segment labels, and the NSP task label.
# - The data from the IMDB data set is tokenized, processed for MLM, and then for NSP. The results are formatted and written to the CSV file, providing a comprehensive data set for BERT model training.
# 
# This process is critical for ensuring the data is in the right format for effective training of BERT on the IMDB data set, focusing on understanding text context and relationships between sentences.
# 
# >This training process might take about 2 to 3 hours.
# 

# In[19]:

''' too long
csv_file_path ='train_bert_data_new.csv'
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(['Original Text', 'BERT Input', 'BERT Label', 'Segment Label', 'Is Next'])

    # Wrap train_iter with tqdm for a progress bar
    for n, (_, sample) in enumerate(tqdm(train_iter, desc="Processing samples")):
        # Tokenize the sample input
        tokens = tokenizer(sample)
        # Create MLM inputs and labels
        bert_input, bert_label = prepare_for_mlm(tokens, include_raw_tokens=False)
        if len(bert_input) < 2:
            continue
        # Create NSP pairs, token labels, and is_next label
        bert_inputs, bert_labels, is_nexts = process_for_nsp(bert_input, bert_label)
        # add zero-paddings, map tokens to vocab indices and create segment labels
        bert_inputs, bert_labels, segment_labels, is_nexts = prepare_bert_final_inputs(bert_inputs, bert_labels, is_nexts)
        # convert tensors to lists, convert lists to JSON-formatted strings
        for bert_input, bert_label, segment_label, is_next in zip(bert_inputs, bert_labels, segment_labels, is_nexts):
            bert_input_str = json.dumps(bert_input.tolist())
            bert_label_str = json.dumps(bert_label.tolist())
            segment_label_str = ','.join(map(str, segment_label.tolist()))
            # Write the data to a CSV file row-by-row
            csv_writer.writerow([sample, bert_input_str, bert_label_str, segment_label_str, is_next])
'''

# # Exercises
# 
# Learn to utilize Hugging Face's pre-trained BertTokenizer for text tokenization, including handling special tokens and preparing the IMDB dataset for NLP model training, without manually building a vocabulary.
# 

# ### Exercise 1 - Initializing the BERTTokenizer
# 1. **Import `BertTokenizer`**:
#    Begin by importing the `BertTokenizer` class from the `transformers` library. This library provides access to a wide range of NLP models and their corresponding tokenizers.
# 
# 2. **Load pretrained tokenizer**:
#    Utilize the `from_pretrained` method to load the `bert-base-uncased` tokenizer. This tokenizer is pre-configured with a vocabulary that suits the BERT model trained on uncapitalized English text. It's ideal for understanding the basics of BERT tokenization.
# 

# In[20]:


from transformers import BertTokenizer

# Load a pre-trained BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# from transformers import BertTokenizer
# 
# # Load a pre-trained BERT tokenizer
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# ```
# 
# </details>
# 

# ### Exercise 2 - Tokenizing the dataset
# 1. **Define the `yield_tokens` Function**:
#    Implement a function named `yield_tokens` that accepts an iterator over the dataset. This function is responsible for processing and tokenizing the text data.
# 
# 2. **Tokenize Text Samples**:
#    Within the `yield_tokens` function, iterate through the dataset. For each text sample, use the `BertTokenizer` to tokenize the text into sequences of token IDs. Make sure to handle longer texts by setting the `truncation` parameter to `True` and specifying a `max_length` to ensure all tokenized outputs are of a manageable size.
# 
# 3. **Yield Tokenized Texts**:
#    After tokenizing each text sample, yield the list of token IDs. These lists will be used in subsequent steps to build data structures suitable for training NLP models.
# 

# In[22]:


def yield_tokens(data_iter):
    for _, data_sample in data_iter:
        # Use the BERT tokenizer to tokenize the text
        # This returns a dictionary with 'input_ids' among other things
        tokens = tokenizer(data_sample, return_tensors='pt', truncation=True, max_length=512)['input_ids'][0]
        yield tokens.tolist()


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# def yield_tokens(data_iter):
#     for _, data_sample in data_iter:
#         # Use the BERT tokenizer to tokenize the text
#         # This returns a dictionary with 'input_ids' among other things
#         tokens = tokenizer(data_sample, return_tensors='pt', truncation=True, max_length=512)['input_ids'][0]
#         yield tokens.tolist()
# ```
# </details>
# 

# ### Exercise 3 - Building the vocabulary with special tokens
# 1. **Define Special Tokens and Indices**: Start by defining indices for special tokens such as `[PAD]`, `[CLS]`, `[SEP]`, `[MASK]`, and `[UNK]`. Create a list named `special_symbols` that includes these tokens, ensuring they are in the correct order according to their indices.
# 
# 2. **Load Dataset**: Ensure you have the IMDB dataset's training split loaded. This data will be used to build the vocabulary.
# 
# 3. **Build Vocabulary**: Utilize the `build_vocab_from_iterator` function, passing the `yield_tokens` generator function as an argument. This function iterates over the tokenized dataset and builds a vocabulary. Make sure to include the special tokens by specifying them in the `specials` argument of the `build_vocab_from_iterator` function.
# (Since you are using a pre-trained tokenizer, you don't need to build the vocab from scratch. Instead, you can directly use the tokenizer's vocab.) 
# 
# 4. **Set Default Index for Unknown Tokens**: After building the vocabulary, use the `set_default_index` method to specify the index for unknown tokens (`UNK_IDX`). This ensures that any tokens not found in the vocabulary are handled correctly.
# (Since you are using a pre-trained tokenizer, you don't need to build the vocab from scratch. Instead, you can directly use the tokenizer's vocab.)
# 

# In[23]:


from torchtext.data.functional import to_map_style_dataset
from torchtext.datasets import IMDB
# Define special symbols and indices
PAD_IDX, CLS_IDX, SEP_IDX, MASK_IDX, UNK_IDX = tokenizer.pad_token_id, tokenizer.cls_token_id, tokenizer.sep_token_id, tokenizer.mask_token_id, tokenizer.unk_token_id
special_symbols = ['[PAD]', '[CLS]', '[SEP]', '[MASK]', '[UNK]']

# Load IMDB dataset
train_iter, test_iter = IMDB(split=('train', 'test'))

# Convert to map-style datasets to be compatible with transformers' tokenizers
train_dataset = to_map_style_dataset(train_iter)
test_dataset = to_map_style_dataset(test_iter)

# Since you are using a pre-trained tokenizer, you don't need to build the vocab from scratch. 
# Instead, you can directly use the tokenizer's vocab.
VOCAB_SIZE = len(tokenizer)

print("Vocabulary Size:", VOCAB_SIZE)


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# from torchtext.data.functional import to_map_style_dataset
# from torchtext.datasets import IMDB
# 
# # Define special symbols and indices
# PAD_IDX, CLS_IDX, SEP_IDX, MASK_IDX, UNK_IDX = tokenizer.pad_token_id, tokenizer.cls_token_id, tokenizer.sep_token_id, tokenizer.mask_token_id, tokenizer.unk_token_id
# special_symbols = ['[PAD]', '[CLS]', '[SEP]', '[MASK]', '[UNK]']
# 
# # Load IMDB dataset
# train_iter, test_iter = IMDB(split=('train', 'test'))
# 
# # Convert to map-style datasets to be compatible with transformers' tokenizers
# train_dataset = to_map_style_dataset(train_iter)
# test_dataset = to_map_style_dataset(test_iter)
# 
# # Since you are using a pre-trained tokenizer, you don't need to build the vocab from scratch. 
# # Instead, you can directly use the tokenizer's vocab.
# VOCAB_SIZE = len(tokenizer)
# 
# print("Vocabulary Size:", VOCAB_SIZE)
# ```
# 
# </details>
# 

# ---
# 

# # Congratulations! You have completed the lab
# 

# ## Authors
# 

# [Joseph Santarcangelo](https://author.skills.network/instructors/joseph_santarcangelo)
# 
# Joseph has a Ph.D. in Electrical Engineering, his research focused on using machine learning, signal processing, and computer vision to determine how videos impact human cognition. Joseph has been working for IBM since he completed his PhD.
# 

# [Ashutosh Sagar](https://www.linkedin.com/in/ashutoshsagar/) is completing his MS in CS from Dalhousie University. He has previous experience working with Natural Language Processing and as a Data Scientist.
# 

# ## References
# 
# 
# - [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/pdf/1810.04805.pdf)
# - [Mastering BERT Model: Building it from Scratch with Pytorch](https://medium.com/data-and-beyond/complete-guide-to-building-bert-model-from-sratch-3e6562228891)
# 

# 
# 
# 

# © Copyright IBM Corporation. All rights reserved.
# 
# 

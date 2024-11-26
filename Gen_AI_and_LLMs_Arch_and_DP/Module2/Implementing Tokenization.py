# jupyter nbconvert --to script "Implementing Tokenization.ipynb"
#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo">
#     </a>
# </p>
# 

# # **Implementing Tokenization**
# 
# Estimated time needed: **60** minutes
# 
# Tokenizers are essential tools in natural language processing that break down text into smaller units called tokens. These tokens can be words, characters, or subwords, making complex text understandable to computers. By dividing text into manageable pieces, tokenizers enable machines to process and analyze human language, powering various language-related applications like translation, sentiment analysis, and chatbots. Essentially, tokenizers bridge the gap between human language and machine understanding.
# 
# <div style="text-align:center">
#   <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-AI0205EN-SkillsNetwork/tokenizer.png" width="700px" alt="wizard">
# </div>
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
#     <li>
#         <a href="#What-is-a-tokenizer-and-why-do-we-use-it?">What is a tokenizer and why do we use it?</a>
#     </li>
#     <li><a href="#Types-of-tokenizer">Types of tokenizer</a></li>
#         <ol>
#             <li><a href="#Word-based-tokenizer">Word-based tokenizer</a></li>
#             <li><a href="#Character-based-tokenizer">Character-based tokenizer</a></li>
#             <li><a href="#Subword-based-tokenizer">Subword-based tokenizer</a></li>
#                 <ol>
#                     <li><a href="#WordPiece">WordPiece</a></li>
#                     <li><a href="#Unigram-and-SentencePiece">Unigram and SentencePiece</a></li>
#                 </ol>
#         </ol>
#     <li>
#         <a href="#Tokenization-with-PyTorch">Tokenization with PyTorch</a>
#     </li>
#     <li>
#         <a href="#Token-indices">Token indices</a>
#         <ol>
#             <li><a href="#Out-of-vocabulary-(OOV)">Out-of-vocabulary (OOV)</a></li>
#         </ol>
#     </li>
#     <li><a href="#Exercise:-Comparative-text-tokenization-and-performance-analysis">Exercise: Comparative text tokenization and performance analysis</a></li>
# </ol>
# 

# ---
# 

# # Objectives
# 
# After completing this lab, you will be able to:
# 
#  - Understand the concept of tokenization and its importance in natural language processing 
#  - Identify and explain word-based, character-based, and subword-based tokenization methods.
#  - Apply tokenization strategies to preprocess raw textual data before using it in machine learning models.
# 

# ---
# 

# # Setup
# 

# For this lab, you will be using the following libraries:
# 
# * [`nltk`](https://www.nltk.org/) or natural language toolkit, will be employed for data management tasks. It offers comprehensive tools and resources for processing natural language text, making it a valuable choice for tasks such as text preprocessing and analysis.
# 
# * [`spaCy`](https://spacy.io/) is an open-source software library for advanced natural language processing in Python. spaCy is renowned for its speed and accuracy in processing large volumes of text data.
# 
# * [`BertTokenizer`](https://huggingface.co/docs/transformers/main_classes/tokenizer#berttokenizer) is part of the Hugging Face Transformers library, a popular library for working with state-of-the-art pre-trained language models. BertTokenizer is specifically designed for tokenizing text according to the BERT model's specifications.
# 
# * [`XLNetTokenizer`](https://huggingface.co/docs/transformers/main_classes/tokenizer#xlnettokenizer) is another component of the Hugging Face Transformers library. It is tailored for tokenizing text in alignment with the XLNet model's requirements.
# 
# * [`torchtext`](https://pytorch.org/text/stable/index.html) It is part of the PyTorch ecosystem, to handle various natural language processing tasks. It  simplifies the process of working with text data and provides functionalities for data preprocessing, tokenization, vocabulary management, and batching.
# 

# ### Installing required libraries
# 

# The following required libraries are __not__ pre-installed in the Skills Network Labs environment. __You will need to run the following cell__ to install them:
# 

# In[1]:


#get_ipython().system('pip install nltk')
#get_ipython().system('pip install transformers')
#get_ipython().system('pip install sentencepiece')
#get_ipython().system('pip install spacy')
#get_ipython().system('pip install numpy==1.24')
#get_ipython().system('python -m spacy download en_core_web_sm')
#get_ipython().system('python -m spacy download de_core_news_sm')
#get_ipython().system('pip install numpy scikit-learn')
#get_ipython().system('pip install torch==2.0.1')
#get_ipython().system('pip install torchtext==0.15.2')


# ### Importing required libraries
# 
# _We recommend you import all required libraries in one place (here):_
# 

# In[2]:


import nltk
nltk.download("punkt")
nltk.download('punkt_tab')
import spacy
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.util import ngrams
from transformers import BertTokenizer
from transformers import XLNetTokenizer

from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.filterwarnings('ignore')


# ---
# 

# ## What is a tokenizer and why do we use it?
# 
# Tokenizers play a pivotal role in natural language processing, segmenting text into smaller units known as tokens. These tokens are subsequently transformed into numerical representations called token indices, which are directly employed by deep learning algorithms.
# <center>
# <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-AI0201EN-Coursera/images/Tokenization%20lab%20Diagram%201.png" width="50%" alt="Image Description">
# </center>
# 

# ## Types of tokenizer
# 
# The meaningful representation can vary depending on the model in use. Various models employ distinct tokenization algorithms, and you will broadly cover the following approaches. Transforming text into numerical values might appear straightforward initially, but it encompasses several considerations that must be kept in mind.
# <center>
# <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-AI0201EN-Coursera/images/Tokenization%20lab%20Diagram%202.png" width="50%" alt="Image Description">
# </center>
# 

# ## Word-based tokenizer
# 
# ###  nltk
# 
# As the name suggests, this is the splitting of text based on words. There are different rules for word-based tokenizers, such as splitting on spaces or splitting on punctuation. Each option assigns a specific ID to the split word. Here you use nltk's  ```word_tokenize```
# 

# In[3]:


text = "This is a sample sentence for word tokenization."
tokens = word_tokenize(text)
print(tokens)


# General libraries like nltk and spaCy often split words like 'don't' and 'couldn't,' which are contractions, into different individual words. There's no universal rule, and each library has its own tokenization rules for word-based tokenizers. However, the general guideline is to preserve the input format after tokenization to match how the model was trained.
# 

# In[4]:


# This showcases word_tokenize from nltk library

text = "I couldn't help the dog. Can't you do it? Don't be afraid if you are."
tokens = word_tokenize(text)
print(tokens)


# In[5]:


# This showcases the use of the 'spaCy' tokenizer with torchtext's get_tokenizer function

text = "I couldn't help the dog. Can't you do it? Don't be afraid if you are."
nlp = spacy.load("en_core_web_sm")
doc = nlp(text)

# Making a list of the tokens and priting the list
token_list = [token.text for token in doc]
print("Tokens:", token_list)

# Showing token details
for token in doc:
    print(token.text, token.pos_, token.dep_)


# Explanation of a few lines:
# - I PRON nsubj: "I" is a pronoun (PRON) and is the nominal subject (nsubj) of the sentence.
# - help VERB ROOT: "help" is a verb (VERB) and is the root action (ROOT) of the sentence.
# - afraid ADJ acomp: "afraid" is an adjective (ADJ) and is an adjectival complement (acomp) which gives more information about a state or quality related to the verb.
# 

# The problem with this algorithm is that words with similar meanings will be assigned different IDs, resulting in them being treated as entirely separate words with distinct meanings. For example, $Unicorns$ is the plural form of $Unicorn$, but a word-based tokenizer would tokenize them as two separate words, potentially causing the model to miss their semantic relationship.
# 

# In[6]:


text = "Unicorns are real. I saw a unicorn yesterday."
token = word_tokenize(text)
print(token)


# Each word is split into a token, leading to a significant increase in the model's overall vocabulary. Each token is mapped to a large vector containing the word's meanings, resulting in large model parameters.
# 

# Languages generally have a large number of words, the vocabularies based on them will always be extensive. However, the number of characters in a language is always fewer compared to the number of words. Next, we will explore character-based tokenizers.
# 

# ## Character-based tokenizer
# 
# As the name suggests, character-based tokenization involves splitting text into individual characters. The advantage of using this approach is that the resulting vocabularies are inherently small. Furthermore, since languages have a limited set of characters, the number of out-of-vocabulary tokens is also limited, reducing token wastage.
# 
# For example:
# Input text: `This is a sample sentence for tokenization.`
# 
# Character-based tokenization output: `['T', 'h', 'i', 's', 'i', 's', 'a', 's', 'a', 'm', 'p', 'l', 'e', 's', 'e', 'n', 't', 'e', 'n', 'c', 'e', 'f', 'o', 'r', 't', 'o', 'k', 'e', 'n', 'i', 'z', 'a', 't', 'i', 'o', 'n', '.']`
# 
# However, it's important to note that character-based tokenization has its limitations. Single characters may not convey the same information as entire words, and the overall token length increases significantly, potentially causing issues with model size and a loss of performance.
# 

# You have explored the limitations of both word-based and character-based tokenization methods. To leverage the advantages of both approaches, transformers employ subword-based tokenization, which will be discussed next.
# 

# ## Subword-based tokenizer
# 
# The subword-based tokenizer allows frequently used words to remain unsplit while breaking down infrequent words into meaningful subwords. Techniques such as SentencePiece, or WordPiece are commonly used for subword tokenization. These methods learn subword units from a given text corpus, identifying common prefixes, suffixes, and root words as subword tokens based on their frequency of occurrence. This approach offers the advantage of representing a broader range of words and adapting to the specific language patterns within a text corpus.
# 
# In both examples below, words are split into subwords, which helps preserve the semantic information associated with the overall word. For instance, 'Unhappiness' is split into 'un' and 'happiness,' both of which can appear as stand-alone subwords. When we combine these individual subwords, they form 'unhappiness,' which retains its meaningful context. This approach aids in maintaining the overall information and semantic meaning of words.
# 
# <center>
# <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-AI0201EN-Coursera/images/Tokenization%20lab%20Diagram%203.png" width="50%" alt="Image Description">
# </center>
# 

# ### WordPiece
# 
# Initially, WordPiece initializes its vocabulary to include every character present in the training data and progressively learns a specified number of merge rules. WordPiece doesn't select the most frequent symbol pair but rather the one that maximizes the likelihood of the training data when added to the vocabulary. In essence, WordPiece evaluates what it sacrifices by merging two symbols to ensure it's a worthwhile endeavor.
# 
# Now, the WordPiece tokenizer is implemented in BertTokenizer. 
# Note that BertTokenizer treats composite words as separate tokens.
# 

# In[7]:


tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
tokenizer.tokenize("IBM taught me tokenization.")


# Here’s a breakdown of the output:
# - 'ibm': "IBM" is tokenized as 'ibm'. BERT converts tokens into lowercase, as it does not retain the case information when using the "bert-base-uncased" model.
# - 'taught', 'me', '.': These tokens are the same as the original words or punctuation, just lowercased (except punctuation).
# - 'token', '##ization': "Tokenization" is broken into two tokens. "Token" is a whole word, and "##ization" is a part of the original word. The "##" indicates that "ization" should be connected back to "token" when detokenizing (transforming tokens back to words).
# 

# ### Unigram and SentencePiece
# 
# Unigram is a method for breaking words or text into smaller pieces. It accomplishes this by starting with a large list of possibilities and gradually narrowing it down based on how frequently those pieces appear in the text. This approach aids in efficient text tokenization.
# 
# SentencePiece is a tool that takes text, divides it into smaller, more manageable parts, assigns IDs to these segments, and ensures that it does so consistently. Consequently, if you use SentencePiece on the same text repeatedly, you will consistently obtain the same subwords and IDs.
# 
# Unigram and SentencePiece work together by implementing Unigram's subword tokenization method within the SentencePiece framework. SentencePiece handles subword segmentation and ID assignment, while Unigram's principles guide the vocabulary reduction process to create a more efficient representation of the text data. This combination is particularly valuable for various NLP tasks in which subword tokenization can enhance the performance of language models.
# 

# In[8]:


tokenizer = XLNetTokenizer.from_pretrained("xlnet-base-cased")
tokenizer.tokenize("IBM taught me tokenization.")


# Here's what's happening with each token:
# - '▁IBM': The "▁" (often referred to as "whitespace character") before "IBM" indicates that this token is preceded by a space in the original text. "IBM" is kept as is because it's recognized as a whole token by XLNet and it preserves the casing because you are using the "xlnet-base-cased" model.
# - '▁taught', '▁me', '▁token': Similarly, these tokens are prefixed with "▁" to indicate they are new words preceded by a space in the original text, preserving the word as a whole and maintaining the original casing.
# - 'ization': Unlike "BertTokenizer," "XLNetTokenizer" does not use "##" to indicate subword tokens. "ization" appears as its own token without a prefix because it directly follows the preceding word "token" without a space in the original text.
# - '.': The period is tokenized as a separate token since punctuation is treated separately.
# 

# ## Tokenization with PyTorch 
# In PyTorch, especially with the `torchtext` library, the tokenizer breaks down text from a data set into individual words or subwords, facilitating their conversion into numerical format. After tokenization, the vocab (vocabulary) maps these tokens to unique integers, allowing them to be fed into neural networks. This process is vital because deep learning models operate on numerical data and cannot process raw text directly. Thus, tokenization and vocabulary mapping serve as a bridge between human-readable text and machine-operable numerical data. Consider the dataset:
# 

# In[9]:


dataset = [
    (1,"Introduction to NLP"),
    (2,"Basics of PyTorch"),
    (1,"NLP Techniques for Text Classification"),
    (3,"Named Entity Recognition with PyTorch"),
    (3,"Sentiment Analysis using PyTorch"),
    (3,"Machine Translation with PyTorch"),
    (1," NLP Named Entity,Sentiment Analysis,Machine Translation "),
    (1," Machine Translation with NLP "),
    (1," Named Entity vs Sentiment Analysis  NLP ")]


# This next line imports the ```get_tokenizer``` function from the ```torchtext.data.utils``` module. In the torchtext library, the ```get_tokenizer```  function is utilized to fetch a tokenizer by name. It provides support for a range of tokenization methods, including basic string splitting, and returns various tokenizers based on the argument passed to it.
# 

# In[10]:


from torchtext.data.utils import get_tokenizer


# In[11]:


tokenizer = get_tokenizer("basic_english")


# You apply the tokenizer to the dataset. Note: If ```basic_english``` is selected, it returns the ```_basic_english_normalize()``` function, which normalizes the string first and then splits it by space.
# 

# In[12]:


tokenizer(dataset[0][1])


# ## Token indices
# You would represent words as numbers as NLP algorithms can process and manipulate numbers more efficiently and quickly than raw text. You use the function **```build_vocab_from_iterator```**, the output is typically referred to as 'token indices' or simply 'indices.' These indices represent the numeric representations of the tokens in the vocabulary.
# 
# The **```build_vocab_from_iterator```** function, when applied to a list of tokens, assigns a unique index to each token based on its position in the vocabulary. These indices serve as a way to represent the tokens in a numerical format that can be easily processed by machine learning models.
# 
# For example, given a vocabulary with tokens ["apple", "banana", "orange"], the corresponding indices might be [0, 1, 2], where "apple" is represented by index 0, "banana" by index 1, and "orange" by index 2.
# 
# **```dataset```** is an iterable. Therefore, you use a generator function yield_tokens to apply the **```tokenizer```**. The purpose of the generator function **```yield_tokens```** is to yield tokenized texts one at a time. Instead of processing the entire dataset and returning all the tokenized texts in one go, the generator function processes and yields each tokenized text individually as it is requested. The tokenization process is performed lazily, which means the next tokenized text is generated only when needed, saving memory and computational resources.
# 

# In[13]:


def yield_tokens(data_iter):
    for  _,text in data_iter:
        yield tokenizer(text)


# In[14]:


my_iterator = yield_tokens(dataset) 


# This creates an iterator called **```my_iterator```** using the generator. To begin the evaluation of the generator and retrieve the values, you can iterate over **```my_iterator```** using a for loop or retrieve values from it using the **```next()```** function.
# 

# In[15]:


next(my_iterator)


# You build a vocabulary from the tokenized texts generated by the **```yield_tokens```** generator function, which processes the dataset. The **```build_vocab_from_iterator()```** function constructs the vocabulary, including a special token `unk` to represent out-of-vocabulary words. 
# 
# ### Out-of-vocabulary (OOV)
# When text data is tokenized, there may be words that are not present in the vocabulary because they are rare or unseen during the vocabulary building process. When encountering such OOV words during actual language processing tasks like text generation or language modeling, the model can use the ```<unk>``` token to represent them.
# 
# For example, if the word "apple" is present in the vocabulary, but "pineapple" is not, "apple" will be used normally in the text, but "pineapple" (being an OOV word) would be replaced by the ```<unk>``` token.
# 
# By including the `<unk>` token in the vocabulary, you provide a consistent way to handle out-of-vocabulary words in your language model or other natural language processing tasks.
# 

# In[16]:


vocab = build_vocab_from_iterator(yield_tokens(dataset), specials=["<unk>"])
vocab.set_default_index(vocab["<unk>"])


# This code demonstrates how to fetch a tokenized sentence from an iterator, convert its tokens into indices using a provided vocabulary, and then print both the original sentence and its corresponding indices.
# 

# In[17]:


def get_tokenized_sentence_and_indices(iterator):
    tokenized_sentence = next(iterator)  # Get the next tokenized sentence
    token_indices = [vocab[token] for token in tokenized_sentence]  # Get token indices
    return tokenized_sentence, token_indices

tokenized_sentence, token_indices = get_tokenized_sentence_and_indices(my_iterator)
next(my_iterator)

print("Tokenized Sentence:", tokenized_sentence)
print("Token Indices:", token_indices)


# Using the lines of code provided above in a simple example, demonstrate tokenization and the building of vocabulary in PyTorch.
# 

# In[18]:


lines = ["IBM taught me tokenization", 
         "Special tokenizers are ready and they will blow your mind", 
         "just saying hi!"]

special_symbols = ['<unk>', '<pad>', '<bos>', '<eos>']

tokenizer_en = get_tokenizer('spacy', language='en_core_web_sm')

tokens = []
max_length = 0

for line in lines:
    tokenized_line = tokenizer_en(line)
    tokenized_line = ['<bos>'] + tokenized_line + ['<eos>']
    tokens.append(tokenized_line)
    max_length = max(max_length, len(tokenized_line))

for i in range(len(tokens)):
    tokens[i] = tokens[i] + ['<pad>'] * (max_length - len(tokens[i]))

print("Lines after adding special tokens:\n", tokens)

# Build vocabulary without unk_init
vocab = build_vocab_from_iterator(tokens, specials=['<unk>'])
vocab.set_default_index(vocab["<unk>"])

# Vocabulary and Token Ids
print("Vocabulary:", vocab.get_itos())
print("Token IDs for 'tokenization':", vocab.get_stoi())


# Let's break down the output:
# 1. **Special Tokens**:
# - Token: "`<unk>`", Index: 0: `<unk>` stands for "unknown" and represents words that were not seen during vocabulary building, usually during inference on new text.
# - Token: "`<pad>`", Index: 1: `<pad>` is a "padding" token used to make sequences of words the same length when batching them together. 
# - Token: "`<bos>`", Index: 2: `<bos>` is an acronym for "beginning of sequence" and is used to denote the start of a text sequence.
# - Token: "`<eos>`", Index: 3: `<eos>` is an acronym for "end of sequence" and is used to denote the end of a text sequence.
# 
# 2. **Word Tokens**:
# The rest of the tokens are words or punctuation extracted from the provided sentences, each assigned a unique index:
# - Token: "IBM", Index: 5
# - Token: "taught", Index: 16
# - Token: "me", Index: 12
#     ... and so on.
#     
# 3. **Vocabulary**:
# It denotes the total number of tokens in the sentences upon which vocabulary is built.
#     
# 4. **Token IDs for 'tokenization'**:
# It represents the token IDs assigned in the vocab where a number represents its presence in the sentence.
# 

# In[19]:


new_line = "I learned about embeddings and attention mechanisms."

# Tokenize the new line
tokenized_new_line = tokenizer_en(new_line)
tokenized_new_line = ['<bos>'] + tokenized_new_line + ['<eos>']

# Pad the new line to match the maximum length of previous lines
new_line_padded = tokenized_new_line + ['<pad>'] * (max_length - len(tokenized_new_line))

# Convert tokens to IDs and handle unknown words
new_line_ids = [vocab[token] if token in vocab else vocab['<unk>'] for token in new_line_padded]

# Example usage
print("Token IDs for new line:", new_line_ids)


# Let's break down the output:
# 
# 1. **Special Tokens**:
# - Token: "`<unk>`", Index: 0: `<unk>` stands for "unknown" and represents words that were not seen during vocabulary building, usually during inference on new text.
# - Token: "`<pad>`", Index: 1: `<pad>` is a "padding" token used to make sequences of words the same length when batching them together. 
# - Token: "`<bos>`", Index: 2: `<bos>` is an acronym for "beginning of sequence" and is used to denote the start of a text sequence.
# - Token: "`<eos>`", Index: 3: `<eos>` is an acronym for "end of sequence" and is used to denote the end of a text sequence.
# 
# 2. The token **`and`** is recognized in the sentence and it is assigned **`token_id` - 7**.
# 

# ## Exercise: Comparative text tokenization and performance analysis
# - Objective: Evaluate and compare the tokenization capabilities of four different NLP libraries (`nltk`, `spaCy`, `BertTokenizer`, and `XLNetTokenizer`) by analyzing the frequency of tokenized words and measuring the processing time for each tool using `datetime`.
# - Text for tokenization is as below:
# 

# In[26]:


text = """
Going through the world of tokenization has been like walking through a huge maze made of words, symbols, and meanings. Each turn shows a bit more about the cool ways computers learn to understand our language. And while I'm still finding my way through it, the journey’s been enlightening and, honestly, a bunch of fun.
Eager to see where this learning path takes me next!"
"""

# Counting and displaying tokens and their frequency
from collections import Counter
def show_frequencies(tokens, method_name):
    print(f"{method_name} Token Frequencies: {dict(Counter(tokens))}\n")


# In[39]:


# TODO
from datetime import datetime
time = datetime.now()
tokens = word_tokenize(text)
show_frequencies(tokens, "nltk")
newtime = datetime.now()
print("processing time =",newtime -time)
time = newtime

nlp = spacy.load("en_core_web_sm")
doc = nlp(text)
# Making a list of the tokens
token_list = [token.text for token in doc]
show_frequencies(token_list, "spaCy")
newtime = datetime.now()
print("processing time =",newtime -time)
time = newtime

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
tokens = tokenizer.tokenize(text)
show_frequencies(tokens, "BertTokenizer")
newtime = datetime.now()
print("processing time =",newtime -time)
time = newtime

tokenizer = XLNetTokenizer.from_pretrained("xlnet-base-cased")
tokens = tokenizer.tokenize(text)
show_frequencies(tokens, "XLNetTokenizer")
newtime = datetime.now()
print("processing time =",newtime -time)




# <details>
#     <summary>Click here for the answer</summary>
#     
# ```Python
# import nltk
# import spacy
# from transformers import BertTokenizer, XLNetTokenizer
# from datetime import datetime
# 
# # NLTK Tokenization
# start_time = datetime.now()
# nltk_tokens = nltk.word_tokenize(text)
# nltk_time = datetime.now() - start_time
# 
# # SpaCy Tokenization
# nlp = spacy.load("en_core_web_sm")
# start_time = datetime.now()
# spacy_tokens = [token.text for token in nlp(text)]
# spacy_time = datetime.now() - start_time
# 
# # BertTokenizer Tokenization
# bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
# start_time = datetime.now()
# bert_tokens = bert_tokenizer.tokenize(text)
# bert_time = datetime.now() - start_time
# 
# # XLNetTokenizer Tokenization
# xlnet_tokenizer = XLNetTokenizer.from_pretrained("xlnet-base-cased")
# start_time = datetime.now()
# xlnet_tokens = xlnet_tokenizer.tokenize(text)
# xlnet_time = datetime.now() - start_time
#     
# # Display tokens, time taken for each tokenizer, and token frequencies
# print(f"NLTK Tokens: {nltk_tokens}\nTime Taken: {nltk_time} seconds\n")
# show_frequencies(nltk_tokens, "NLTK")
# 
# print(f"SpaCy Tokens: {spacy_tokens}\nTime Taken: {spacy_time} seconds\n")
# show_frequencies(spacy_tokens, "SpaCy")
# 
# print(f"Bert Tokens: {bert_tokens}\nTime Taken: {bert_time} seconds\n")
# show_frequencies(bert_tokens, "Bert")
# 
# print(f"XLNet Tokens: {xlnet_tokens}\nTime Taken: {xlnet_time} seconds\n")
# show_frequencies(xlnet_tokens, "XLNet")
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

# [Roodra Kanwar](https://www.linkedin.com/in/roodrakanwar/) is completing his MS in CS specializing in big data from Simon Fraser University. He has previous experience working with machine learning and as a data engineer.
# 

# [Joseph Santarcangelo](https://www.linkedin.com/in/joseph-s-50398b136/) has a Ph.D. in Electrical Engineering, his research focused on using machine learning, signal processing, and computer vision to determine how videos impact human cognition. Joseph has been working for IBM since he completed his PhD.
# 

# [Vicky Kuo](https://www.linkedin.com/in/vicky-tck/) is completing her Master's degree in IT at York University with scholarships. Her master's thesis explores the optimization of deep learning algorithms, employing an innovative approach to scrutinize and enhance neural network structures and performance.
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
# ```{|2023-10-02|0.1|Roodra|Created Lab Template|}
# ```
# ```{|2023-10-03|0.1|Vicky|Revised the Lab|}
# ```
# 

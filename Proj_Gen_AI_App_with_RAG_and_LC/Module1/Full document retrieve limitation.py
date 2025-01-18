#!/usr/bin/env python
# coding: utf-8

# <p style="text-align:center">
#     <a href="https://skills.network" target="_blank">
#     <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/assets/logos/SN_web_lightmode.png" width="200" alt="Skills Network Logo"  />
#     </a>
# </p>
# 

# # **Put Whole Document into Prompt and Ask the Model**
# 

# Estimated time needed: **20** minutes
# 

# ## Overview
# In recent years, the development of Large Language Models (LLMs) like GPT-3 and GPT-4 has revolutionized the field of natural language processing (NLP). These models are capable of performing a wide range of tasks, from generating coherent text to answering questions and summarizing information. Their effectiveness, however, is not without limitations. One significant constraint is the context window length, which affects how much information can be processed at once. LLMs operate within a fixed context window, measured in tokens, with GPT-3 having a limit of 4096 tokens and GPT-4 extending to 8192 tokens. When dealing with lengthy documents, attempting to input the entire text into the model's prompt can lead to truncation, where essential information is lost, and increased computational costs due to the processing of large inputs.
# 
# These limitations become particularly pronounced when creating a retrieval-based question-answering (QA) assistant. The context length constraint restricts the ability to input all content into the prompt simultaneously, leading to potential loss of critical context and details. This necessitates the development of sophisticated strategies for selectively retrieving and processing relevant sections of the document. Techniques such as chunking the document into manageable parts, employing summarization methods, and using external retrieval systems are crucial to address these challenges. Understanding and mitigating these limitations are essential for designing effective QA systems that leverage the full potential of LLMs while navigating their inherent constraints.
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
#         </ol>
#     </li>
#     <li><a href="#Build-LLM">Build LLM</a></li>
#     <li><a href="#Load-source-document">Load source document</a></li>
#     <li>
#         <a href="#Limitation-of-retrieve-directly-from-full-document">Limitation of retrieve directly from full document</a>
#         <ol>
#             <li><a href="#Context-length">Context length</a></li>
#             <li><a href="#LangChain-prompt-template">LangChain prompt template</a></li>
#             <li><a href="#Use-mixtral-model">Use mixtral model</a></li>
#             <li><a href="#Use-Llama-3-model">Use Llama 3 model</a></li>
#             <li><a href="#Use-one-piece-of-information">Use one piece of information</a></li>
#         </ol>
#     </li>
# </ol>
# 
# <a href="#Exercises">Exercises</a>
# <ol>
#     <li><a href="#Exercise-1---Change-to-use-another-LLM">Exercise 1 - Change to use another LLM</a></li>
# </ol>
# 

# ## Objectives
# 
# After completing this lab you will be able to:
# 
#  - Explain the concept of context length for LLMs.
#  - Recognize the limitations of retrieving information when inputting the entire content of a document into a prompt.
# 

# ----
# 

# ## Setup
# 

# For this lab, you will use the following libraries:
# 
# *   [`ibm-watson-ai`](https://ibm.github.io/watson-machine-learning-sdk/index.html) for using LLMs from IBM's watsonx.ai.
# *   [`langchain`, `langchain-ibm`, `langchain-community`](https://www.langchain.com/) for using relevant features from LangChain.
# 

# ### Installing required libraries
# 
# The following required libraries are __not__ preinstalled in the Skills Network Labs environment. __You must run the following cell__ to install them:
# 
# **Note:** The version is being pinned here to specify the version. It's recommended that you do this as well. Even if the library is updated in the future, the installed library could still support this lab work.
# 
# This might take approximately 1 minute. 
# 
# As `%%capture` is used to capture the installation, you won't see the output process. After the installation is completed, you will see a number beside the cell.
# 

# In[26]:


#get_ipython().run_cell_magic('capture', '', '#After executing the cell,please RESTART the kernel and run all the cells.\n!pip install --user "ibm-watsonx-ai==1.0.10"\n!pip install --user "langchain==0.2.6" \n!pip install --user "langchain-ibm==0.1.8"\n!pip install --user "langchain-community==0.2.1"\n')


# After you install the libraries, restart your kernel. You can do that by clicking the **Restart the kernel** icon.
# 
# <img src="https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/build-a-hotdog-not-hotdog-classifier-guided-project/images/Restarting_the_Kernel.png" width="70%" alt="Restart kernel">
# 

# ### Importing required libraries
# 

# In[1]:


# You can use this section to suppress warnings generated by your code:
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.filterwarnings('ignore')

from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.document_loaders import TextLoader
from langchain_ibm import WatsonxLLM


# ## Build LLM
# 

# Here, you will create a function that interacts with the watsonx.ai API, enabling you to utilize various models available.
# 
# You just need to input the model ID in string format, then it will return you with the LLM object. You can use it to invoke any queries. A list of model IDs can be found in [here](https://ibm.github.io/watsonx-ai-python-sdk/fm_model.html).
# 

# In[2]:


def llm_model(model_id):
    parameters = {
        GenParams.MAX_NEW_TOKENS: 256,  # this controls the maximum number of tokens in the generated output
        GenParams.TEMPERATURE: 0.5, # this randomness or creativity of the model's responses
    }
    
    credentials = {
        "url": "https://us-south.ml.cloud.ibm.com"
    }
    
    project_id = "skills-network"
    
    model = ModelInference(
        model_id=model_id,
        params=parameters,
        credentials=credentials,
        project_id=project_id
    )
    
    llm = WatsonxLLM(watsonx_model = model)
    return llm


# Let's try to invoke an example query.
# 

# In[3]:


llama_llm = llm_model('meta-llama/llama-3-70b-instruct')


# In[4]:


llama_llm.invoke("How are you?")


# ## Load source document
# 

# A document has been prepared here.
# 

# In[5]:


#get_ipython().system('wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d_ahNwb1L2duIxBR6RD63Q/state-of-the-union.txt"')
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d_ahNwb1L2duIxBR6RD63Q/state-of-the-union.txt"
output_file = "state-of-the-union.txt"

# Télécharger le fichier
response = requests.get(url)
if response.status_code == 200:
    with open(output_file, 'wb') as file:
        file.write(response.content)
else:
    print(f"Erreur : Impossible de télécharger le fichier (code {response.status_code})")


# Use `TextLoader` to load the text.
# 

# In[6]:


loader = TextLoader("state-of-the-union.txt")


# In[7]:


data = loader.load()


# Let's take a look at the document.
# 

# In[8]:


content = data[0].page_content
print(content)


# ## Limitation of retrieve directly from full document
# 

# ### Context length
# 

# Before you explore the limitations of directly retrieving information from a full document, you need to understand a concept called `context length`. 
# 
# `Context length` in LLMs refers to the amount of text or information (prompt) that the model can consider when processing or generating output. LLMs have a fixed context length, meaning they can only take into account a limited amount of text at a time.
# 
# For example, the model `llama-3-70b-instruct` has a context window size of `8,192` tokens, while the model `mixtral-8x7b-instruct-v01` has a context window size of `32,768`.
# 

# So, how long is your source document here? The answer is 8,235 tokens, which you calculated using this [platform](https://platform.openai.com/tokenizer).
# 

# In this situation, it means your source document can fit within the `mixtral-8x7b-instruct-v01`, model but cannot fit entirely within the `llama-3-70b-instruct model`. Is this true? Let's use code to explore this further.
# 

# ### LangChain prompt template
# 

# A prompt template has been set up using LangChain to make it reusable.
# 
# In this template, you will define two input variables:
# - `content`: This variable will hold all the content from the entire source document at once.
# - `question`: This variable will capture the user's query.
# 

# In[9]:


template = """According to the document content here 
            {content},
            answer this question 
            {question}.
            Do not try to make up the answer.
                
            YOUR RESPONSE:
"""

prompt_template = PromptTemplate(template=template, input_variables=['content', 'question'])
print(prompt_template)


# ### Use mixtral model
# 

# Since the context window length of the mixtral model is longer than your source document, you can assume it can retrieve relevant information for the query when you input the whole document into the prompt.
# 

# First, let's build a mixtral model.
# 

# In[10]:


mixtral_llm = llm_model('mistralai/mixtral-8x7b-instruct-v01')


# Then, create a query chain.
# 

# In[11]:


query_chain = LLMChain(llm=mixtral_llm, prompt=prompt_template)


# Then, set the query and get the answer.
# 

# In[12]:


query = "It is in which year of our nation?"
response = query_chain.invoke(input={'content': content, 'question': query})
print(response['text'])


# Ypu have asked a question whose answer appears at the very end of the document. Despite this, the LLM was still able to answer it correctly because the model's context window is long enough to accommodate the entire content of the document.
# 

# ### Use Llama 3 model
# 

# Now, let's try using an LLM with a smaller context window, which is less than the total number of tokens in the document.
# 

# First, create a query chain.
# 

# In[13]:


query_chain = LLMChain(llm=llama_llm, prompt=prompt_template)
print(query_chain)


# Then, use the query chain (the code is shown below) to invoke the LLM, which will answer the same query as before based on the entire document's content.
# 

# **Important Note**: The code has been commented. You need to uncomment it to run. When you run the following code, you will observe an error being invoked. This is because the total number of tokens in the document exceeds the LLM's context window. Consequently, the LLM cannot accommodate the entire content as a prompt.
# 

# In[16]:


#query = "It is in which year of our nation?"
#response = query_chain.invoke(input={'content': content, 'question': query})
#print(response['text'])


# Now you can see the limitation of inputting the entire document content at once into the prompt and using the LLM to retrieve information.
# 

# ### Use one piece of information
# 

# So, putting the whole content does not work. Does this mean that if you input only the piece of information related to the query from the document, and its token length is smaller than the LLM's context window, it can work?
# 
# Let's see.
# 

# Now, let's retrieve the piece of information related to the query and put it in the content variable.
# 

# In[17]:


content = """
    The only nation that can be defined by a single word: possibilities. 
    
    So on this night, in our 245th year as a nation, I have come to report on the State of the Union. 
    
    And my report is this: the State of the Union is strong—because you, the American people, are strong. 
"""


# Then, use the Llama model again.
# 

# In[18]:


query_chain = LLMChain(llm=llama_llm, prompt=prompt_template)


# In[19]:


query = "It is in which year of our nation?"
response = query_chain.invoke(input={'content': content, 'question': query})
print(response['text'])


# Now it works.
# 

# #### Take away
# 

# If the document is much longer than the LLM's context length, it is important and necessary to cut the document into chunks, index them, and then let the LLM retrieve the relevant information accurately and efficiently.
# 
# In the next lesson, you will learn how to perform these operations using LangChain.
# 

# # Exercises
# 

# ### Exercise 1 - Change to use another LLM
# 

# Try to use another LLM with smaller context length to see if the same error occurs. For example, try using `'ibm/granite-13b-chat-v2'` with `8192` context length.
# 

# In[25]:


# Your code here
ibm_llm = llm_model('ibm/granite-13b-chat-v2')
content = data[0].page_content
query_chain = LLMChain(llm=ibm_llm, prompt=prompt_template)
#response = query_chain.invoke(input={'content': content, 'question': query})
print(response['text'])


# <details>
#     <summary>Click here for Solution</summary>
# 
# ```python
# granite_llm = llm_model('ibm/granite-13b-chat-v2')
# query_chain = LLMChain(llm=granite_llm, prompt=prompt_template)
# query = "It is in which year of our nation?"
# response = query_chain.invoke(input={'content': content, 'question': query})
# print(response['text'])
# ```
# 
# </details>
# 

# ## Authors
# 

# [Kang Wang](https://author.skills.network/instructors/kang_wang)
# 
# Kang Wang is a Data Scientist in IBM. He is also a PhD Candidate in the University of Waterloo.
# 

# ### Other Contributors
# 

# [Joseph Santarcangelo](https://author.skills.network/instructors/joseph_santarcangelo), 
# 
# Joseph has a Ph.D. in Electrical Engineering, his research focused on using machine learning, signal processing, and computer vision to determine how videos impact human cognition. Joseph has been working for IBM since he completed his PhD.
# 

# ```{## Change Log}
# ```
# 

# ```{|Date (YYYY-MM-DD)|Version|Changed By|Change Description||-|-|-|-||2024-07-12|0.1|Kang Wang|Create the lab|}
# ```
# 

# Copyright © IBM Corporation. All rights reserved.
# 

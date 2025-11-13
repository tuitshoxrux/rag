import os
from dotenv import load_dotenv
from pprint import pprint

import pandas as pd

import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings

import google.generativeai as genai

from IPython.display import Markdown

genai.__version__
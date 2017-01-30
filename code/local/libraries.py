# data handling
import glob
import json
import pickle
import os.path
import numpy as np
import pandas as pd
from datetime import datetime

# visualization
import folium
import networkx as nx
import seaborn as sns
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt

# location data
import googlemaps

# NLP
from nltk.corpus import stopwords
import string
import re

# API requests
import requests

# translation
from yandex_translate import YandexTranslate

# data structures
from collections import defaultdict
from collections import Counter

# warnings
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'
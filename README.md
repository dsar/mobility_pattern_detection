# Mobility patterns/events in Switzerland with Twitter

This README file includes information about the project assignment, as well as the project implementation.

## Project Assignment

### Abstract

We are given a dataset containing tweets in Switzerland starting from 2010. The first goal of the project is to analyse the data and reconstruct mobility flows of the users. More concretely, we will try to get insights into high-frequency migration patterns in the Swiss territory. This could be achieved by focusing on "frontaliers" who commute daily from France and Germany to Geneva and Zurich respectively. In addition, we will try to detect changes in migration patterns when special events take place (e.g., a new Alpine tunnel gets opened). The second task of the project is to detect events. Here, we will focus on dates and locations of such events, as well as positive or negative sentiment.

### Data Description

The dataset consists of 5GB of tweets in Switzerland, which are collected using the Twitter API starting from 2010. The tweets have been downloaded in json format and processed such that only a subset of the attributes is kept. Thus, we have information about the user id, the date and time of the tweet, the tweet text, etc. Moreover, all tweets have geo-location data, which is crucial for our analysis. Finally, the dataset is stored in the HDFS of the IC cluster.

### Feasibility and Risks

The feasibility of the project depends strongly on the dataset. The reconstruction of mobility flows of users requires their location at different times during each day. In our case, tweets are the only source of geo-located information. In order for our project to be feasible, users should tweet uniformly during the day in order for their mobility patterns to be revealed. For example, people who work in Zurich but live in Germany should tweet both during the day and during the evening, so that we can have information about their working and living place respectively.

With respect to the second task, we need to set certain thresholds and make certain assumptions in order to perform a successful analysis. More concretely, we should set a reasonable threshold for the number of tweets that indicates that an event took place (e.g. more than 100 tweets within a distance of 100m. may indicate that an event took place). Moreover, the assumptions that many events take place late in the evening and especially during the weekend may help in filtering properly our data and performing successful analysis.

The feasibility and risks of our project could be further assessed once the dataset is provided.

### Deliverables

We will use Spark in order to handle properly the given dataset. We will perform data filtering and aggregations according to the needs of each task. As soon as we have aggregated results, we will use Python for data analysis and visualization. The deliverables of our project are going to be:

- A well documented and commented Spark application for data filtering and aggregation written in Python.
- A Python notebook with data analysis and visualization of our results. 
- Our assumptions and data analysis pipeline would be well documented in the Python notebook.

### Timeplan
A rough timeplan of our project is as follows:

- Phase 1: Exploratory data analysis, data cleaning and data wrangling.
- Phase 2: Detection of mobility patterns.
- Phase 3: We work on the event detection.
- Phase 4: We partner with a team that focused on the visualization part (to be done).
- Phase 5: We work on the sentiment analysis of the tweets (to be done).

## Project Implementation

The provided dataset contains tweets starting from 2010 till 2016. We choose to make a yearly based analysis on all our data analysis tasks. We focus on the machine learning side of the project and provide a simple but insightful visualization of our results. Also, we try to partner with a team that focuses on the visualization part of the project that is responsible for producing more complex plots.

### Mobility Patterns

The [mobility_patterns](code/local/mobility_patterns.ipynb) notebook contains our work on detecting mobility patterns in Switzerland. It contains both the code and the assumptions we made in order to produce our results. These assumptions have to do mainly with:
* which users to keep in order to produce our results
* how we determined if a user is at work or not
* how we determined the user's location of residence and work
For more information and a detailed analysis of how we approach the problem of mobility patterns, please refer to the [mobility_patterns](code/local/mobility_patterns.ipynb) notebook

### Event Detection
The [event_detection](code/local/event_detection.ipynb) notebook contains our work on detecting events in Switzerland based on geolocated information. It contains both the code and the assumptions we made in order to produce our results. These assumptions have to do mainly with:
* minimum number of tweets to declare the presence of an event
* distance between tweets referring to the same event (tweets for the same event should be posted from the same area, i.e. in a small distance)
* metrics we introduce in order to better detect events (e.g. an event should have tweets from numerous users)
For more information and a detailed analysis of how we approach the problem of event detection, please refer to the [mobility_patterns](code/local/event_detection.ipynb) notebook.

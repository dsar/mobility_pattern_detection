# Mobility patterns/events in Switzerland with Twitter

## Abstract

We are given a dataset containing tweets in Switzerland starting from 2012. The first goal of the project is to analyse the data and reconstruct mobility flows of the users. More concretely, we will try to get insights into high-frequency migration patterns in the swiss territory. This could be achieved by focusing on "frontaliers" who commute daily from France and Germany to Geneva and Zurich respectively. In addition, we will try to detect changes in migration patterns when special events take place (e.g., a new Alpine tunnel gets opened). The second task of the project is to detect events. Here, we will focus on dates and locations of such events, as well as positive or negative sentiment.

## Data Description

The dataset consists of 80GB of tweets in Switzerland, which are collected using the Twitter API starting from 2012. The tweets have been downloaded in json format and processed such that only a subset of the attributes is kept. Thus, we have information about the user id, the date and time of the tweet and the tweet (We would know if we have more attributes for our data once we get access to the dataset) . Moreover, all tweets have geo-location data, which is crucial for our analysis. Finally, the dataset is stored in the HDFS of the IC cluster.

## Feasibility and Risks

The feasibility of the project depends strongly on the dataset. The reconstruction of mobility flows of users requires their location at different times during each day. In our case, tweets are the only source of geo-located information. In order for our project to be feasible, users should tweet uniformly during the day in order for their mobility patterns to be revealed. For example, people who work in Zurich but live in Germany should tweet both during the day and during the evening, so that we can have information about their working and living place respectively.

With respect to the second task, we need to set certain thresholds and make certain assumptions in order to perform a successful analysis. More concretely, we should set a reasonable threshold for the number of tweets that indicates that an event took place (e.g. more than 100 tweets within a distance of 100m. may indicate that an event took place). Moreover, the assumptions that many events take place late in the evening and especially during the weekend may help in filtering properly our data and performing successful analysis.

The feasibility and risks of our project could be further assessed once the dataset is provided.

## Deliverables

We will use Spark for exploratory data analysis. We will perform data filtering and aggregations according to the needs of each task. As soon as we have aggregated results, we will use Python for data analysis and visualization. The deliverables of our project are going to be:

- A well documented and commented Spark application for data filtering and aggregation written in Scala.
- A Python notebook with data analysis and visualization of our results. 
- Our assumptions and data analysis pipeline would be well documented in the Python notebook.


## Timeplan
...

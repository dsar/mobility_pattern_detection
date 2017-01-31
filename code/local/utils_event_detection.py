from libraries import *
from ast import literal_eval
from sklearn.cluster import DBSCAN


def parse_day_of_tweet(date):
    """
    Returns the date of the tweet
    
    Parameters
    ----------
    data: datetime object
    
    Returns
    ------
    string of date
    """

    return str(date.date())

def parse_hour_of_tweet(date):
    """
    Returns the hour of the tweet
    
    Parameters
    ----------
    data: datetime object
    
    Returns
    ------
    tweet hour
    """

    return date.time()

def keep_hashtags(tweet):
    """
    Finds all hashtags contained in one tweet
    
    Parameters
    ----------
    tweet: text of tweet
    
    Returns
    -------
    set of hashtags contains in tweet text
    """

    # make sure tweet is str (some tweets may be numbers)
    tweet = str(tweet)
    # find hashtags, if any exist
    hashtags = [item for item in tweet.split() if item.startswith('#')]
    # check is list is empty
    if not hashtags:
        return np.nan
    # return set
    return set(hashtags)

def hashtag_preprocess(hashtag, translator):
    """
    Removes punctuation from hashtags and convert everything to lowercase
    
    Parameters
    ----------
    hashtag: hashtag string
    translator: create a dictionary using a comprehension - this maps every character from 
    string.punctuation to None. Initialize a translation object from it.
    
    Returns
    -------
    A processes hashtag with small letters and no punctuation
    """

    # convert to lowercase
    hashtag = hashtag.lower()
    # return hashtag without punctuation
    return '#' + hashtag.translate(translator)

def fill_num_of_tweets(row, df_grouped):
    """
    Find the number of tweets given the day of tweet and the hashtag
    
    Parameters
    ----------
    row: dataframe row
    df_grouped: Series that contains the hashtag and day of tweets as index and the number of tweets as value
    
    Returns
    -------
    new row containing the number of tweets for a particular day with the particular hashtag
    """

    # use dayOfTweet and hashtag as index and find the number of tweets using the df_grouped Series
    row['numOfTweets'] = df_grouped.ix[(row['dayOfTweet'], row['hashtag'])]
    return row

def train_dbscan(coordinates, eps, min_samples):
    """
    Trains a DBSCAN model given some parameters
    
    Parametes
    ---------
    coordinates: list of (lat, long) coordinates
    eps: parameter that indicates how close points should be to form a cluster
    min_samples: minimum number of points to form a cluster
    
    Returns
    -------
    a trained DBSCAN model
    """

    # initialize DBSCAN object based on parameters
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    # fit model
    dbscan.fit(coordinates)
    return dbscan

def visualize_dbscan(dbscan, coordinates):
    """
    Visualizes the DBSCAN clusters
    
    Parameters
    ----------
    dbscan: trained dbscan model
    coordinates: list of coordinates
    """

    # define some useful variables
    core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
    core_samples_mask[dbscan.core_sample_indices_] = True
    # find label for each point
    labels = dbscan.labels_
    # find number of clusters (remove noise)
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    # find unique labels
    unique_labels = set(labels)
    # define color spectrum
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    # black removed and is used for noise instead
    # visualize clusters
    for index, color in zip(unique_labels, colors):
        if index == -1:
            color = 'k'
        class_member_mask = (labels == index)
        data = coordinates[class_member_mask & core_samples_mask]
        plt.plot(data.ix[:, 0], data.ix[:, 1], 'o', 
                 markerfacecolor=color, markeredgecolor='k', markersize=8)
        data = coordinates[class_member_mask & ~core_samples_mask]
        plt.plot(data.ix[:, 0], data.ix[:, 1], 'o', 
                 markerfacecolor=color, markeredgecolor='k', markersize=4)
    plt.title('Estimated number of clusters: %d' % n_clusters_)
    plt.show()

def detect_event_dbscan(df_grouped, accuracy, min_tweets):
    """
    Detects events using geolocated information, if any exist
    
    Parameters
    ----------
    df_grouped: a grouped dataframe based on day of tweet and hashtag 
    (geolocated information should be contained in the dataframe)
    min_tweets = minimum number of tweets to form cluster
    accuracy: how close points should be to form a cluster
    
    Returns
    -------
    list of tuples of events (date, hashtag)
    """

    # initialize list of events
    list_of_events = []
    # iterate though all groups
    for index, dataframe in df_grouped:
        # keep coordinates
        coordinates = dataframe[['longitude', 'latitude']]
        # train dbscan
        dbscan = train_dbscan(coordinates, accuracy, min_tweets)
        # check if clusters are detected (if len equals 1, only noise is detected)
        if len(set(dbscan.labels_)) == 1:
            continue
        # find unique labels
        labels = set(dbscan.labels_)
        # remove label for noise
        if -1 in labels:
        	labels.remove(-1)
        # assign right label to each tweet
        dataframe['clusterId'] = dbscan.labels_
        # iterate though all labels
        for label in labels:
            # process data about certain label
            df_subset = dataframe[dataframe['clusterId'] == label]
            # find average location of event
            avg_lat = "{0:.3f}".format(df_subset['latitude'].mean())
            avg_long = "{0:.3f}".format(df_subset['longitude'].mean())
            avg_loc = (avg_lat, avg_long) 
            # find hashtags
            hashtags = df_subset['hashtag'].values.tolist()
            # append event to list
            list_of_events.append((index[0], hashtags[0], avg_loc)) 
            # print log message
            print('Date: ', index[0], '\t', 'Location: ', avg_loc, '\t', 'Hashtags: ', hashtags[0])
    # return list of events
    return list_of_events

def is_spam_event(row, threshold):
    """
    Finds if an event is spam or not
    
    Parameters
    ----------
    row: row of dataframe 
    threshold: spammer threshold
    
    Returns
    -------
    True of False
    """

    if(row['usersPerHashtag'] < threshold):
        row['spamEvent'] = True
    else:
        row['spamEvent'] = False
    return row

def std_of_events(df, new_df=None):
    """
    Finds the standard deviation of events
    
    Parameters
    ----------
    df: dataframe with all tweets that may be events
    new_df: dataframe with hashtags and day of tweets that are detected as events

    Returns
    -------
    dict with events as keys and std as values
    """

    # create a dict to store timestamps for each event
    d = defaultdict(list)
    if new_df is not None:
        # keep timestamp and hashtag for each event
        event_indices = new_df.index.values.tolist()
        # iterate though all rows
        for line in df.iterrows():
            # keep timestame
            timestamp = line[1][1]
            # keep hashtag
            hashtag = line[1][5] 
            # keep dayOfTweet
            dayOfTweet = line[1][4]
            # if the row refers to a detected event, keep timestamp
            if(hashtag, dayOfTweet) in event_indices:   
                d[hashtag, dayOfTweet].append(timestamp)
    else:
        for line in df.iterrows():
            hashtag = line[1][4] 
            dayOfTweet = line[1][5]
            approxLocation = line[1][6]
            hour = line[1][1]
            d[hashtag, dayOfTweet, approxLocation].append(hour)
    # iterate though dictionary and convert timestamps to seconds
    for key, values in d.items():
        # count seconds from midnight
        midnight = values[0].replace(hour=0, minute=0, second=0)
        # convert to seconds
        d[key] = [(value - midnight).total_seconds() for value in values]
    # build dict for the standard deviation
    std_dict = dict()
    for key, value in d.items():
        if len(value) > 1:
            # calculate std
            std_dict[key] = np.std(value)
    return std_dict

def fill_std(row, std_dict):
    """
    Fills the std value for each event
    
    Parameters
    ----------
    row: row of dataframe
    std_dict: dictionary with events and their respective std
    
    Returns
    -------
    new row that contains std information
    """

    # case if approxLocation is in keys
    if 'approxLocation' in row.keys():
        # define dict key
        key = (row['dayOfTweet'], row['hashtag'], row['approxLocation'])
        try:
            # get value from dict
            std = std_dict[key]
        except:
            # return NaN if key does not exist
            std = np.nan
    else:
        # define dict key
        key = (row['hashtag'], row['dayOfTweet'])
        try:
            # get value from dict
            std = std_dict[key]
        except:
            # return NaN if key does not exist 
            std = np.nan
    # convert std to minutes
    row['std'] = std / 60
    return row

def set_event_location(row, list_of_events_dbscan):
    """
    Set the location of events using the list_of_events_dbscan list
    
    Parameters
    ----------
    row: row of dataframe
    list_of_events_dbscan: list of events with (dayOfTweet, hashtag, location)
    
    Returns
    -------
    the location of the events using the hashtag and the day of tweet
    """

    for item in list_of_events_dbscan:
        if row['hashtag'] == item[1] and row['dayOfTweet'] == item[0]:
            return item[2]
    return np.nan

def reduce_location_accuracy(row, accuracy):
    """
    Reduces the location accuracy of the longitude and latitude based on the accuracy parameter
    
    Parameters
    ----------
    row: row of dataframe
    accuracy: how many decimals should be kept
    
    Returns
    -------
    new row with the reduced accuracy as tuple
    """

    # reduce long and lat accuracy
    long = ("{0:."+str(accuracy)+"f}").format(row['longitude'])
    lat = ("{0:."+str(accuracy)+"f}").format(row['latitude'])
    # build tuple
    row['approxLocation'] = (lat, long)
    return row

def spam_events(row, users_per_hashtag, threshold):
    """
    Finds if an event is created due to spam and the users per hashtag on a particular day and location
    
    Parameters
    ----------
    row: row of dataframe
    users_per_hashtag: series with key = (hashtag, dayOfTweet, approxLocation) and value = number of users
    threshold: spammer threshold
    
    Returns
    -------
    new row
    """

    # build key to look-up in the series
    key = (row['hashtag'], row['dayOfTweet'], row['approxLocation'])
    # check if value is above threshold
    if users_per_hashtag.ix[key] >= threshold:
        row['spamEvent'] = False
    else:
        row['spamEvent'] = True
    # find users per key
    row['usersPerHashtag'] = users_per_hashtag[key]
    return row

def find_canton_of_event(coordinates, gmaps, swiss_cantons, debug=True):
    """
    Finds the canton of residence and work

    Parameters
    ----------
    coordinates: the coordinates to be searched (given as string)
    gmaps: googlemaps object
    debug: if True, print debug message

    Returns
    ------
    canton id
    """

    # convert from string to tuple
    coordinates = literal_eval(coordinates)
    # get result from API
    try:
	    event_location = gmaps.reverse_geocode(coordinates)
	    if debug:
	    	print('Successful gmaps API call')
	    # iterate through result and find canton
	    for d in event_location[0]['address_components']:
	        if d['types'][0] == 'administrative_area_level_1':
	            canton = d['short_name']
	            if canton in swiss_cantons:
	                return canton
	            else:
	                return d['long_name']
    except:
    	return np.nan

def create_event_map(year, coord, hashtag, spams, usersPerHashtag):
    """
    Visualize the non-spam events in Switzerland
    
    Parameters
    year: year to be analyzed
    coord: coordinates for events
    hashtag: hashtag for the event
    spam: is event spam or not
    usersPerHashtag: users per event
    """

    # load json
    canton_geo = r'../../maps/data/ch-cantons.topojson.json'
    # create map object
    event_map = folium.Map(location=[46.762579, 7.927242], zoom_start=7)
    # iterate though all events
    for index, (lat, long) in enumerate(coord):
        # skip spam events
        if spams[index]:
            continue
        # find coordinates and plot
        lat = float(lat)
        long = float(long)
        popup_text = hashtag[index]+ ' (Users: ' + str(usersPerHashtag[index]) + ')'
        # make marker according to number of tweets per event
        folium.RegularPolygonMarker(location=(lat, long), radius=usersPerHashtag[index]/2.0, 
                            color='darkblue', fill_color='#769d96', fill_opacity=0.7, 
                            popup=popup_text, number_of_sides=6).add_to(event_map)
    map_name = '../../data/maps/event_detection_' + str(year) + '.html'
    event_map.save(map_name)
    return event_map

def analyse_performance(list_of_events_dbscan, list_of_events_heuristic):
    """
    Analyses the performance of the two approaches given their results
    
    Parameters
    list_of_events_dbscan: list of events detected using DBSCAN
    list_of_events_heuristic: list of events detected using the heuristic
    """
    
    # remove the location information from the lists
    list_of_events_dbscan = [(str(item[0]), item[1]) for item in list_of_events_dbscan]
    list_of_events_heuristic = [(str(item[0]), item[1]) for item in list_of_events_heuristic] 
    # how many events are detected by DBSCAN
    method_1 = len(set(list_of_events_dbscan))
    # how many events are detected by the heuristic
    method_2 = len(set(list_of_events_heuristic))
    print('Number of events detected with DBSCAN = ', method_1)
    print('Number of events detected with heuristic = ', method_2)
    print('---------------------------------------------')
    # find common events
    common_events_1 = [str(event) for event in list_of_events_dbscan if event in list_of_events_heuristic]
    common_events_2 = [str(event) for event in list_of_events_heuristic if event in list_of_events_dbscan]
    common_events = set(common_events_1 + common_events_2)
    print('The two methods found {0} events in common'.format(len(common_events)))
    print('Common events:')
    print('\n'.join(common_events))
    # find events detected by only one method
    only_dbscan = [str(event) for event in list_of_events_dbscan if event not in list_of_events_heuristic]
    only_heuristic = [str(event) for event in list_of_events_heuristic if event not in list_of_events_dbscan]
    print('---------------------------------------------')
    print('Found only by DBSCAN:')
    print('\n'.join(only_dbscan))
    print('---------------------------------------------')
    print('Found only by heuristic:')
    print('\n'.join(only_heuristic))
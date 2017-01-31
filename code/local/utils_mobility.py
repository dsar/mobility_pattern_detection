from libraries import *


def fill_gps_coordinates(row):
    """
    Feels any missing GPS information from the location information provided in the placeLongitude and placeLatitude
    columns
    
    Parameters
    ----------
    row: dataframe row
    
    Returns
    -------
    row feeled with missing data
    """

    # check if GPS information is None
    # check if place coordinates are in good range
    if (row['latitude'] == np.nan) and (40.0 < row['placeLatitude'] < 50.0):
        # feel missing value
        row['latitude'] = row['placeLatitude']
    if (row['longitude'] == np.nan) and (4.0 < row['placeLongitude'] < 8.0):
        # feel missing value
        row['longitude'] = row['placeLongitude']
    return row

def coordinates_distribution(coordinates):
    """
    Plots the distribution of the coordinates
    
    Parameters
    ----------
    coordinates: dataframe containing longitude and latitude information
    """

    # name of the features (longitude and latitude)
    features = coordinates.columns
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    axes = axes.ravel()
    feature_id = 0
    for idx, ax in enumerate(axes):
        # histogram for each feature
        ax.hist(coordinates[features[feature_id]], bins=100)
        # set display information for the plot
        title = 'Distribution of ' + features[feature_id]
        ax.set_title(title)
        ax.set_xlabel(features[feature_id])
        ax.set_ylabel('Frequency')
        feature_id += 1
    plt.tight_layout()

def is_at_work(date_and_time):
    """
    Checks if the given timestamp corresponds to working hours or not
    
    Parameters
    ----------
    date_and_time: timestamp of tweet in datetime format
    
    Returns
    -------
    True if the given timestamp is a working hour, otherwise False
    """

    # extract day
    week_day = date_and_time.weekday()
    # extract time
    time_of_day = date_and_time.hour
    # check if day is between Mon and Fri and if time is between 08:00 and 18:00
    if (week_day < 5) and (8 <= time_of_day < 18):
        return True
    return False

def hour_of_tweet(date_and_time):
    """
    Gets the time of the tweet
    
    Parameters
    ----------
    date_and_time: timestamp of tweet in datetime format
    
    Returns
    -------
    hour of tweet
    """

    return date_and_time.hour

def count_tweets_per_user(data):
    """
    Counts tweets per user
    
    Parameters
    ----------
    data: dataframe of the dataset
    
    Returns
    ------
    number of tweets per user
    """

    # group by userId and count 
    tweets_per_user = data[['userId', 'createdAt']].groupby(by='userId', as_index=False).count()
    tweets_per_user = tweets_per_user['createdAt'].copy()
    # give column a proper name
    tweets_per_user.rename('numOfTweets', inplace=True)
    # sort data
    tweets_per_user.sort(inplace=True)
    # reset index, keep useful information
    tweets_per_user = tweets_per_user.reset_index()['numOfTweets']
    return tweets_per_user

def visualize_tweets_per_user(tweets_per_user):
    """
    Plots the distribution of tweets with respect to the users
    
    Parameters
    ----------
    tweets_per_user: series containing the tweets per user
    """

    fig, ax = plt.subplots()
    # plot tweets
    f = tweets_per_user.plot(kind='line', figsize=(10, 6), ax=ax);
    # remove x labels, they are not usefull
    labels = pd.Series([])
    ax.set_xticklabels(labels)
    ax.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
    ax.grid()
    # set axis labels
    ax.set_xlabel('Users')
    ax.set_ylabel('Number of Tweets')
    ax.set_title('Number of Tweets per User')

def get_active_userIds(data, upper_threshold=5000, lower_threshold=50):
    """
    Get the user IDs of active users given a certain threshold
    
    Parameters
    ----------
    data: dataframe of the Twitter dataset
    lower_threshold: minimum number of tweets to detect an active user
    upper_threshold: maximum number of tweets to detect an active user
    
    Returns
    ------
    a list of user IDs for the active users
    """

    # group by user ID and count tweets
    tweets_per_user = data.groupby(by='userId', as_index=False).count()
    # keep only those above threshold
    filtered_data = tweets_per_user[(tweets_per_user['createdAt'] >= lower_threshold) & (tweets_per_user['createdAt'] <= upper_threshold)]
    # keep user IDs
    active_userIds = filtered_data['userId']
    # return list
    return list(active_userIds)

def reduce_location_accuracy(row, accuracy):
    """
    Reduces the accuracy of the GPS location
    
    Parameters
    ----------
    row: row of dataframe that contains the longitude and latitude informatio
    accuracy: how many decimals should be kept
    
    Returns
    ------
    new row that contains a tuple with the reduced accuracy
    """

    # reduce accuracy of coordinates
    long = ("{0:."+str(accuracy)+"f}").format(row['longitude'])
    lat = ("{0:."+str(accuracy)+"f}").format(row['latitude'])
    # create tuple
    row['reducedAccuracy'] = (lat, long)
    return row

def most_freq_locations(df):
    """
    Given a dataframe, find the location with me most tweets
    
    Parameters
    ----------
    df: dataframe of the modified Twitter dataset
    
    Returns
    ------
    a dataframe with the user ID as index and the coordinates of the location with the most tweets per user
    """

    # counter
    df['numTweets'] = 1
    # aggregated dataframe by user ID and location
    df_agg = df.groupby(by=['userId', 'reducedAccuracy'], as_index=False)['numTweets'].count().set_index('userId')
    # sort in descending according to number of tweets
    df_agg = df_agg.sort_values('numTweets', ascending=False).reset_index()
    # for each group take the first value, i.e. the location with the highest number of tweets
    result = df_agg.groupby(by='userId').first()
    # give meaningful names
    result.columns = ['frequentLocation', 'numTweets']
    return result

def get_freq_loc_coordinates(row):
    """
    From given row, extract latitude and longitude from the coordinates tuple
    
    Parameters
    ----------
    row: row of dataframe 
    
    Returns
    ------
    new row with latitude and longitude information
    """

    # extract lat and long from coordinates tuple
    lat, long = row['frequentLocation'] 
    row['frequentLatitude'] = float(lat)
    row['frequentLongitude'] = float(long)
    return row

def home_is_work(row):
    """
    Check is workplace is same as home
    
    Parameters
    ----------
    row: dataframe row
    
    Returns
    ------
    new dataframe row
    """

    # check if home == work
    if (row['homeLatitude'] == row['workLatitude']) and (row['homeLongitude'] == row['workLongitude']):
        row['homeIsWork'] = True
    return row

def create_swiss_map(year, workplace_coord, homeplace_coord, user_ids, show_all_users=True, user_id=None):
    """
    Creates a map with workplaces and home coordinates for each user
    
    Parameters
    ----------
    year: year of analysis
    workplace_coord: list of tuples with workplace coordinates
    homeplace_coord: list of tuples with homeplace coordinates
    user_ids: list of user IDs
    show_all_users: True if all users should be displayed
    user_id: user ID for particular user to be plotted
    
    Returns
    ------
    a map with workplace and homeplace locations
    """

    # load swiss map data
    canton_geo = r'../../data/maps/ch-cantons.topojson.json'

    # create map object
    swiss_map = folium.Map(location=[46.762579, 7.927242], zoom_start=7)

    if show_all_users:
        # iterate through the workplace location of all users
        for index, (lat, long) in enumerate(workplace_coord):
            # create popup text
            popup_text = 'User: ' + str(user_ids[index])
            # create marker for workplace location
            folium.CircleMarker(location=(lat,long), radius=500, 
                                color='darkblue', fill_color='darkblue', fill_opacity=0.7, 
                                popup=popup_text).add_to(swiss_map)
        # iterate through the homeplace location of all users
        for index, (lat, long) in enumerate(homeplace_coord):
            # create popup text
            popup_text = 'User: ' + str(user_ids[index])
             # create marker for homeplace location
            folium.CircleMarker(location=(lat,long), radius=500, 
                                color='red', fill_color='red', fill_opacity=0.7, 
                                popup=popup_text).add_to(swiss_map)
        # save map
        map_name = '../../data/maps/home_and_work_' + str(year) + '.html'
        swiss_map.save(map_name)
        return swiss_map
    else:
        try:
            # check if given user ID is valid
            index = user_ids.index(user_id)
            # create popup text
            popup_text = 'User: ' + str(user_id)
            # find workplace for particular user
            (lat, long) = workplace_coord[index]
            # create marker
            folium.CircleMarker(location=(lat,long), radius=5000, 
                                color='darkblue', fill_color='darkblue', fill_opacity=1, 
                                popup=popup_text).add_to(swiss_map)
            # find homeplace for particular user
            (lat, long) = homeplace_coord[index]
            # create popup text
            popup_text = 'User: ' + str(user_ids[index])
            # create marker
            folium.CircleMarker(location=(lat,long), radius=5000, 
                                color='red', fill_color='red', fill_opacity=1, popup=popup_text).add_to(swiss_map)
            # save_map
            map_name = '../../data/maps/home_and_work_individual_' + str(year) + '.html'
            swiss_map.save(map_name)
            return swiss_map
        except:
            # print error message
            print('Not a valid user ID')
            return

def get_travel_info(row, gmaps, debug=True):
    """
    Get time and distance to work using the googlemaps API
    
    Parameters
    ----------
    row: row of dataframe
    gmaps: googlemaps object
    debug: if True, print debug message
    
    Returns
    ------
    new row that contains travel information
    """

    # get distance and time from home to work
    try:
        travel_info = gmaps.distance_matrix((row['homeLatitude'], row['homeLongitude']), (row['workLatitude'], row['workLongitude']))
    except:
        if debug:
            print('API limit exceeded')
        return row
    try:
        distance = travel_info['rows'][0]['elements'][0]['distance']['value']
    except:
        if debug:
            print('Invalid response for distance')
        distance = np.nan
    try:
        time = int(travel_info['rows'][0]['elements'][0]['duration']['value'])
    except:
        if debug:
            print('Invalid response for time')
        time = np.nan
    # put distance and time into row
    row['distance'] = distance
    row['time'] = time
    if debug:
        print('Successful gmaps API call')
    return row

def find_cantons(row, gmaps, debug=True):
    """
    Finds the canton of residence and work

    Parameters
    ----------
    row: dataframe row
    gmaps: googlemaps object
    debug: if True, print debug message

    Returns
    ------
    new row with canton information
    """

    # set home coordinates
    home = (row['homeLatitude'], row['homeLongitude'])
    # get result from API
    try:
        home_result = gmaps.reverse_geocode(home)
    except:
        return row
    # iterate through result and find canton
    try:
        for d in home_result[0]['address_components']:
            if d['types'][0] == 'administrative_area_level_1':
                row['homeCanton'] = d['short_name']
                break
    except:
        return row
    # set workplace coordinates
    work = (row['workLatitude'], row['workLongitude'])
    # get result from API
    try:
        work_result = gmaps.reverse_geocode(work)
    except:
        return row
    # iterate through result and find canton
    try:
        for d in work_result[0]['address_components']:
            if d['types'][0] == 'administrative_area_level_1':
                row['workCanton'] = d['short_name']
                break
    except:
        return row
    if debug:
        print('Successful API call')
    return row

def visualize_gyration_radius(short_distance, year):
    """
    Creates a map with the radius of gyrations for users
    
    Parameters
    ----------
    short_distance: dataframe with gyration information and home location for each user
    year: year of analysis
    
    Returns
    -------
    folium object
    """

    canton_geo = r'../../data/ch-cantons.topojson.json'
    # data used for visualization
    map_data = [list(x) for x in short_distance.values]

    swiss_map = folium.Map(location=[45.9, 7.9], zoom_start=7)

    for lat, long, gyr in map_data:
        # create circle market, radius should be given in meters
        folium.CircleMarker(location=(lat,long), radius=gyr * 1000, color='lightblue', 
                            fill_color='blue', fill_opacity=0.5).add_to(swiss_map)
        folium.Marker((lat,long)).add_to(swiss_map)

    # save map
    map_name = '../../data/maps/gyration_' + str(year) + '.html'
    swiss_map.save(map_name)
    return swiss_map

def load_all_files(pattern):
    """
    Creates a dataframe with data from all years

    Parameters
    ----------
    pattern: pattern of file names to be searched

    Returns
    -------
    a dataframe with travel information from all years that have been analyzed
    """

    # path to files
    path = '../../data/'
    # pattern for files
    pattern = pattern + '*'
    # find all files that match the pattern
    all_files = glob.glob(path + pattern)
    # initialize dataframe
    frame = pd.DataFrame()
    # initialize list
    list_ = []
    # iterate through all files and create an aggregated dataframe
    for file_ in all_files:
        df = pd.read_csv(file_, sep='|')
        year = re.findall('\d+', file_)[0]
        df['year'] = int(year)
        list_.append(df)
    # create dataframe
    frame = pd.concat(list_)
    frame.reset_index(inplace=True, drop=True)
    # return dataframe
    return frame

def visualize_graph(graph_data, swiss_cantons, seed=1):

    """
    Build a network representation of where people live and where they work
    
    Parameters
    ----------
    graph_data: dataframe to be used for visualization
    swiss_cantons: dictionary with swiss cantons
    seed: integer for random number generator
    """
    
    # initialize graph
    G=nx.DiGraph()
    # dict for labels
    labels = {}
    
    # add edges to graph and build labels dict
    for _, values in graph_data.iterrows():
        np.random.seed(seed)
        # add edge (from, to, weight)
        G.add_edge(values['homeCanton'], values['workCanton'], weight=values['sum'])
        labels[(values['homeCanton'], values['workCanton'])] = values['sum']

    # configure plotting settings
    plt.figure(figsize=(25, 25))
    plt.axis('off')
    # positions for all nodes
    pos=nx.spring_layout(G, scale=100)
    # draw network
    nx.draw_networkx_nodes(G, pos, node_size=1500)
    # non-swiss nodes are green and square
    non_swiss = [node for node in G.nodes() if node not in swiss_cantons.keys()]
    nx.draw_networkx_nodes(G, pos, node_size=1700, node_shape='s', nodelist=non_swiss, node_color='g')
    # fix network edges
    
    # build weights for labels - aggregated traffic between points U and V
    weight_labels = Counter()
    for (u,v,d) in G.edges(data=True):
        # weight variable
        w = d['weight']
        # set (u,v) and (v,u) to have the same weight
        if u != v:
            weight_labels[(u,v)] += int(w)
            weight_labels[(v,u)] += int(w)
        else:
            weight_labels[(u,v)] += int(w)

    for (u,v,d) in G.edges(data=True):
        nx.draw_networkx_edges(G, pos, edgelist=[(u,v)], width=d['weight'] / 10.0)
    # put labels on edges
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weight_labels, font_size=20)
    # put labels on nodes
    nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
    # display
    plt.show()

def estimate_avg_gyration(group):
    """
    Estimates the average radius of gyration according to a formula given in the notebook

    Parameters
    ----------
    group: subset of dataframe after the groupby operation

    Returns
    -------
    the average radius of gyration
    """
    
    if group.shape[0] > 1:
        # apply formula as given in the notebook
        avg_gyration = np.sqrt(np.sum((group.tweets - 1) * (group.gyration ** 2)) / np.sum(group.tweets - 1))
        d = {'avg_gyration': avg_gyration}
        # return pd.Series(data=d)
        return avg_gyration
    d = {'avg_gyration': group.gyration.iloc[0]}
    # return pd.Series(data=d)
    return group.gyration.iloc[0]

def different_canton(label):
    """
    Takes a label in the form (x,y) and checks if x is equal to y
    
    Parameters
    ----------
    label: xtick text of the form "(x,y)"
    
    Returns
    -------
    True or False depending on x == y
    """
    
    # keep only canton of work and residence
    label = label[1:-1].split(', ')    
    # check if they are the same
    if label[0] == label[1]:
        return False
    return True
from libraries import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def remove_token(token):
    """
    Decides if a token starts with #, @ and http (URL)

    Parameters
    ----------
    token: token string

    Returns
    -------
    True or False
    """

    if token.startswith('#'):
        return True
    if token.startswith('@'):
        return True
    if token.startswith('http'):
        return True
    return False

def clean_tweet_text(text):
    """
    Removes tokens with #, @ and http (URLs) from tweet string

    Parameters
    ----------
    text: tweet text

    Returns
    -------
    cleaned tweet text without words starting with #, @ and http
    """

    # get tokens
    tokens = text.strip().split()
    # filter tokens
    cleaned_text = [token for token in tokens if not remove_token(token)]
    # return filtered text
    return ' '.join(cleaned_text)

def get_sentiment(row, analyzer, translate, debug=True):
    """
    Translates tweet text to English and estimates the sentiment score

    Parameters
    ----------
    row: row of dataframe
    analyzer: SentimentIntensityAnalyzer() object
    translate: Yandex translator
    debug: if True, print debug message

    Returns
    -------
    updated row
    """

    # get row text
    text = row['text']
    # get language
    from_lang = row['language']
    # target language for translation
    to_lang = "en"
    # already translated
    if row['translated'] == 'yes':
        return row
    # no translation needed
    if (from_lang == "en"):
        translation = text
    # translation needed
    else:
        try:
            response = translate.translate(text, 'en')
            translation = response['text'][0]
        except:
            return row
    # get sentiment score for the text
    vs = analyzer.polarity_scores(translation)
    row['compound'] = vs['compound']
    row['translated'] = 'yes'
    # return score
    if debug:
        print('Successful yandex API call')
    return row

def normalize_sentiment(subgroup):
    """
    Normalizes the compound sentiment per subgroup. Sums the compound sentiment score and divides 
    by the total number of tweets per event. The final score is in [-1,1]
    
    Parameters
    ----------
    subgroup: subgroup of dataframe
    
    Returns
    -------
    normalized compound sentiment score per event
    """
    
    return subgroup['compound'].sum() / subgroup.shape[0]

def weighted_transform(subgroup):
    """
    Finds the weighted compound sentiment score for each event and the total number of users per event
    
    Parameters
    ----------
    subgroup: dataframe subgroup
    
    Returns
    -------
    a new dataframe with columns [compound, usersPerHashtag]
    """
    
    # find total users per hashtag
    total_users = subgroup['usersPerHashtag'].sum()
    # estimate the weighted compound score
    weigthed_compound = (subgroup['compound'] * subgroup['usersPerHashtag']).sum() / total_users
    # build dictionary
    d = {'compound': weigthed_compound, 'usersPerHashtag': total_users}
    # return dictionary as dataframe
    return pd.Series(data=d)

def group_sentiment_score(by='hashtag', data=None):
    """
    Performs a groupby operation on the given data to find the aggregated compound score
    
    Parameters
    ----------
    by: attribute on which the aggregation is performed. Should be either 'hashtag' or 'area'
    data: dataframe on which the aggregation is performed
    
    Returns
    -------
    An aggregated dataframe
    """
    
    # perform the group by operation and use the weighted_transform function
    grouped_sentiment = data[['hashtag', 'compound', 'usersPerHashtag', 'area']].groupby(
        by=by).apply(weighted_transform)
    # reset index
    grouped_sentiment.reset_index(inplace=True)
    # return result
    return grouped_sentiment

def visualize_sentiment_score(data=None, threshold=1, x_axis='hashtag', year=''):
    """
    Visualizes the sentiment score in a barplot
    
    Parameters
    ----------
    data: dataframe used for visualization
    threshold: numbed of points in the x-axis, i.e. number of bars
    x_axis: attribute to be used for the values of x
    year: year to be analyzed
    """
    
    sns.set_context("poster")
    # sort values in descending order
    data.sort_values(by='usersPerHashtag', ascending=False, inplace=True)
    # take the first 'threshold' values
    data = data.head(threshold)
    # build the colormap based on the sentiment score
    index = np.arange(len(data))
    color_data = data['compound'].values
    colors = cm.winter(color_data / float(max(color_data)))
    plt.figure(figsize=(15,10))
    plot = plt.scatter(color_data, color_data, c=color_data, cmap='winter')
    plt.clf()
    # plot the colorbar
    colorbar = plt.colorbar(plot)
    colorbar.set_label('Compound sentiment', rotation=270, labelpad=20)
    # plot the bars
    fig = sns.barplot(x=x_axis, y='usersPerHashtag', data=data, palette=colors)
    labels = data[x_axis].values
    fig.set_xticklabels(labels, rotation=90)
    plot_title = 'Compound sentiment score per ' + x_axis
    sns.plt.title(plot_title)
    fig.set(xlabel=x_axis.capitalize(), ylabel='Number of users')
    for txt in fig.texts:
        txt.set_visible(False)
    # file name
    file_name = '../../data/figures/sentiment_' + x_axis + '_' + year + '.png'
    plt.savefig(file_name, bbox_inches='tight')
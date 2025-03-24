from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

# Load stop words once to avoid multiple file I/O operations
with open('stop_hinglish.txt', 'r') as f:
    STOP_WORDS = set(f.read().split())

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    num_messages = df.shape[0]
    words = sum(len(message.split()) for message in df['message'])
    num_media_messages = df.query("message == '<Media omitted>\n'").shape[0]
    num_links = sum(len(extract.find_urls(message)) for message in df['message'])

    return num_messages, words, num_media_messages, num_links

def most_busy_users(df):
    user_counts = df['user'].value_counts()
    percent_users = round((user_counts / df.shape[0]) * 100, 2).reset_index()
    percent_users.columns = ['name', 'percent']
    return user_counts.head(), percent_users

def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    df = df.query("user != 'group_notification' and message != '<Media omitted>\n'")

    def remove_stop_words(message):
        return " ".join([word.lower() for word in message.split() if word.lower() not in STOP_WORDS])

    df['message'] = df['message'].apply(remove_stop_words)
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    return wc.generate(df['message'].str.cat(sep=" "))

def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    df = df.query("user != 'group_notification' and message != '<Media omitted>\n'")

    words = [word.lower() for message in df['message'] for word in message.split() if word.lower() not in STOP_WORDS]

    return pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    emojis = [c for message in df['message'] for c in message if c in emoji.EMOJI_DATA]

    return pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    timeline = df.groupby(['year', 'month_num', 'month']).size().reset_index(name='message_count')
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    return df.groupby('only_date').size().reset_index(name='message_count')

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df.query("user == @selected_user")

    return df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

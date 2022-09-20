from textblob import TextBlob
import os
import pandas as pd
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.util import ngrams
from nltk.tokenize.treebank import TreebankWordDetokenizer
import warnings
warnings.filterwarnings('ignore')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
stop_words=set(stopwords.words('english'))

def associated_bag_of_words(data, occurences, folder, name):
    title_data=data['product.name'].fillna('')
    phrase_counter=Counter()
    title_list=[]

    #get most common associated words
    for title in title_data:
        title_list.append(title.lower())
        for sentence in sent_tokenize(title):
            words=word_tokenize(sentence)
            for phrase in ngrams(words, 3):
                phrase_counter[TreebankWordDetokenizer().detokenize(phrase)]+=1
    most_common_words=phrase_counter.most_common(occurences)
    most_common_words_list=[]
    for word, occurence in most_common_words:
        most_common_words_list.append(word)
    file_path=os.path.join(folder, name+'.txt')
    with open(file_path, 'w') as fp:
        fp.write('\n'.join(str(item) for item in most_common_words_list))
        fp.close()
    return most_common_words_list

def bag_of_words(data, occurences):
    title_data=data['product.name'].fillna('')
    vectorizer=CountVectorizer(ngram_range=(1,1), stop_words='english')
    title_vectorized=vectorizer.fit_transform(title_data)
    title_df=pd.DataFrame(title_vectorized.toarray(), columns=vectorizer.get_feature_names())
    total_occurences=[]
    occurence_position=[]
    for i in range(len(title_df.columns)):
        location=title_df.iloc[:,i]
        total_occurences.append(location.sum())
        occurence_position.append(i)
    occurence_df=pd.DataFrame({'position':occurence_position, 'Occurence':total_occurences})
    occurence_df=occurence_df.sort_values(by=['Occurence'], ascending=False)
    occurence_list=occurence_df['position'].tolist()
    bag_of_words_df=pd.DataFrame()
    for j in range(occurences):
        bag_of_words_df[title_df.columns[occurence_list[j]]]=title_df[title_df.columns[occurence_list[j]]]
    return bag_of_words_df
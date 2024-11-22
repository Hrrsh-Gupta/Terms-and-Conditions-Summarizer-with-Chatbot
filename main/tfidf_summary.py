from nltk import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from numpy import argsort
import networkx as nx
from networkx import from_numpy_array, pagerank
from nltk.tokenize import sent_tokenize
import re

# nltk.download('punkt_tab')


# def preprocess_text(text):
#     sentences = sent_tokenize(text)  # Split text into sentences
#     return sentences


def preprocess_text(text):
    # Remove hyperlinks
    text = re.sub(r'http[s]?://\S+', '', text)  # Matches and removes URLs
    text = re.sub(r'www\.\S+', '', text)  # Matches and removes URLs starting with www
    
    # Split text into sentences
    sentences = sent_tokenize(text)
    return sentences

def tfidf_summarize(text, n=5):
    sentences = preprocess_text(text)
    
    # Vectorize sentences using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)
    
    # Compute similarity between sentences
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Rank sentences based on the sum of their similarity scores
    sentence_scores = similarity_matrix.sum(axis=1)
    ranked_sentences = [sentences[i] for i in argsort(sentence_scores)[-n:]]
    
    # Join top-ranked sentences to form the summary
    summary = ' '.join(ranked_sentences)
    return summary


def textrank_summarize(text, n=5):
    sentences = preprocess_text(text)
    
    # Vectorize sentences using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)
    
    # Compute similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Build graph and rank sentences with TextRank
    nx_graph = from_numpy_array(similarity_matrix)
    scores = pagerank(nx_graph)
    
    # Rank sentences by score
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    
    # Select top-ranked sentences for the summary
    summary = ' '.join([sentence for _, sentence in ranked_sentences[:n]])
    return summary


def hybrid_summary(tfidf_summary, textrank_summary, threshold=0.5):
    combined_summary = []
    tfidf_sentences = tfidf_summary.split('.')
    textrank_sentences = textrank_summary.split('.')
    
    vectorizer = TfidfVectorizer().fit(tfidf_sentences + textrank_sentences)
    tfidf_vectors = vectorizer.transform(tfidf_sentences)
    textrank_vectors = vectorizer.transform(textrank_sentences)
    
    for i, tfidf_vec in enumerate(tfidf_vectors):
        for j, textrank_vec in enumerate(textrank_vectors):
            similarity = cosine_similarity(tfidf_vec, textrank_vec)[0, 0]
            if similarity >= threshold:
                combined_summary.append(tfidf_sentences[i].strip())
                break
    
    unique_textrank = [sent.strip() for i, sent in enumerate(textrank_sentences) 
                       if not any(cosine_similarity(textrank_vectors[i], tfidf_vec)[0, 0] >= threshold 
                                  for tfidf_vec in tfidf_vectors)]
    
    combined_summary.extend(unique_textrank)
    return '. '.join(combined_summary) + '.'

def read_text_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def st_generate_summary(text, reducing_factor = 6):
    n = len(text.split(". "))// reducing_factor
    tfidf_summary = tfidf_summarize(text, n)
    textrank_summary = textrank_summarize(text, n)

    # for sentence in textrank_summary.split(". "):
    #     print(sentence)

    final_summary = hybrid_summary(tfidf_summary, textrank_summary)
    return final_summary

#-----------------------------------------------------------------------------------------------------------------------
# text = read_text_file(".//dataset//apple.txt")

# n = len(text.split(". "))//6
# tfidf_summary = tfidf_summarize(text, n)
# textrank_summary = textrank_summarize(text, n)

# # for sentence in textrank_summary.split(". "):
# #     print(sentence)

# final_summary = hybrid_summary(tfidf_summary, textrank_summary)



    
# print(final_summary)

from numpy import mean
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from regex import match, sub

from nltk import pos_tag


topics = {
    "Intellectual Property": ["intellectual property", "copyright", "trademark", "ownership", "license", "trade secrets", "patent", "intellectual rights"],
    "Governing Law": ["jurisdiction", "governing law", "disputes", "arbitration", "enforceable"],
    "Terms and Conditions": ["terms and conditions", "agreement", "contract", "acceptance", "binding terms", "agreement terms", "usage terms"],
    "Privacy Agreements": ["privacy", "data", "collection", "consent", "security"],
    "Excuse Yourself of Liability": ["liability", "disclaimer", "responsibility", "waiver", "limited liability", "personal information", "data privacy"],
    "Payments": ["payment", "billing", "subscription", "charge", "fee", "payment terms", "recurring fees", "financial obligations"],
    "Termination": ["termination", "suspension", "violation", "account suspension", "cancellation","deactivate"],
    "Liability Limitations": ["limitation of liability", "damages", "indirect damages", "loss", "damage limitation"],
    "Conditions of Use": ["conditions of use", "user conduct", "acceptable use", "restrictions", "user obligations"],
    "Refund Policy": ["refund policy", "refund", "returns", "money back","return eligibility","cashback","payment reimbursement", "refund conditions"],
    "Changes to the Agreement": ["change", "modify", "update", "revision", "notification", "agreement adjustments", "policy alterations"],
    "Contact Information": ["customer support","contact", "support", "email", "address", "communication","helpdesk", "service inquiries"],
    "Effective Date": ["effective date", "commencement", "start date", "start of terms"],
    "System Requirements": ["software compatibility","technical requirements", "system requirements", "hardware", "software"],
    "User Limitations": ["user restrictions", "not permitted", "prohibited actions","prohibited conduct", "non-compliance"],
    "Product Warranties or Guarantees": ["warranty", "guarantee","product guarantees", "coverage limitations"],
    "Warranty Disclaimer Clause": ["warranty disclaimer", "as is", "no guarantees","no responsibility", "non-liability"]
}

# buzzwords = [
#     "herein", "thereof", "whereas", "hereinafter", "therefore", "such", "additional",
#     "further", "notwithstanding", "including but not limited to", "subject to", "as applicable",
#     "in accordance with", "pursuant to", "thereto", "hereby"
# ]

LEGAL_KEYWORDS = {
    "obligations": ["shall", "must", "agree", "required", "obliged"],
    "permissions": ["may", "allow", "permit", "authorize"],
    "prohibitions": ["prohibited", "restricted", "not allowed", "forbidden"],
    "liability_terms": ["liability", "indemnity", "damages", "warranty", "disclaimer"],
    "termination_terms": ["terminate", "suspend", "cancel", "revocation"],
}

buzzwords = []


def preprocess_text(text):
    sentences = sent_tokenize(text)
    cleaned_sentences = []
    stop_words = set(stopwords.words('english'))
    
    for sentence in sentences:
        # Filter out uppercase headers or short, non-informative phrases
        if sentence.isupper() or match(r'^[A-Z]\.\s+[A-Z\s]+$', sentence) or len(sentence.split()) < 2:
            continue
        
        # Remove non-word characters and filter buzzwords and stopwords
        words = word_tokenize(sentence.lower())
        words = [sub(r'\W+', '', word) for word in words]
        words = [word for word in words if word not in stop_words and word not in buzzwords and word.isalpha()]
        
        # Only keep sentences that are longer than two words and are not just numbers/letters
        if len(words) > 3:
            cleaned_sentences.append(' '.join(words))
        
    return cleaned_sentences, sentences

def is_meaningful(sentence):
    tokens = word_tokenize(sentence)
    pos_tags = pos_tag(tokens)
    
    # Check for presence of nouns and verbs (general meaningfulness)
    has_noun = any(tag.startswith('N') for _, tag in pos_tags)
    has_verb = any(tag.startswith('V') for _, tag in pos_tags)
    
    # Check for legal keywords
    has_legal_keyword = any(token.lower() in word_list for token in tokens for word_list in LEGAL_KEYWORDS.values())
    
    # Sentence is considered meaningful if it contains both noun and verb or a legal keyword
    return (has_noun and has_verb) or has_legal_keyword


def classify_sentences_by_topic(cleaned_sentences, topics):
    sentence_topics = {}
    
    # Preprocess topics to lowercase and set keywords for faster lookup
    processed_topics = {topic: set(keyword.lower() for keyword in keywords) for topic, keywords in topics.items()}
    
    for i, sentence in enumerate(cleaned_sentences):
        words = set(word.lower() for word in sentence.split())
        
        if len(words) <= 2:
            continue
        
        for topic, keywords in processed_topics.items():
            if keywords.intersection(words):
                sentence_topics.setdefault(topic, []).append(i)
                break  # Stop checking other topics once a match is found

    return sentence_topics


def apply_lsa(cleaned_sentences, n_topics=6):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned_sentences)
    
    lsa = TruncatedSVD(n_components=n_topics)
    lsa_matrix = lsa.fit_transform(tfidf_matrix)
    
    return lsa_matrix, vectorizer

def mmr_selection(topic_sentences, lsa_matrix, lambda_param=0.9, num_sentences=2):
    selected_sentences = []
    unselected = topic_sentences[:]
    
    selected_sentences.append(unselected.pop(0))
    
    while len(selected_sentences) < num_sentences and unselected:
        max_mmr = -float("inf")
        best_sentence = None
        
        for i in unselected:
            relevance = cosine_similarity(lsa_matrix[i].reshape(1, -1), mean(lsa_matrix[selected_sentences], axis=0).reshape(1, -1)).flatten()[0]
            redundancy = max(cosine_similarity(lsa_matrix[i].reshape(1, -1), lsa_matrix[j].reshape(1, -1))[0][0] for j in selected_sentences)
            
            mmr_score = lambda_param * relevance - (1 - lambda_param) * redundancy
            if mmr_score > max_mmr:
                max_mmr = mmr_score
                best_sentence = i
                
        selected_sentences.append(best_sentence)
        unselected.remove(best_sentence)
    
    return selected_sentences

def ag_generate_summary(text, num_sentences=3):
    cleaned_sentences, original_sentences = preprocess_text(text)
    sentence_topics = classify_sentences_by_topic(cleaned_sentences, topics)
    lsa_matrix, vectorizer = apply_lsa(cleaned_sentences)
    
    summary = {}
    selected_memory = set()
    
    for topic, sentence_indices in sentence_topics.items():
        if not sentence_indices:
            continue
        
        selected_indices = mmr_selection(sentence_indices, lsa_matrix, num_sentences=num_sentences)
        valuable_sentences = [original_sentences[i] for i in selected_indices if i not in selected_memory]
        
        if valuable_sentences:
            summary[topic] = valuable_sentences
            selected_memory.update(selected_indices)
    
    return summary


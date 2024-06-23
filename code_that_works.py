import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse
import numpy as np
def classify_link(href):
    if href.startswith('http'):
        return 'External Links'
    elif href.startswith('#'):
        return 'Internal Links (Anchors)'
    elif href.startswith('mailto:'):
        return 'Email Links'
    elif href.startswith('tel:'):
        return 'Phone Links'
    elif re.search(r'\.(jpg|jpeg|png|gif|svg)$', href, re.IGNORECASE):
        return 'Image Links'
    elif re.search(r'(facebook|twitter|instagram|linkedin)', href, re.IGNORECASE):
        return 'Social Media Links'
    else:
        return 'Other Links'

def get_backlink_counts(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        img_links = soup.find_all('img', src=True)
        social_media_links = soup.find_all(href=re.compile(r'(facebook|twitter|instagram|linkedin)'))
        backlink_counts = Counter()
        for link in links:
            href = link['href']
            link_type = classify_link(href)
            backlink_counts[link_type] += 1
        for img_link in img_links:
            href = img_link['src']
            link_type = classify_link(href)
            backlink_counts[link_type] += 1
        for social_link in social_media_links:
            href = social_link['href']
            link_type = classify_link(href)
            backlink_counts[link_type] += 1
        for link_type, count in backlink_counts.items():
            print(link_type + ":", count)
    else:
        print("Error:", response.status_code)
        
def get_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        return links
    except Exception as e:
        print("Error:", e)
        return []
def categorize_link(link):
    categories = {
        'Science': ['science', 'research', 'physics', 'chemistry', 'astronomy','beaker','biochemistry','biology','botany','Bunsen','burnerburette'],
        'Art': ['art', 'painting', 'sculpture', 'gallery', 'artist'],
        'Entertainment': ['entertainment', 'movies', 'music', 'celebrities', 'cinema', 'film'],
        'Fashion': ['fashion', 'clothing', 'style', 'designer', 'apparel'],
        'Food': ['food', 'cooking', 'recipe', 'restaurant', 'cuisine', 'chef'],
        'Health & Wellness': ['health', 'wellness', 'fitness', 'nutrition', 'diet', 'exercise'],
        'Technology': ['technology', 'tech', 'innovation', 'gadget', 'electronics'],
        'Education': ['education', 'learning', 'school', 'university', 'college'],
        'Travel & Tourism': ['travel', 'tourism', 'vacation', 'destination', 'hotel'],
        'Business & Finance': ['business', 'finance', 'economy', 'money', 'investment', 'stock'],
        'Sports': ['sports', 'athletics', 'fitness', 'exercise', 'competition'],
        'Environment': ['environment', 'climate', 'sustainability', 'green', 'ecology'],
        'Politics': ['politics', 'government', 'policy', 'election', 'democracy'],
        'Social Media': ['social media', 'facebook', 'twitter', 'instagram', 'linkedin']
    }
    for category, keywords in categories.items():
        for keyword in keywords:
            if re.search(r'\b{}\b'.format(keyword), link, re.IGNORECASE):
                return category
    return 'Other'
def categorize_links(links):
    categorized_links = {}
    for link in links:
        category = categorize_link(link)
        if category in categorized_links:
            categorized_links[category].append(link)
        else:
            categorized_links[category] = [link]
    return categorized_links

def get_backlinks(url):
    domain = urlparse(url).netloc
    backlinks = []
    try:
        response = requests.get("https://www.google.com/search?q=link:{}&num=100".format(domain))
        soup = BeautifulSoup(response.content, 'html.parser')
        for cite in soup.find_all('cite'):
            backlink = cite.text.strip()
            if domain not in backlink:
                backlinks.append(backlink)
        return backlinks
    except Exception as e:
        print("Error:", e)
        return []


def get_link_transitions(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        link_transitions = Counter()
        for link in links:
            href = link['href']
            if not href or href.startswith('#'):
                continue
            source_category = categorize_link(url)
            target_category = categorize_link(href)
            if source_category != target_category:
                link_transitions[(source_category, target_category)] += 1

        return link_transitions
    else:
        print("Error:", response.status_code)
        return Counter()
    

def Transition_matrix(categorized_links,link_transitions, categories):

    n = len(categories)
    matrix = np.zeros((n, n))
    total_links = sum(link_transitions.values())

    for source_category, target_category in link_transitions.keys():
        source_index = categories.index(source_category)
        target_index = categories.index(target_category)
        matrix[source_index, target_index] = link_transitions[(source_category, target_category)]
        if source_index==target_index:
            matrix[source_index,target_index]=0
    for i in range(n):
        if sum(matrix[i]) > 0:
            matrix[i] /= sum(matrix[i])
        else:
            
            matrix[i] = np.ones(n) / (n)

    return (matrix[0],matrix)

def main(url):
    links = get_links(url)
    link_transitions = get_link_transitions(url)

    print("Categorized Links:")
    categorized_links = categorize_links(links)
    for category, links in categorized_links.items():
        if category != "Other":
            print(category, ":", len(links))
    max_value=max(categorized_links.values())
    for key,value in categorized_links.items():
        if value==max_value:
            print(f"Central theme of the website is {key}.")
    
    categories = list(categorized_links.keys())
    transition_most,transition_matrix = Transition_matrix(categorized_links,link_transitions, categories)
    print("\nMost Probable transitions:")
    print(transition_most)
    
    print("Transition Matrix:")
    print(transition_matrix)


url = "https://en.wikipedia.org/wiki/Markov_chain"  
main(url)
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse
import numpy as np
def classify_link(href):
    if href.startswith('http'):
        return 'External Links'
    elif href.startswith('#'):
        return 'Internal Links (Anchors)'
    elif href.startswith('mailto:'):
        return 'Email Links'
    elif href.startswith('tel:'):
        return 'Phone Links'
    elif re.search(r'\.(jpg|jpeg|png|gif|svg)$', href, re.IGNORECASE):
        return 'Image Links'
    elif re.search(r'(facebook|twitter|instagram|linkedin)', href, re.IGNORECASE):
        return 'Social Media Links'
    else:
        return 'Other Links'

def get_backlink_counts(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        img_links = soup.find_all('img', src=True)
        social_media_links = soup.find_all(href=re.compile(r'(facebook|twitter|instagram|linkedin)'))
        backlink_counts = Counter()
        for link in links:
            href = link['href']
            link_type = classify_link(href)
            backlink_counts[link_type] += 1
        for img_link in img_links:
            href = img_link['src']
            link_type = classify_link(href)
            backlink_counts[link_type] += 1
        for social_link in social_media_links:
            href = social_link['href']
            link_type = classify_link(href)
            backlink_counts[link_type] += 1
        for link_type, count in backlink_counts.items():
            print(link_type + ":", count)
    else:
        print("Error:", response.status_code)
        
def get_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        return links
    except Exception as e:
        print("Error:", e)
        return []
def categorize_link(link):
    categories = {
        'Science': ['science', 'research', 'physics', 'chemistry', 'astronomy','beaker','biochemistry','biology','botany','Bunsen','burnerburette'],
        'Art': ['art', 'painting', 'sculpture', 'gallery', 'artist'],
        'Entertainment': ['entertainment', 'movies', 'music', 'celebrities', 'cinema', 'film'],
        'Fashion': ['fashion', 'clothing', 'style', 'designer', 'apparel'],
        'Food': ['food', 'cooking', 'recipe', 'restaurant', 'cuisine', 'chef'],
        'Health & Wellness': ['health', 'wellness', 'fitness', 'nutrition', 'diet', 'exercise'],
        'Technology': ['technology', 'tech', 'innovation', 'gadget', 'electronics'],
        'Education': ['education', 'learning', 'school', 'university', 'college'],
        'Travel & Tourism': ['travel', 'tourism', 'vacation', 'destination', 'hotel'],
        'Business & Finance': ['business', 'finance', 'economy', 'money', 'investment', 'stock'],
        'Sports': ['sports', 'athletics', 'fitness', 'exercise', 'competition'],
        'Environment': ['environment', 'climate', 'sustainability', 'green', 'ecology'],
        'Politics': ['politics', 'government', 'policy', 'election', 'democracy'],
        'Social Media': ['social media', 'facebook', 'twitter', 'instagram', 'linkedin']
    }
    for category, keywords in categories.items():
        for keyword in keywords:
            if re.search(r'\b{}\b'.format(keyword), link, re.IGNORECASE):
                return category
    return 'Other'
def categorize_links(links):
    categorized_links = {}
    for link in links:
        category = categorize_link(link)
        if category in categorized_links:
            categorized_links[category].append(link)
        else:
            categorized_links[category] = [link]
    return categorized_links

def get_backlinks(url):
    domain = urlparse(url).netloc
    backlinks = []
    try:
        response = requests.get("https://www.google.com/search?q=link:{}&num=100".format(domain))
        soup = BeautifulSoup(response.content, 'html.parser')
        for cite in soup.find_all('cite'):
            backlink = cite.text.strip()
            if domain not in backlink:
                backlinks.append(backlink)
        return backlinks
    except Exception as e:
        print("Error:", e)
        return []


def get_link_transitions(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        link_transitions = Counter()
        for link in links:
            href = link['href']
            if not href or href.startswith('#'):
                continue
            source_category = categorize_link(url)
            target_category = categorize_link(href)
            if source_category != target_category:
                link_transitions[(source_category, target_category)] += 1

        return link_transitions
    else:
        print("Error:", response.status_code)
        return Counter()
    

def Transition_matrix(categorized_links,link_transitions, categories):

    n = len(categories)
    matrix = np.zeros((n, n))
    total_links = sum(link_transitions.values())

    for source_category, target_category in link_transitions.keys():
        source_index = categories.index(source_category)
        target_index = categories.index(target_category)
        matrix[source_index, target_index] = link_transitions[(source_category, target_category)]
        if source_index==target_index:
            matrix[source_index,target_index]=0
    for i in range(n):
        if sum(matrix[i]) > 0:
            matrix[i] /= sum(matrix[i])
        else:
            
            matrix[i] = np.ones(n) / (n)

    return (matrix[0],matrix)

def main(url):
    links = get_links(url)
    link_transitions = get_link_transitions(url)

    print("Categorized Links:")
    categorized_links = categorize_links(links)
    for category, links in categorized_links.items():
        if category != "Other":
            print(category, ":", len(links))
    max_value=max(categorized_links.values())
    for key,value in categorized_links.items():
        if value==max_value:
            print(f"Central theme of the website is {key}.")
    
    categories = list(categorized_links.keys())
    transition_most,transition_matrix = Transition_matrix(categorized_links,link_transitions, categories)
    print("\nMost Probable transitions:")
    print(transition_most)
    
    print("Transition Matrix:")
    print(transition_matrix)


url = "https://en.wikipedia.org/wiki/Markov_chain"
main(url)
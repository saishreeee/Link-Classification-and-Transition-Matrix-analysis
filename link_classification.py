import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse
import numpy as np

# Classify the type of link based on the href attribute
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

# Fetch all the links from a webpage
def get_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link['href'] for link in soup.find_all('a', href=True)]
        return links
    except Exception as e:
        print("Error:", e)
        return []

# Categorize a single link based on keywords
def categorize_link(link):
    categories = {
        'Science': ['science', 'research', 'physics', 'chemistry', 'astronomy', 'beaker', 'biochemistry', 'biology', 'botany', 'bunsen', 'burnerburette'],
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

# Categorize all the links into different categories
def categorize_links(links):
    categorized_links = {}
    for link in links:
        category = categorize_link(link)
        if category in categorized_links:
            categorized_links[category].append(link)
        else:
            categorized_links[category] = [link]
    return categorized_links

# Get the transitions between different categories of links
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

# Create a transition matrix for the categorized links
def transition_matrix(categorized_links, link_transitions, categories):
    n = len(categories)
    matrix = np.zeros((n, n))

    for source_category, target_category in link_transitions.keys():
        source_index = categories.index(source_category)
        target_index = categories.index(target_category)
        matrix[source_index, target_index] = link_transitions[(source_category, target_category)]
        if source_index == target_index:
            matrix[source_index, target_index] = 0

    for i in range(n):
        if sum(matrix[i]) > 0:
            matrix[i] /= sum(matrix[i])
        else:
            matrix[i] = np.ones(n) / n

    return matrix[0], matrix

# Main function to execute the link analysis
def main(url):
    links = get_links(url)
    if not links:
        print("No links found or error fetching the page.")
        return

    link_transitions = get_link_transitions(url)
    
    categorized_links = categorize_links(links)
    print("Categorized Links:")
    other_link_count=0
    for category, links in categorized_links.items():
        if category != "Other":
            print(category, ":", len(links))
        else:
            other_link_count+=len(links)
    print("Other Links:", other_link_count)
    
    max_value = max(len(links) for links in categorized_links.values())
    for key, value in categorized_links.items():
        if len(value) == max_value:
            print(f"Central theme of the website is {key}.")
            break
    
    categories = list(categorized_links.keys())
    transition_most, transition_matrix_result = transition_matrix(categorized_links, link_transitions, categories)
    
    print("\nMost Probable transitions:")
    print(transition_most)
    
    print("Transition Matrix:")
    print(transition_matrix_result)

url = "https://www.geeksforgeeks.org/markov-chain/"
main(url)

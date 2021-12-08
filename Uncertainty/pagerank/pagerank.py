import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])  # crawl takes the HTML code and return a dictionary
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)  # estimate each pageRank by sampling
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)  # iterative version of the algorithm
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    number_of_pages = len(corpus)
    number_of_links = len(corpus[page])
    probability = dict()

    if number_of_links == 0:
        for page1 in corpus:
            probability[page1] = 1 / number_of_pages
        return probability

    for page1 in corpus:  # probability to choose one from everything
        probability[page1] = (1 - damping_factor) / number_of_pages

    for link in corpus[page]:
        probability[link] += damping_factor / number_of_links

    return probability


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    visited_pages = {}
    for page in corpus:
        visited_pages[page] = 0

    page = random.choice(list(corpus.keys()))
    visited_pages[page] += 1

    for i in range(n-1):
        chances = transition_model(corpus, page, damping_factor)
        weights = []
        pages = []
        for p in chances:
            pages.append(p)
            weights.append(chances[p])
        page = random.choices(pages, weights, k=1)
        page = page.pop()
        visited_pages[page] += 1

    importance = {}

    for page in visited_pages:
        importance[page] = visited_pages[page] / n

    return importance


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    importance = {}
    n = len(corpus)  # total number of pages
    for page in corpus:
        importance[page] = 1 / n

    change = 1
    iterations = 1

    corpus_with_fixed_zero_links = corpus.copy()
    for page in corpus_with_fixed_zero_links:
        if len(corpus_with_fixed_zero_links[page]) == 0:
            corpus_with_fixed_zero_links[page] = {link for link in corpus}

    while change >= 0.001:
        previous_values = importance.copy()

        for page in importance:

            parent_links = [x for x in corpus if page in corpus_with_fixed_zero_links[x]]

            first_part = (1 - damping_factor) / n
            second_part = []

            if len(parent_links) != 0:
                for link in parent_links:
                    num_links = len(corpus_with_fixed_zero_links[link])
                    value = previous_values[link] / num_links
                    second_part.append(value)

            second_part = sum(second_part)
            importance[page] = first_part + (damping_factor * second_part)

            change = abs(importance[page] - previous_values[page])
        iterations += 1

    print(f"Iterative algorithm took {iterations} iterations")

    return importance


if __name__ == "__main__":
    main()

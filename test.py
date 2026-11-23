from wikirecommender import WikipediaRecommender

url = "https://en.wikipedia.org/wiki/Python_(programming_language)"

# Instantiate the recommender
recommender = WikipediaRecommender()

# Load 100 articles starting from a specific URL
recommender.load_articles(page_count=100, start_link="https://en.wikipedia.org/wiki/Main_Page")

urls = [
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Artificial_intelligence"
]

# Generate recommendations for multiple pages and include the provided URL
recommendations = recommender.recommend(urls, include_provided_urls=True)

# Display the top 10 recommendations
print(recommendations.head(10))

# Save the current state to a file
recommender.save_to_file("recommender.csv")

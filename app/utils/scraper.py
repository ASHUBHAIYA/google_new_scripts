import requests
from bs4 import BeautifulSoup
import re
from .. import db
import validators
import nltk
from app.models import Article
nltk.download('punkt')
from nltk import sent_tokenize
from app import create_app, db


# Define URLs with hardcoded categories
url_category_mapping = {
    "World": "https://www.thehindu.com/news/international/",
    "Entertainment": "https://www.thehindu.com/entertainment/",
    "Sports": "https://www.thehindu.com/sport/",
    "Bussiness": "https://www.thehindu.com/business/",
    "Technology": "https://www.thehindu.com/sci-tech/technology/"
}


def scrape_hindu(homepage_url, category):
    if not validators.url(homepage_url):
        print(f"Invalid URL for {category}: {homepage_url}")
        return

    try:
        response = requests.get(homepage_url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch URL for {category}: {homepage_url}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []

        # Step 1: Fetch all article links from the homepage
        title_tags = soup.find_all(['h1', 'h2', 'h3'], class_='title') + \
                     soup.find_all(['h1', 'h2', 'h3'], class_='title mb-3')

        # Extract links from title tags
        for item in title_tags:
            link_tag = item.find('a')
            if link_tag:
                article_url = link_tag['href']
                article_title = link_tag.get_text(strip=True)
                articles.append({'url': article_url, 'title': article_title, 'category': category})

        # Step 2: Process each article URL
        all_articles = []  # Store all articles for this category
        for article in articles:
            article_url = article['url']
            try:
                article_response = requests.get(article_url, timeout=10)
                article_soup = BeautifulSoup(article_response.content, 'html.parser')

                # Extracting title
                title = article_soup.find('h1', itemprop='name')
                title = title.get_text(strip=True) if title else 'No Title Available'
                title = title.encode('utf-8').decode('unicode_escape')
                clean_title = title.replace("Premium", "").strip()

                # Extracting sub-title
                sub_title = article_soup.find('h2', class_='sub-title')
                sub_title = sub_title.get_text(strip=True) if sub_title else 'No Sub-Title Available'

                # Extracting content paragraphs
                content_paragraphs = article_soup.find_all('p')

                # Extract and clean content
                full_text = ' '.join([
                    re.sub(r'Photo Credit[:|]\s*\S.*?(?=\.\s|$)', '', p.get_text(strip=True))  # Removes "Photo Credit: ..."
                    for p in content_paragraphs
                    if not any(keyword in p.get_text() for keyword in [
                        'e-Paper', 'Copyright', 'Published-', 'Updated-', 'Premium'
                    ])
                ])

                # Remove "Updated- <date> <time> IST" and "Published- <date> <time> IST"
                full_text = re.sub(r'(Updated-|Published-).*? IST', '', full_text).strip()

                # Remove unwanted text
                full_text = full_text.replace(
                    "The Hindu On BooksBooks of the week, reviews, excerpts, new titles and features. "
                    "Data PointDecoding the headlines with facts, figures, and numbers First Day First ShowNews and reviews from the world of cinema and streaming. "
                    "Health MattersRamya Kannan writes to you on getting to good health, and staying there The View From IndiaLooking at World Affairs from the Indian perspective. "
                    "Science For AllThe weekly newsletter from science writers takes the jargon out of science and puts the fun in! Karnataka TodayYour daily dose of news highlights from Karnataka Today's CacheYour download of the top 5 technology stories of the day.",
                    ""
                ).replace(
                    "BACK TO TOP Terms & conditions|Institutional Subscriber Comments have to be in English, and in full sentences. "
                    "They cannot be abusive or personal. Please abide by ourcommunity guidelinesfor posting your comments. "
                    "We have migrated to a new commenting platform. If you are already a registered user of The Hindu and logged in, "
                    "you may continue to engage with our articles. If you do not have an account please register and login to post comments. "
                    "Users can access their older comments by logging into their accounts on Vuukle.",
                    ""
                ).strip()

                # Remove all "|" symbols and normalize spaces
                full_text = re.sub(r'\s*\|\s*', ' ', full_text)

                # Tokenize the text into sentences
                sentences = sent_tokenize(full_text)

                # Split content into actual news and extracted tags
                if len(sentences) > 5:
                    news_content = ' '.join(sentences[:-5])  # Keep all but last 5 sentences
                    tags = ', '.join(sentences[-5:])  # Store last 5 sentences as tags
                else:
                    news_content = full_text  # If content is too short, keep all
                    tags = ""

                # Save article data
                all_articles.append({
                    'title': clean_title,
                    'sub_title': sub_title,
                    'content': news_content,
                    'category': article['category'],
                    'tags': tags
                })
                db.session.bulk_insert_mappings(Article, all_articles)

            except Exception as e:
                print(f"Error processing article: {article_url} - {e}")
                continue

        # Write articles to file
        with open("D:\\google_news copy\\article.txt", mode="a", encoding="utf-8") as file:
            for article in all_articles:
                file.write(
                    f'\nNew Article:\nTitle: {article["title"]}\nSub-Title: {article["sub_title"]}\n'
                    f'Content: {article["content"]}\nCategory: {article["category"]}\n'
                    f'Tags: {article["tags"]}\n{"-"*40}'
                )
        db.session.commit()
        print(f'Successfully scraped and processed {len(all_articles)} articles from {category}.')

    except Exception as e:
        print(f"Error fetching homepage for {category}: {e}")



app = create_app()
with app.app_context():
    for category, homepage_url in url_category_mapping.items():
        scrape_hindu(homepage_url, category)



# import requests
# from bs4 import BeautifulSoup
# import re
# import validators
# import nltk
# from datetime import datetime, timezone
# from nltk import sent_tokenize
# from app import db
# from app.models import Article
# from app import create_app

# # Create app context


# nltk.download('punkt')

# # Define URLs with hardcoded categories
# url_category_mapping = {
#     "World": "https://www.thehindu.com/news/international/",
#     "Entertainment": "https://www.thehindu.com/entertainment/",
#     "Sports": "https://www.thehindu.com/sport/",
#     "Bussiness": "https://www.thehindu.com/business/",
#     "Technology": "https://www.thehindu.com/sci-tech/technology/"
# }


# def scrape_hindu(homepage_url, category):
#     if not validators.url(homepage_url):
#         print(f"Invalid URL for {category}: {homepage_url}")
#         return

#     try:
#         response = requests.get(homepage_url, timeout=10)
#         if response.status_code != 200:
#             print(f"Failed to fetch URL for {category}: {homepage_url}")
#             return

#         soup = BeautifulSoup(response.content, 'html.parser')

#         articles = []

#         # Step 1: Fetch all article links from the homepage
#         title_tags = soup.find_all(['h1', 'h2', 'h3'], class_='title') + \
#                      soup.find_all(['h1', 'h2', 'h3'], class_='title mb-3')

#         # Extract links from title tags
#         for item in title_tags:
#             link_tag = item.find('a')
#             if link_tag:
#                 article_url = link_tag['href']
#                 article_title = link_tag.get_text(strip=True)
#                 articles.append({'url': article_url, 'title': article_title, 'category': category})

#         # Step 2: Process each article URL
#         all_articles = []  # Store all articles for this category
#         for article in articles:
#             article_url = article['url']
#             try:
#                 article_response = requests.get(article_url, timeout=10)
#                 article_soup = BeautifulSoup(article_response.content, 'html.parser')

#                 # Extracting title
#                 title = article_soup.find('h1', itemprop='name')
#                 title = title.get_text(strip=True) if title else 'No Title Available'
#                 clean_title = title.replace("Premium", "").strip()

#                 # Extracting sub-title
#                 sub_title = article_soup.find('h2', class_='sub-title')
#                 sub_title = sub_title.get_text(strip=True) if sub_title else 'No Sub-Title Available'

#                 # Extracting content paragraphs
#                 content_paragraphs = article_soup.find_all('p')

#                 # Extract and clean content
#                 full_text = ' '.join([
#                     re.sub(r'Photo Credit[:|]\s*\S.*?(?=\.\s|$)', '', p.get_text(strip=True))  # Removes "Photo Credit: ..."
#                     for p in content_paragraphs
#                     if not any(keyword in p.get_text() for keyword in [
#                         'e-Paper', 'Copyright', 'Published-', 'Updated-', 'Premium'
#                     ])
#                 ])

#                 # Remove "Updated- <date> <time> IST" and "Published- <date> <time> IST"
#                 full_text = re.sub(r'(Updated-|Published-).*? IST', '', full_text).strip()

#                 # Remove unwanted text
#                 full_text = full_text.replace(
#                     "The Hindu On BooksBooks of the week, reviews, excerpts, new titles and features. "
#                     "Data PointDecoding the headlines with facts, figures, and numbers First Day First ShowNews and reviews from the world of cinema and streaming. "
#                     "Health MattersRamya Kannan writes to you on getting to good health, and staying there The View From IndiaLooking at World Affairs from the Indian perspective. "
#                     "Science For AllThe weekly newsletter from science writers takes the jargon out of science and puts the fun in! Karnataka TodayYour daily dose of news highlights from Karnataka Today's CacheYour download of the top 5 technology stories of the day.",
#                     ""
#                 ).replace(
#                     "BACK TO TOP Terms & conditions|Institutional Subscriber Comments have to be in English, and in full sentences. "
#                     "They cannot be abusive or personal. Please abide by ourcommunity guidelinesfor posting your comments. "
#                     "We have migrated to a new commenting platform. If you are already a registered user of The Hindu and logged in, "
#                     "you may continue to engage with our articles. If you do not have an account please register and login to post comments. "
#                     "Users can access their older comments by logging into their accounts on Vuukle.",
#                     ""
#                 ).strip()

#                 # Remove all "|" symbols and normalize spaces
#                 full_text = re.sub(r'\s*\|\s*', ' ', full_text)

#                 # Tokenize the text into sentences
#                 sentences = sent_tokenize(full_text)

#                 # Split content into actual news and extracted tags
#                 if len(sentences) > 5:
#                     news_content = ' '.join(sentences[:-5])  # Keep all but last 5 sentences
#                     tags = ', '.join(sentences[-5:])  # Store last 5 sentences as tags
#                 else:
#                     news_content = full_text  # If content is too short, keep all
#                     tags = ""

#                 # Save article data to DB
#                 article_db = Article(
#                     title=clean_title,
#                     sub_title=sub_title,
#                     content=news_content,
#                     category=article['category'],
#                     date=datetime.now(timezone.utc)
#                 )
#                 db.session.add(article_db)

#             except Exception as e:
#                 print(f"Error processing article: {article_url} - {e}")
#                 continue

#         db.session.commit()
#         print(f'Successfully scraped and inserted {len(all_articles)} articles from {category}.')

#     except Exception as e:
#         print(f"Error fetching homepage for {category}: {e}")

# # Process URLs one by one

# app = create_app()
# with app.app_context():
#     # Process URLs one by one
#     for category, homepage_url in url_category_mapping.items():
#         scrape_hindu(homepage_url, category)
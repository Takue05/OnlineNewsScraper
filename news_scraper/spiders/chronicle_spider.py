import scrapy
from datetime import datetime
from news_scraper.items import NewsArticleItem
import re


class ChronicleSpider(scrapy.Spider):
    name = 'chronicle'
    allowed_domains = ['heraldonline.co.zw']

    # Define start URLs for each category
    def start_requests(self):
        categories = {
            'https://www.heraldonline.co.zw/single-category/?tag=business&category=chronicle': 'Business',
            'https://www.heraldonline.co.zw/single-category/?tag=international&category=chronicle': 'Politics',
            'https://www.heraldonline.co.zw/single-category/?tag=entertainment&category=chronicle': 'Arts/Culture/Celebrities',
            'https://www.heraldonline.co.zw/single-category/?tag=sport&category=chronicle': 'Sports'
        }

        for url, category in categories.items():
            yield scrapy.Request(url, callback=self.parse, meta={'category': category})

    def parse(self, response):
        category = response.meta['category']
        self.logger.info(f"Processing category page: {response.url}")

        # Target h6 elements that contain links
        h6_elements = response.css('h6')
        self.logger.info(f"Found {len(h6_elements)} h6 elements")

        # Find article links and their dates
        for h6 in h6_elements:
            # Extract link from h6
            link = h6.css('a::attr(href)').get()
            if not link:
                continue

            # Look for date in paragraph immediately following the h6 element
            date_text = None
            next_p = h6.xpath('./following-sibling::p[1]')

            if next_p:
                date_text = next_p.get()
                self.logger.info(f"Found paragraph after link: {date_text}")

                # Extract the date text from the paragraph
                if date_text:
                    # Extract date from <p style="color:black">May 10, 2025</p> format
                    date_match = re.search(r'>([A-Za-z]+ \d{1,2}, \d{4})<', date_text)
                    if not date_match:
                        # Try alternative format Month Day, Year
                        date_match = re.search(
                            r'>((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})<',
                            date_text)

                    if date_match:
                        date_text = date_match.group(1)
                    else:
                        # Try another pattern for just extracting text between tags
                        clean_text = re.sub(r'<.*?>', '', date_text).strip()
                        if re.search(
                                r'(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}',
                                clean_text):
                            date_text = clean_text

            # Process the article link
            if link and not link.startswith(('http://', 'https://')):
                link = response.urljoin(link)

            self.logger.info(f"Following link: {link}, with date: {date_text}")

            # Pass the extracted date to the parse_article method
            yield response.follow(link, self.parse_article, meta={
                'category': category,
                'date_text': date_text
            })

        # Check if there's a "next page" link
        next_page = response.css('.pagination a.next::attr(href), .nav-links a.next::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse, meta={'category': category})

    def parse_article(self, response):
        self.logger.info(f"Parsing article: {response.url}")

        item = NewsArticleItem()

        # Try multiple selectors for title with more variations
        selectors = [
            'h1::text',
            'h1.article-title::text',
            'h1.entry-title::text',
            '.headline h1::text',
            '.article-header h1::text',
            '.post-title::text',
            'header h1::text'
        ]

        for selector in selectors:
            title = response.css(selector).get()
            if title and title.strip():
                item['title'] = title.strip()
                self.logger.info(f"Found title with selector {selector}: {item['title']}")
                break

        item['url'] = response.url
        item['newspaper'] = 'The Chronicle'
        item['category'] = response.meta['category']

        # IMPORTANT: Use the date passed from the category page first
        if 'date_text' in response.meta and response.meta['date_text']:
            # Clean up the date text if needed
            date_text = response.meta['date_text']

            # If it's HTML, extract just the text content
            if '<' in date_text and '>' in date_text:
                # Extract text between tags like <p style="color:black">May 10, 2025</p>
                date_match = re.search(r'>([A-Za-z]+ \d{1,2}, \d{4})<', date_text)
                if date_match:
                    item['date'] = date_match.group(1)
                else:
                    # Try another pattern
                    clean_text = re.sub(r'<.*?>', '', date_text).strip()
                    month_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}'
                    match = re.search(month_pattern, clean_text)
                    if match:
                        item['date'] = match.group(0)
            else:
                # It's already clean text
                month_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}'
                match = re.search(month_pattern, date_text)
                if match:
                    item['date'] = match.group(0)

            self.logger.info(f"Using date from category page: {item.get('date')}")

        # If we couldn't extract the date from meta, try to find it in the article
        if 'date' not in item or not item['date']:
            # Define common month pattern
            month_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}'

            # Look for dates in paragraphs
            for p_element in response.css('p'):
                text = p_element.get()
                if text:
                    # Check for dates in paragraph
                    match = re.search(month_pattern, text)
                    if match:
                        item['date'] = match.group(0)
                        self.logger.info(f"Found date in paragraph: {item['date']}")
                        break

            # If still no date, try CSS selectors
            if 'date' not in item or not item['date']:
                date_selectors = [
                    '.post-date::text',
                    '.entry-date::text',
                    '.date::text',
                    '.meta-date::text',
                    '.article-date::text',
                    '.post-meta::text',
                ]

                for selector in date_selectors:
                    date_text = response.css(selector).get()
                    if date_text and date_text.strip():
                        match = re.search(month_pattern, date_text)
                        if match:
                            item['date'] = match.group(0)
                            self.logger.info(f"Found date with selector {selector}: {item['date']}")
                            break

        # Fallback if no date found
        if 'date' not in item or not item['date']:
            item['date'] = datetime.now().strftime('%B %d, %Y')
            self.logger.info("No date found, using current date as fallback")

        item['timestamp'] = datetime.now().isoformat()

        yield item
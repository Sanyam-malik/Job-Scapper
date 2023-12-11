import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

websites = [
    {
        "name": "TechCompreviews",
        "url": "https://techcompreviews.in/category/jobs-update",
        "main-class": "site-main",
        "title-class": "entry-title",
        "summary-class": "entry-summary",
        "img-class": "post-image",
        "url-class": "entry-title",
        "date-class": "entry-date",
        "date-format": "%d %B %Y",
        "page-length": "10"
    },
    {
        "name": "FrontLinesMedia",
        "url": "https://frontlinesmedia.in/category/job-notifications",
        "main-class": "td-ss-main-content",
        "title-class": "td-module-title",
        "summary-class": "td-excerpt",
        "img-class": "td-module-thumb",
        "url-class": "td-module-title",
        "date-class": "td-module-date",
        "date-format": "%B %d, %Y",
        "page-length": "10"
    },
    {
        "name": "SightsInPlus",
        "url": "https://sightsinplus.com/category/news/hiring",
        "main-class": "td-main-content",
        "title-class": "td-module-title",
        "summary-class": "entry-summary",
        "img-class": "td-module-thumb",
        "url-class": "td-module-title",
        "date-class": "td-post-date",
        "date-format": "%B %d, %Y",
        "page-length": "10"
    }
]


def get_pages(website):
    url = website['url']
    headers = {
        "User-Agent": "Site24x7",
        "Cache-Control": "no-cache",
        "Accept": "*/*",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        if website['name'] == "TechCompreviews":
            next_btn = soup.find_all(class_="page-numbers")
            return next_btn[len(next_btn) - 2].text.strip().lower().replace("page", "")
        elif website['name'] == "FrontLinesMedia":
            next_btn = soup.find_all(class_="last")
            return next_btn[len(next_btn) - 2].text.strip().lower().replace("page", "")
        elif website['name'] == "SightsInPlus":
            next_btn = soup.find_all(class_="last")
            return next_btn[len(next_btn) - 2].text.strip().lower().replace("page", "")
    else:
        return "1"


def scrape_website(website, page=1):
    url = website['url']
    if page != 1:
        url = url + "/page/" + str(page)

    print("Processing URL: ", url)

    json_response_list = []
    # Send an HTTP request to the website
    headers = {
        "User-Agent": "Site24x7",
        "Cache-Control": "no-cache",
        "Accept": "*/*",
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        soup = soup.find(class_=website['main-class'])
        paragraphs = [paragraph.get_text().strip() for paragraph in soup.find_all(class_=website['title-class'])]
        summaries = [summary.get_text().strip() for summary in soup.find_all(class_=website['summary-class'])]
        links = [url.find('a')['href'] for url in soup.find_all(class_=website['url-class']) if url.find('a')]
        images = [url.find('img')['src'] for url in soup.find_all(class_=website['img-class']) if url.find('img')]
        dates = [date.get_text() for date in soup.find_all(class_=website['date-class'])]

        for index in range(0, len(paragraphs)):
            publish_date = datetime.strptime(dates[index], website['date-format'])
            last_date = datetime.now() - timedelta(days=29)

            if publish_date > last_date:
                # Check if any of the values are None
                title = paragraphs[index].strip() if paragraphs[index] is not None else ""
                image = str(images[index]).strip() if images[index] is not None else ""
                summary = summaries[index].strip() if (len(summaries) > 0 and summaries[index] is not None) else ""

                # Assuming publish_date and links are not None, as you are using them directly without checking
                date = str(publish_date.date())
                url = str(links[index]).strip() if links[index] is not None else ""

                # Append the values to the json_response_list
                json_response_list.append({
                    "title": title,
                    "image": image,
                    "summary": summary,
                    "date": date,
                    "url": url
                })

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
    return json_response_list


if __name__ == "__main__":
    current_page = 1
    last_page = int(get_pages(websites[2]))
    list = []
    while current_page <= last_page:
        new_list = scrape_website(websites[2], current_page)
        for item in new_list:
            list.append(item)
        if len(new_list) < int(websites[2]['page-length']):
            break
        else:
            current_page = current_page + 1
    with open(f"{websites[2]['name'].lower()}.json", 'w') as file:
        json.dump(list, file, indent=2)

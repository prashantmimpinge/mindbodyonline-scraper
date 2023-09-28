"""
Script to retrieve the data from mindbodyonline
"""
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time, csv
import argparse

class Scapper:
    """
    This class deals with mindbodyonline scrapper
    """

    def __init__(self,url,*args, **kwargs):
        self.url = url
        self.homeurl = "https://www.mindbodyonline.com/explore/"
        self.BaseURL = "https://www.mindbodyonline.com"
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("window-size=1420,1080")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--enable-javascript")
        self.driver = webdriver.Chrome(options=self.options)
        self.columns = [
            "url",
            "name of studio",
            "activities",
            "address",
            "phone number",
        ]
        self.data = []
    
    def get_urls(self, url):
        urls_list = []
        try:
            self.driver.get(url)
            time.sleep(10)
        except Exception as e:
            print("get_urls>>>>>>", e)

        soup = BeautifulSoup(self.driver.page_source, "html5lib")
        urls = soup.findAll("div", attrs={"class": "ResultsPage_card__huif9"})
        if len(urls) > 0:
            pass
        else:
            urls = soup.findAll("div", attrs={"class": "ResultsPage_listItem__jJT5O"})
        for i in urls:
            urls_list.append(self.BaseURL + i.a["href"])
        return urls_list
    
    def get_page_numbers(self, url):
        try:
            self.driver.get(url)
            time.sleep(10)
        except Exception as e:
            print("get_page_numbers>>>>>>", e)

        soup = BeautifulSoup(self.driver.page_source, "html5lib")

        pages_list = soup.find("ul", attrs={"class": "Pagination_list__3oaAo"})
        try:
            last_page = pages_list.findAll(
                "li", attrs={"class": "Pagination_number__TLPw1"}
            )[-1]
        except AttributeError as e:
            return 1
        return last_page.get_text()

    def output_urls_data(self, url):
        no_of_pages = self.get_page_numbers(url)
        print(no_of_pages, "no_of_pages")

        for i in range(1, int(no_of_pages) + 1):
            if i == 1:
                url = self.url
            else:
                url = self.url + "?page={}".format(i)
            studio_urls = self.get_urls(url)
            for j in studio_urls:
                self.output_data(j)

    def output_data(self, url):
        try:
            self.driver.get(url)
            time.sleep(10)
        except Exception as e:
            print(e)
            return False

        soup = BeautifulSoup(self.driver.page_source, "html5lib")

        section = soup.find(
            "div", attrs={"class": "column is-5-desktop DetailHeader_content__2TwFs"}
        )
        address = ""
        try:
            studio_name = section.find(
                "h2", attrs={"class": "is-marginless"}
            ).get_text()
        except AttributeError as e:
            studio_name = ""
        address_obj = section.find(
            "div", attrs={"class": "DetailHeader_address__3jDc1"}
        )
        address_obj_p = address_obj.findAll("p", attrs={"class": "is-marginless"})
        for address_data in address_obj_p:
            address = address + address_data.get_text()
        phone_number = section.find(
            "span", attrs={"class": "PhoneNumber_tel__2X0do"}
        ).get_text()
        activities_data = section.find(
            "h6", attrs={"class": "DetailHeader_category__1NCIZ"}
        )

        activities = activities_data.p.get_text().split("|")
        activity_list = []
        for activity in activities:
            act_value = activity.replace("…", "")
            activity_list.append(act_value.strip())
        dataList = [url, studio_name, activity_list, address, phone_number]
        self.data.append(dataList)
        print(dataList)
        """
        Return required Response
        """
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="City URL",type=str)
    
    args = parser.parse_args()
    print(args.url)
    obj = Scapper(args.url)
    obj.output_urls_data(obj.url)
    filename = "{}.csv".format(args.url.split('/')[-1])

    # writing to csv file
    with open(filename, "w") as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields
        csvwriter.writerow(obj.columns)

        # writing the data rows
        csvwriter.writerows(obj.data)

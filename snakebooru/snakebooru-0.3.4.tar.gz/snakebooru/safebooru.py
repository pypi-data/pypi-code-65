import asyncio
import aiohttp
import urllib.request as urlreq
import xml.etree.ElementTree as ET
from random import randint
from typing import *
from furl import furl

class DataContainer:
    pass

class Safebooru:

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):

        self.booru_url  = "https://safebooru.org/index.php?"
        self.loop       = loop

    def __endpoint(self, s) -> furl:

        endpoint = furl(self.booru_url)
        endpoint.args["page"] = "dapi"
        endpoint.args["s"] = s
        endpoint.args["q"] = "index"

        return endpoint

    async def __fetch(self, session, url):
        async with session.get(url) as response:
            return response.status, await response.read()

    async def __request(self, url):
        async with aiohttp.ClientSession(loop=self.loop) as session:
            code, response = await self.__fetch(session, url)

        if code not in [200, 201]:
            raise Exception(f"""Site returned a non-200 status code: {response}""")

        return response

    # Private function to link images from the various functions above.
    def __link_images(self, response) -> list:

        image_list = []
        temp_dict = dict()
        post_url = "https://safebooru.org/index.php?page=post&s=view&id="
        for i in response:
            post_id = i["id"]
            image_url = i["file_url"]
            temp_dict["post_url"] = post_url + f"{post_id}"
            temp_dict["image_url"] = image_url
            temp_dict["id"] = post_id
            image_list.append(temp_dict)
            temp_dict = dict()

        return image_list

    # hungry
    def __tagifier(self, tags) -> list:

        tags = [tag.strip().lower().replace(" ", "_") for tag in tags.split(", ")] if tags else []
        return tags

    # Returns up too 100 posts and images based on tags the user inputs
    async def get_posts(self, tags="", limit=100, offset=0):
        """User can pass in tags separated by a comma
        Using a dash before a tag will exclude it
        e.g. (cat ears, -blue eyes)
        The limit parameter has a default value of 100
        Safebooru max limit is 100
        Regardless of limit, this should return a list"""

        posts = []
        if limit > 100:
            raise Exception("Limit parameter cannot be greater than 100")
        tags = self.__tagifier(tags)
        endpoint = self.__endpoint("post")
        endpoint.args["limit"] = limit
        endpoint.args["tags"] = " ".join(tags)
        endpoint.args["pid"] = offset

        results = await self.__request(str(endpoint))
        try:
            results = ET.fromstring(results)
        except ET.ParseError:
            raise Exception("Parsing error. Endpoint may be inappropriate.")

        temp = 4
        attempts = 5

        # Offset is randomly set between 0 and 4 until results are found
        # If no results found at offset = 0: returns none
        # This is so no results are missed if obscure tags are passed
        while not results:
            if attempts == 0:
                return None

            endpoint.args["pid"] = randint(0, temp)
            results = await self.__request(str(endpoint))
            try:
                results = ET.fromstring(results)
            except ET.ParseError:
                raise Exception("Parsing error. Endpoint may be inappropriate.")

            temp += -1
            attempts += -1

        for post in results:
            posts.append(post.attrib)

        images = self.__link_images(posts)
        return images

    async def get_single_post(self, tags="", offset=0) -> dict or str:
        """User can pass in tags separated by a comma
        Using a dash before a tag will exclude it
        e.g. (cat ears, -blue eyes)
        Has a hard limit of 1"""

        tags = self.__tagifier(tags)
        posts = []
        endpoint = self.__endpoint("post")
        endpoint.args["limit"] = 100
        endpoint.args["tags"] = tags
        endpoint.args["pid"] = offset

        results = await self.__request(str(endpoint))

        try:
            results = ET.fromstring(results)
        except ET.ParseError:
            raise Exception("Parsing error. Endpoint may be inappropriate.")

        temp = 3
        attempts = 4
        while not results:
            if attempts == 0:
                return "No results after 5 attempts."

            endpoint.args["pid"] = randint(0, temp)
            results = await self.__request(str(endpoint))

        posts.append(results[randint(0, len(results)-1)].attrib)
        image = self.__link_images(posts)
        return image

    # TODO: replace urllib with aiohttp
    async def get_random_post(self):
        """Returns random post
        """

        posts = []
        try:
            urlobj = urlreq.urlopen(self.booru_url)
            data = ET.parse(urlobj)
            urlobj.close()
            root_temp = data.getroot()
        except ET.ParseError:
            return None

        post_id = randint(1, int(root_temp.attrib["count"]))
        final_url = self.booru_url + f"""&id={post_id}"""
        try:
            urlobj = urlreq.urlopen(self.booru_url)
            data = ET.parse(urlobj)
            urlobj.close()
            root = data.getroot()
        except ET.ParseError:
            return None

        posts.append(root[0].attrib)
        image = self.__link_images(posts)
        return image[0]

    # Get data from a post
    # TODO: replace urllib with aiohttp
    # TODO: create post container/class for this
    async def get_post_data(self, post_id):
        "User can pass in a post ID to get all of its data"

        data_url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&id={post_id}"

        urlobj = urlreq.urlopen(data_url)
        data = ET.parse(urlobj)
        urlobj.close()
        root = data.getroot()

        return root[0].attrib # Returns a dictionary

# ! testing method, ignore.
async def __test():
    safebooru = Safebooru()

    post = await safebooru.get_single_post(tags="cat ears, blue eyes")
    print(post)

if __name__ == "__main__":
    asyncio.run(__test())
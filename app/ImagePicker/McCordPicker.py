import re
import random
from requests_html import HTMLSession

from app.Base import Base


class McCordPicker(Base):
    def __init__(self):
        super(McCordPicker, self).__init__()
        self.baseUrl = "https://collections.musee-mccord-stewart.ca"
        self.searchUrl = "https://collections.musee-mccord-stewart.ca/fr/collections/155926/photographie/objects/images?filter=date%3A1800%2C1940%3BmediaExistence%3Atrue%3Bdepartment%3APhotographie%20-%20Collection%20documentaire"
        self.paginationParam = "page"
        self.imageViewUrl = "https://collections.musee-mccord-stewart.ca/internal/media/dispatcher/:id/preview"
        self.imageDescription = "Oeuvre du bot Pröspect pour le gisement des archives du Musée McCord, Canada"
        self.twitterText = "#MuséeMcCord"
        self.log("\n* McCordPicker initialized")

    def pickImage(self):
        session = HTMLSession()
        r = session.get(self.searchUrl)
        elMaxPage = r.html.find(".max-pages", first=True)
        maxPageMatch = re.sub(r'[^0-9]', '', elMaxPage.text)
        maxPage = int(maxPageMatch)
        randomPage = random.randint(1, maxPage)
        payload = {self.paginationParam: randomPage}
        r = session.get(self.searchUrl, params=payload)
        elsImages = r.html.find("#timagesview div.img-wrap > a")
        links = []
        for elImage in elsImages:
            absoluteLinks = elImage.absolute_links
            absoluteLink = next(iter(absoluteLinks))
            links.append(absoluteLink)
        randomIndex = random.randint(0, len(links) - 1)
        pickedLink = links[randomIndex]
        imageId = re.search("objects/([0-9]+)", pickedLink).group(1)
        imageUrl = re.sub(":id", imageId, self.imageViewUrl)
        return {
            "url": imageUrl,
            "sourceId": "mccord",
            "source": "McCord",
            "description": self.imageDescription,
            "twitterText": self.twitterText,
        }


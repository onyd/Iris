import urllib.request as urlreq
from bs4 import BeautifulSoup
from bs4.element import Comment
import re


class WebUtils:

    @staticmethod
    def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    @staticmethod
    def text_from_html(body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(WebUtils.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    @staticmethod
    def url_to_text(url):
        """Load text from website (wikipedia ...) to train embedding"""
        html = urlreq.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        raw = ""
        for p in soup.findAll('p'):
            raw += WebUtils.text_from_html(str(p))

        return raw.lower()

    @staticmethod
    def text_to_sentences(text):
        """Slice and remove general unwanted chars in text into sentences
        """
        # Apply some regex cleaning
        text = re.sub(r"\/.?\/", "", text)
        text = re.sub(r"\/.?", "", text)
        text = re.sub(r".?\/", "", text)
        text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"\[.*?\]", "", text)

        text = re.sub(r"[^A-Za-z0-9^.'éèàêùâÂûç]", " ", text)
        text = re.sub(" [A-Za-z] ", " ", text)
        text = re.sub(r" +", " ", text)

        # Slice by sentences
        sentences = re.split("\.+", text)
        return sentences[:-1]

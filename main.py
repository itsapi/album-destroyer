import urllib.request
from PIL import Image
from io import BytesIO
from convert_image import convert_image


def get_image_from_url(url):
    return Image.open(BytesIO(urllib.request.urlopen(url).read()))

def main():
    pass

if __name__ == '__main__':
    main()

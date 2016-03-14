# Get size of image
def get_image_size(source):
    from PIL import Image
    return Image.open(source).size

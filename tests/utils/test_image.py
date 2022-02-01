from pytest import main
from PIL import Image
from ocrd_utils.image import rotate_image

def test_32bit_fill():
    img = Image.new('F', (200, 100), 1)
    rotate_image(img, 0.1, fill='background', transparency=False)

def test_max_image_pixels():
    assert Image.MAX_IMAGE_PIXELS == 40_000 ** 2

if __name__ == '__main__':
    main([__file__])

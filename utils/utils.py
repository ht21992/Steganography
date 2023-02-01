from PIL import Image
from io import BytesIO
import numpy as np


def generateDownloadableImage(img):
    img = Image.fromarray(img)
    buf = BytesIO()
    img.save(buf, format="png")
    byte_im = buf.getvalue()
    return byte_im


def to_bin(data):
    """
    Convert `data` to binary format as string

    Args:
        data (str, bytes, np array, int or uint8): it refers to the data that its format is needed to be changed

    """
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes):
        return ''.join([format(i, "08b") for i in data])
    elif isinstance(data, np.ndarray):
        return [format(i, '08b') for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported")


def calculate_image_max_bytes(img):
    """ max_bytes calculation: 
        each pixel on a photo holds a byte for each of the 3 makeup colors namely; red, green, blue.
        each pixel equals to 3 bytes, with each color equaling to 1byte, where 1 byte == 8bits
        if we imagine an image with size of 720*480 then we have 720 x 480 = 345,600 pixels
        since each pixel holds three bytes(for the assumed 24 Bit Depth size) 
        so we can calculate total bytes 345600 x 3 =  1, 036, 800 bytes
        and since 1byte = 8bit so we need to divide it by 8 and get the division floor

    Args:
        img (PIL Image Object): The Image

    Returns:
        int: return max_bytes as Integer
    """
    img = Image.open(img)
    img_numpy = np.array(img.convert('RGB'))
    max_bytes = img_numpy.shape[0] * img_numpy.shape[1] * 3 // 8
    return max_bytes


def encode(uploaded: object, secret_data: str, key: str):
    """
    Args:
        image (PIL Image): it refers to the uploaded image
        secret_data (str): refers to your secret message
        key (str): refers to the key that you as sender and the person who is going to receive the message must have
        max_bytes (int):

    Raises:
        ValueError: if there is Insufficient

    Returns:
        img: returns a numpy ndarray
    """
    # read the uploaded image
    img = Image.open(uploaded)
    img = np.array(img.convert('RGB'))
    # add stopping criteria using the defined key
    secret_data += key
    data_index = 0
    # convert data to binary
    binary_secret_data = to_bin(secret_data)
    # size of data to hide
    data_len = len(binary_secret_data)

    for row in img:
        for pixel in row:
            # convert RGB values to binary format
            r, g, b = to_bin(pixel)
            # modify the LSB(least significant bit) only if there is still data to store
            if data_index < data_len:
                # least significant red pixel bit
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            if data_index < data_len:
                # least significant green pixel bit
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            if data_index < data_len:
                # least significant blue pixel bit
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            # if data is encoded, just break out of the loop
            if data_index >= data_len:
                break
    flag = 'Encode-Done'
    return flag, img


def decode(encoded_img, key):
    binary_data = ""
    for row in encoded_img:
        for pixel in row:
            r, g, b = pixel
            r, g, b = to_bin(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    # split by 8-bits
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-len(key):] == key:
            break
    flag = 'Decode-Done'
    return flag, decoded_data[:-len(key)]

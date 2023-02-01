import streamlit as st
import numpy as np
from PIL import Image
from io import BytesIO
from utils.styles import styles
from utils.utils import generateDownloadableImage, calculate_image_max_bytes, encode, decode
# Change page names on Side bar
st.set_page_config(
    page_title="Steganography",

)

#  css part
st.write(styles, unsafe_allow_html=True)

with st.expander("About Steganography"):
    st.write("""
        Hide your secret message within an image.\n\n Hope you enjoy!
     """)

    st.markdown("""
        <h3>What is Steganography?<h3>
     """, unsafe_allow_html=True)
    st.markdown("""<p>Steganography is the practice of hiding a file, message, image, or video within another file, message, image, or video. The word Steganography is derived from the Greek words "steganos" (meaning hidden or covered) and "graphe" (meaning writing).
           Hackers often use it to hide secret messages or data within media files such as images, videos, or audio files. Even though there are many legitimate uses for Steganography, such as watermarking, malware programmers have also been found to use it to obscure the transmission of malicious code.<p>
     """, unsafe_allow_html=True)
    st.markdown('<a href="https://www.buymeacoffee.com/hosseintaj">Buy Me A Coffee</a>',
                unsafe_allow_html=True)
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'encode'
if 'stage' not in st.session_state:
    st.session_state['stage'] = 'waiting'

col1, col2 = st.columns([0.3, 1.3])
with col1:
    en_btn = st.button('Encode')
with col2:
    dec_btn = st.button('Decode')

if en_btn:
    st.session_state['mode'] = 'encode'
if dec_btn:
    st.session_state['mode'] = 'decode'


with col1:
    key = st.text_input('Your Key', 'cigar')
if st.session_state['mode'] == 'encode':
    with col2:
        secret_msg = st.text_input('Your Secret Message', 'my text')
        st.markdown(
            '<small>*The receiver must use the same key</small>', unsafe_allow_html=True)


# Add file uploader to allow users to upload photos
uploaded_image = st.file_uploader(
    "Upload Your Image", type=['png'])


if uploaded_image is not None:
    st.session_state['stage'] = 'waiting'
    if st.session_state['mode'] == 'encode':
        max_bytes = calculate_image_max_bytes(uploaded_image)
        st.markdown(
            f"<p class='info-text'>Max bytes to encode: {max_bytes}</p>", unsafe_allow_html=True)

        if len(secret_msg) > max_bytes:
            st.session_state['stage'] = 'Error'
            st.markdown(
                '<p class="info-text">Insufficient bytes, need bigger image or less data</p>', unsafe_allow_html=True)

    start = st.button(
        f"Start {st.session_state['mode'].title()}ing", disabled=st.session_state['stage'] == 'Error')
    process_logger = st.empty()
    if start:
        # Encode Mode

        if st.session_state['mode'] == 'encode':
            if len(key) > 0 and len(secret_msg) > 0:
                process_logger.markdown(
                    "<p class='info-text'>Encoding...</p>", unsafe_allow_html=True)
                flag, encoded_image = encode(
                    uploaded_image, secret_data=secret_msg, key=key)
                st.session_state['stage'] = flag
                if st.session_state['stage'] == 'Encode-Done':
                    process_logger.write('')
                    byte_im = generateDownloadableImage(encoded_image)
                    st.markdown(
                        "<p class='info-text'>&#9989;Your message has been successfully concealed within the image</p>", unsafe_allow_html=True)
                    st.download_button(
                        label=f"Download Encrypted Image",
                        data=byte_im,
                        file_name=f"image.png",
                        mime=f"image/png"
                    )
        # Decode Mode
        if st.session_state['mode'] == 'decode':
            img = Image.open(uploaded_image)
            img_numpy = np.array(img.convert('RGB'))
            process_logger.markdown(
                "<p class='info-text'>Decoding...</p>", unsafe_allow_html=True)
            flag, decoded_data = decode(img_numpy, key)
            st.session_state['stage'] = flag
            if st.session_state['stage'] == 'Decode-Done':
                process_logger.write('')
                st.markdown(
                    f'<p class="info-text">Extracted Message: <b>{decoded_data}</b></p>', unsafe_allow_html=True)

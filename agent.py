from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.subheader("🎨 AI Image Generator")

prompt = st.text_area(
    "Describe the image you want to generate",
    placeholder="A futuristic city at sunset, cinematic lighting..."
)

if st.button("Generate Image"):
    if prompt:
        with st.spinner("Generating image..."):
            try:
                result = client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size="1024x1024"
                )

                image_b64 = result.data[0].b64_json

                import base64
                image_bytes = base64.b64decode(image_b64)

                st.image(image_bytes, caption="Generated Image")

                st.download_button(
                    "Download Image",
                    data=image_bytes,
                    file_name="generated_image.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Error: {e}")
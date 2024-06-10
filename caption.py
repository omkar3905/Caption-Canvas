from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer
import torch
from PIL import Image
import requests
from io import BytesIO

# Load pretrained model and tokenizer
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Initialize ViT feature extractor
feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Define max_length, num_beams, and gen_kwargs
max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

def predict_step_from_urls(image_urls):
    images = []
    for image_url in image_urls:
        response = requests.get(image_url)
        if response.status_code == 200:
            i_image = Image.open(BytesIO(response.content))
            if i_image.mode != "RGB":
                i_image = i_image.convert(mode="RGB")
            images.append(i_image)
        else:
            print(f"Failed to download image from URL: {image_url}")

    if images:
        pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        output_ids = model.generate(pixel_values, **gen_kwargs)

        preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        preds = [pred.strip() for pred in preds]
        return preds
    else:
        return []

# Example usage:
image_urls = ['https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfOzu8fxNP8N2pKNE4McERTTngj9sC7miJirdc2AhFow&s']
predictions = predict_step_from_urls(image_urls)
print(predictions)

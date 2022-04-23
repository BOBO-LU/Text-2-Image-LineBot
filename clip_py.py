
import torch

import clip
import numpy as np
import pandas as pd

class clip_class():
    def __init__(self) -> None:

        # Load the open CLIP model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)


        # Load the photo IDs
        photo_ids = pd.read_csv("unsplash-dataset/photo_ids.csv")
        photo_ids = list(photo_ids['photo_id'])

        self.photo_ids = photo_ids
        
        # Load the features vectors
        photo_features = np.load("unsplash-dataset/features.npy")

        # Convert features to Tensors: Float32 on CPU and Float16 on GPU
        if self.device == "cpu":
            photo_features = torch.from_numpy(photo_features).float().to(self.device)
        else:
            photo_features = torch.from_numpy(photo_features).to(self.device)

        self.photo_features = photo_features

        # Print some statistics
        print(f"Photos loaded: {len(photo_ids)}")


    def encode_search_query(self, search_query):
        with torch.no_grad():
            # Encode and normalize the search query using CLIP
            text_encoded = self.model.encode_text(clip.tokenize(search_query).to(self.device))
            text_encoded /= text_encoded.norm(dim=-1, keepdim=True)

        # Retrieve the feature vector
        return text_encoded


    def find_best_matches(self, text_features, results_count=3):
        # Compute the similarity between the search query and each photo using the Cosine similarity
        similarities = (self.photo_features @ text_features.T).squeeze(1)

        # Sort the photos by their similarity score
        best_photo_idx = (-similarities).argsort()

        # Return the photo IDs of the best matches
        return [self.photo_ids[i] for i in best_photo_idx[:results_count]]


    def id_to_url(self, photo_id):
        # Get the URL of the photo resized to have a width of 320px
        # photo_image_url = f"https://unsplash.com/photos/{photo_id}/download?w=320"
        photo_image_url = f"https://source.unsplash.com/{photo_id}"
        return photo_image_url

    def search_unslash(self, search_query, results_count=3):
        # Encode the search query
        text_features = self.encode_search_query(search_query)

        # Find the best matches
        best_photo_ids = self.find_best_matches(text_features, results_count)

        url_results = []
        # Display the best photos
        for photo_id in best_photo_ids:
            url_results.append(self.id_to_url(photo_id))

        return url_results


import torch
import clip
import numpy as np
import pandas as pd
import requests

class clip_class():
    def __init__(self) -> None:

        # 載入模型
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

        # 讀取照片id
        photo_ids = pd.read_csv("unsplash-dataset/photo_ids.csv")
        photo_ids = list(photo_ids['photo_id'])

        self.photo_ids = photo_ids
        
        # 讀取特徵
        photo_features = np.load("unsplash-dataset/features.npy")

        # 將numpy特徵轉tensor
        if self.device == "cpu":
            photo_features = torch.from_numpy(photo_features).float().to(self.device)
        else:
            photo_features = torch.from_numpy(photo_features).to(self.device)

        self.photo_features = photo_features

    
    def encode_search_query(self, search_query):
        # 使用CLIP將照片編碼
        with torch.no_grad():
            text_encoded = self.model.encode_text(clip.tokenize(search_query).to(self.device))
            text_encoded /= text_encoded.norm(dim=-1, keepdim=True)

        return text_encoded


    def find_best_matches(self, text_features, results_count=3):
        # 計算照片相似度
        similarities = (self.photo_features @ text_features.T).squeeze(1)

        # 排序相似度
        best_photo_idx = (-similarities).argsort()

        # 回傳最像的前幾張照片
        return [self.photo_ids[i] for i in best_photo_idx[:results_count]]


    def id_to_url(self, photo_id):
        # 將id轉網址
        photo_image_url = f"https://source.unsplash.com/{photo_id}"
        return photo_image_url

    def get_unsplash_redirect(self, url):
        # 訪問一次，取得重新導向的網址
        r = requests.get(url)
        return r.url

    def search_unslash(self, search_query, results_count=3):
        # 將照片編碼
        text_features = self.encode_search_query(search_query)

        # 找到最像的照片
        best_photo_ids = self.find_best_matches(text_features, results_count)

        # 後處理
        url_results = []
        for photo_id in best_photo_ids:
            url = self.id_to_url(photo_id)
            file_url = self.get_unsplash_redirect(url)
            url_results.append(file_url)

        return url_results

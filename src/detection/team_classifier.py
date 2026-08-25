"""
Team Classification using K-Means Clustering on Jersey Colors.
"""

import cv2
import numpy as np
from src.core.protocols import Trackable

class KMeansTeamClassifier:
    """Classifies player team based on dominant jersey color."""
    
    def __init__(self, num_teams: int = 3):
        self.num_teams = num_teams
        self.kmeans = None
        self.is_fitted = False
        self.color_memory = []
        
        try:
            from sklearn.cluster import KMeans
            self.model_class = KMeans
        except ImportError:
            print("scikit-learn not installed.")
            self.model_class = None

    def _extract_torso_color(self, crop: np.ndarray) -> np.ndarray:
        """Extract dominant color from the upper half of the player bounding box, avoiding green (pitch)."""
        h, w = crop.shape[:2]
        if h == 0 or w == 0:
            return np.zeros(3)
            
        # Take upper 40% (torso + shoulders)
        torso = crop[int(h*0.1):int(h*0.5), int(w*0.2):int(w*0.8)]
        
        if torso.size == 0:
            return np.zeros(3)
            
        # Convert to HSV and mask out green (pitch/court)
        hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
        
        # Green mask (roughly 35-85 in OpenCV HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        mask_inv = cv2.bitwise_not(mask)
        
        pixels = torso[mask_inv > 0]
        if len(pixels) == 0:
             # Fallback if entirely masked
             pixels = torso.reshape(-1, 3)
             
        return np.mean(pixels, axis=0) # Return BGR mean
        
    def fit(self, features: np.ndarray) -> None:
        """Fit the KMeans model."""
        if self.model_class is None:
            return
            
        self.kmeans = self.model_class(n_clusters=self.num_teams, n_init=10, random_state=42)
        self.kmeans.fit(features)
        self.is_fitted = True

    def classify(self, player: Trackable, image: np.ndarray) -> int:
        """Return team ID (0, 1, or 2 for referee/goalkeeper)."""
        if player.class_id != 0: # Only classify people
            return -1
            
        x1, y1, x2, y2 = map(int, player.bbox)
        # Ensure bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
        
        crop = image[y1:y2, x1:x2]
        dominant_bgr = self._extract_torso_color(crop)
        
        self.color_memory.append(dominant_bgr)
        
        # Re-fit k-means dynamically for first N players to find the team centroids
        if len(self.color_memory) == 50 and not self.is_fitted:
            self.fit(np.array(self.color_memory))
            
        if self.is_fitted and self.kmeans is not None:
            pred = self.kmeans.predict([dominant_bgr])
            return int(pred[0])
            
        return -1

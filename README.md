# Globussoft Assignment Submission

**Name:** Chandana Jagadish 
**Date:** 22nd April 2026

---

## What This Repo Contains

This repository contains solutions for both tasks assigned by Globussoft.

---
## NOTE: I have also added the required comments in the code for better understanding

## Task 1 — Amazon.in Web Scraper

**File:** `task1/amazon_scraper.py`

### What it does:
Scrapes laptop listings from Amazon.in and saves them to a CSV file with a timestamp in the filename.

### Data collected:
- Product Title
- Price
- Rating
- Ad / Organic result type
- Product Image URL
- Product Link

### How to run:
```bash
cd Task1-Amazon web scraping
pip install requests beautifulsoup4 pandas
python amazon_scraper.py
```

### Output:
A CSV file named like: `amazon_laptops_20260422_143055.csv`

---

## Task 2 — Face Authentication (Face Verification)

**Files:**
- `Task 2-Face authentication/train.py` — loads and prepares the FaceNet model
- `Task 2-Face authentication/face_auth.py` — FastAPI service for face verification

### What it does:
A web API that accepts two face images and tells you if they are the same person or different people.

### Returns:
- `verification_result` — "same person" or "different person"
- `similarity_score` — float between 0.0 and 1.0
- `face1_bounding_box` — x, y, width, height of face in image 1
- `face2_bounding_box` — x, y, width, height of face in image 2

### Model Used:
**FaceNet** via the DeepFace library (pre-trained open-source model by Google)

### How to run:

**Step 1 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 2 — Prepare the model (run once):**
```bash
cd Task 2-Face authentication
python train.py
```

**Step 3 — Start the API:**
```bash
python face_auth.py
```

**Step 4 — Test in browser:**
Once we run the file don't forget to add "/docs" for the below link in the web address tab of your browser if its not present
```
http://127.0.0.1:8000/docs
```

Upload two face images using the `/verify` endpoint and click Execute.

### Sample Output:
```json
{
  "verification_result": "same person",
  "similarity_score": 0.8732,
  "threshold_used": 0.70,
  "face1_bounding_box": {"x": 142, "y": 80, "width": 120, "height": 120},
  "face2_bounding_box": {"x": 98, "y": 65, "width": 115, "height": 118},
  "model_used": "FaceNet (via DeepFace)"
}
```

---

## Sample Images

The `sample_images/` folder contains test face images you can use to try the API.

---

## Repo Structure

```
├── Task 1-Amazon web scraping/
│   └── amazon_scraper.py
├── Task 2-Face authentication/
│   ├── train.py
│   └── face_auth.py
├── sample_images/
│   ├── face1.jpg
│   └── face2.jpg
├── requirements.txt
└── README.md
```

---

## Libraries Used

| Library | Purpose |

| requests | Fetch web pages |
| beautifulsoup4 | Parse HTML |
| pandas | Save data to CSV |
| fastapi | Build web API |
| uvicorn | Run the API server |
| deepface | Face detection + embeddings |
| opencv-python | Image processing |
| numpy | Math on arrays |

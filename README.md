# 🎬 videoRanking.py

A Python script to analyze and rank video files in a folder based on their technical quality.

## 🔍 What It Does

`videoRanking.py` scans a folder containing video files and generates a CSV report that includes:

- File name and last modified date
- Raw technical data: resolution, video/audio bitrate, codecs, audio channels, source type
- A technical quality score (per metric and total)

The script is useful for comparing different versions of the same video (e.g., different encodings of a movie or lecture) to choose the best-quality file.

---

## 🧠 Scoring Criteria

| Metric             | Description                              | Score |
|--------------------|------------------------------------------|-------|
| **Resolution**     | Based on height (e.g., 2160p, 1080p...)  | 1–4   |
| **Video Bitrate**  | Higher bitrate = better quality          | 1–3   |
| **Video Codec**    | HEVC/H.265 preferred over AVC/H.264      | 1–2   |
| **Audio Channels** | 5.1 (surround) preferred over stereo     | 1–2   |
| **Audio Bitrate**  | Bonus if >192 kbps                       | 0–1   |
| **Source**         | Bonus if BluRay is detected in metadata  | 0–2   |

Each file gets a **total score** based on the sum of these metrics.

---

## 📦 Output

A CSV file named `video_quality_report.csv` is created in the scanned folder. It contains:

- All technical data
- Individual scores per metric
- A total score
- File modification timestamps

Example structure:

| File Name | Resolution (px) | Video Bitrate (bps) | Audio Channels | Total Score | Last Modified |
|-----------|------------------|----------------------|----------------|--------------|----------------|
| file1.mkv | 1920x1080        | 5600000              | 6              | 10           | 2025-04-13     |

---

## ▶️ Usage

### Prerequisites

- Python 3.x
- [MediaInfo](https://mediaarea.net/en/MediaInfo/Download) must be installed on your system
- Install Python dependency:

```bash
pip install pymediainfo

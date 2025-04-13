"""
videoRanking.py
----------------

Analyzes all video files in a given folder and generates a CSV report including:

- File name
- Technical quality score (total and by metric)
- Raw technical details: resolution, bitrate, codec, etc.
- Last modification date

🎯 Scoring criteria:

1. Resolution height:
   - 2160p (4K): +4
   - 1080p: +3
   - 720p: +2
   - 480p: +1

2. Video bitrate (bps):
   - > 8 Mbps: +3
   - 4–8 Mbps: +2
   - 1–4 Mbps: +1

3. Video codec:
   - H.265 / HEVC: +2
   - H.264: +1

4. Audio channels:
   - ≥ 6: +2
   - = 2: +1

5. Audio bitrate:
   - > 192 kbps: +1

6. Source:
   - Metadata contains 'BluRay': +2

📌 Usage:

    python videoRanking.py "/path/to/video/folder"

Requirements:
    - Python 3
    - pymediainfo (`pip install pymediainfo`)
    - MediaInfo installed: https://mediaarea.net/en/MediaInfo/Download
"""

import os
import csv
import argparse
from datetime import datetime
from pymediainfo import MediaInfo

VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm']

def is_video_file(filename):
    return any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS)

def get_detailed_score_and_data(info):
    width = height = video_bitrate = audio_bitrate = audio_channels = None
    resolution_str = "Unknown"
    video_codec = audio_codec = "Unknown"
    source_type = ""

    resolution_score = 0
    video_bitrate_score = 0
    video_codec_score = 0
    audio_channels_score = 0
    audio_bitrate_score = 0
    source_score = 0

    for track in info.tracks:
        if track.track_type == 'Video':
            if track.width and track.height:
                width = track.width
                height = track.height
                resolution_str = f"{width}x{height}"
                if height >= 2000:
                    resolution_score = 4
                elif height >= 1080:
                    resolution_score = 3
                elif height >= 720:
                    resolution_score = 2
                elif height >= 480:
                    resolution_score = 1
            if track.bit_rate:
                video_bitrate = int(track.bit_rate)
                if video_bitrate > 8000000:
                    video_bitrate_score = 3
                elif video_bitrate > 4000000:
                    video_bitrate_score = 2
                else:
                    video_bitrate_score = 1
            if track.codec_id:
                codec = track.codec_id.lower()
                video_codec = codec
                if '265' in codec or 'hevc' in codec:
                    video_codec_score = 2
                elif '264' in codec:
                    video_codec_score = 1

        elif track.track_type == 'Audio':
            if track.channel_s:
                audio_channels = int(track.channel_s)
                if audio_channels >= 6:
                    audio_channels_score = 2
                elif audio_channels == 2:
                    audio_channels_score = 1
            if track.bit_rate:
                audio_bitrate = int(track.bit_rate)
                if audio_bitrate > 192000:
                    audio_bitrate_score = 1
            if track.codec_id:
                audio_codec = track.codec_id

        elif track.track_type == 'General':
            if track.internet_media_type and 'blu' in track.internet_media_type.lower():
                source_type = 'BluRay'
                source_score = 2

    total_score = sum([
        resolution_score,
        video_bitrate_score,
        video_codec_score,
        audio_channels_score,
        audio_bitrate_score,
        source_score
    ])

    return {
        'Width': width,
        'Height': height,
        'Resolution (px)': resolution_str,
        'Resolution Score': resolution_score,

        'Video Bitrate (bps)': video_bitrate,
        'Video Bitrate Score': video_bitrate_score,

        'Video Codec': video_codec,
        'Video Codec Score': video_codec_score,

        'Audio Channels': audio_channels,
        'Audio Channels Score': audio_channels_score,

        'Audio Bitrate (bps)': audio_bitrate,
        'Audio Bitrate Score': audio_bitrate_score,

        'Source Type': source_type,
        'Source Score': source_score,

        'Total Score': total_score
    }

def analyze_folder(folder_path, output_csv="video_quality_report.csv"):
    files = [f for f in os.listdir(folder_path) if is_video_file(f)]
    results = []

    for file in files:
        full_path = os.path.join(folder_path, file)
        media_info = MediaInfo.parse(full_path)
        scores = get_detailed_score_and_data(media_info)
        mod_time = os.path.getmtime(full_path)
        mod_datetime = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

        row = {
            'File Name': file,
            **scores,
            'Last Modified': mod_datetime
        }
        results.append(row)

    ranked = sorted(results, key=lambda x: x['Total Score'], reverse=True)

    csv_path = os.path.join(folder_path, output_csv)
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'File Name',
            'Width', 'Height', 'Resolution (px)', 'Resolution Score',
            'Video Bitrate (bps)', 'Video Bitrate Score',
            'Video Codec', 'Video Codec Score',
            'Audio Channels', 'Audio Channels Score',
            'Audio Bitrate (bps)', 'Audio Bitrate Score',
            'Source Type', 'Source Score',
            'Total Score', 'Last Modified'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ranked)

    print(f"\n✅ Report saved as: {csv_path}")
    print("\n📊 Quality Ranking:")
    for rank, entry in enumerate(ranked, start=1):
        print(f"{rank}. {entry['File Name']} — Total Score: {entry['Total Score']} — Last Modified: {entry['Last Modified']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze the technical quality of video files in a folder.")
    parser.add_argument("folder", help="Path to the folder containing video files")
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print("❌ Error: The specified path is not a valid folder.")
    else:
        analyze_folder(args.folder)

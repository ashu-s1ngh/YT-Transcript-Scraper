import os
import re
import glob
import time
import random
import socket
import shutil
import zipfile
import scrapetube
import yt_dlp

# Force IPv4 to prevent Windows SSL hangs
def force_ipv4():
    old_getaddrinfo = socket.getaddrinfo
    def new_getaddrinfo(*args, **kwargs):
        responses = old_getaddrinfo(*args, **kwargs)
        return [response for response in responses if response[0] == socket.AF_INET]
    socket.getaddrinfo = new_getaddrinfo

force_ipv4()

class YouTubeScraper:
    def __init__(self, output_dir="transcripts"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def log(self, msg, callback=None):
        print(msg)
        if callback:
            callback(msg)

    def get_channel_videos(self, channel_url, sort_by='newest', callback=None):
        self.log(f"Fetching videos from: {channel_url} (Sort: {sort_by})", callback)
        try:
            videos = scrapetube.get_channel(channel_url=channel_url, sort_by=sort_by)
            return videos
        except Exception as e:
            self.log(f"Error fetching channel: {e}", callback)
            return []

    def clean_vtt_text(self, vtt_content):
        lines = vtt_content.splitlines()
        text_lines = []
        seen = set()
        
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('WEBVTT'): continue
            if '-->' in line: continue
            if line.startswith('NOTE'): continue
            
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = clean_line.strip()
            
            if clean_line and clean_line not in seen:
                text_lines.append(clean_line)
                seen.add(clean_line)
                
        return " ".join(text_lines)

    def download_transcript(self, video_id, title, callback=None):
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        safe_title = safe_title.replace(" ", "_")
        
        # Check for cookies.txt first
        if os.path.exists('cookies.txt'):
            auth_opts = {'cookiefile': 'cookies.txt'}
        else:
            auth_opts = {'cookiesfrombrowser': ('chrome',)}

        ydl_opts = {
            'skip_download': True,
            'writesub': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'subtitlesformat': 'vtt',
            'outtmpl': os.path.join(self.output_dir, f"{safe_title}_{video_id}"),
            'quiet': True,
            'no_warnings': True,
            **auth_opts
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            pattern = os.path.join(self.output_dir, f"{safe_title}_{video_id}*.vtt")
            files = glob.glob(pattern)
            
            if not files:
                self.log(f"✗ No transcript: {title}", callback)
                return False
                
            vtt_file = files[0]
            
            with open(vtt_file, 'r', encoding='utf-8') as f:
                vtt_content = f.read()
                
            clean_text = self.clean_vtt_text(vtt_content)
            
            txt_filename = os.path.join(self.output_dir, f"{safe_title}_{video_id}.txt")
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(clean_text)
                
            os.remove(vtt_file)
            self.log(f"✓ Saved: {os.path.basename(txt_filename)}", callback)
            return True
            
        except Exception as e:
            self.log(f"✗ Error {video_id}: {str(e)}", callback)
            return False

    def zip_transcripts(self, callback=None):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"Transcripts_{timestamp}.zip"
        zip_path = os.path.join(self.output_dir, zip_name)
        
        self.log(f"Zipping files to {zip_name}...", callback)
        try:
            files_to_zip = []
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(self.output_dir):
                    for file in files:
                        if file.endswith(".txt"):
                            full_path = os.path.join(root, file)
                            zipf.write(full_path, file)
                            files_to_zip.append(full_path)
                            
            self.log(f"✓ Created ZIP: {zip_name}", callback)
            
            # Cleanup text files
            for f in files_to_zip:
                try:
                    os.remove(f)
                except:
                    pass
            self.log("✓ Cleaned up text files", callback)
            
            return True
        except Exception as e:
            self.log(f"Error zipping: {e}", callback)
            return False

    def run_scrape(self, channel_url, limit=10, sort_by='newest', callback=None):
        videos = self.get_channel_videos(channel_url, sort_by, callback)
        processed = 0
        
        for video in videos:
            if processed >= limit:
                break
                
            video_id = video['videoId']
            title = video['title']['runs'][0]['text']
            
            self.log(f"Processing {processed+1}/{limit}: {title}", callback)
            if self.download_transcript(video_id, title, callback):
                processed += 1
                
            sleep_time = random.uniform(3, 7)
            time.sleep(sleep_time)
                
        self.log(f"Done! Processed {processed} videos.", callback)
        self.zip_transcripts(callback=callback)

# CLI Interface (Backward Compatibility)
def main():
    scraper = YouTubeScraper()
    channel_url = input("Enter YouTube Channel URL: ").strip()
    try:
        limit = int(input("How many videos to scrape? (default 10): ") or 10)
    except ValueError:
        limit = 10
        
    # Clear buffer/Wait
    time.sleep(0.5)
    try:
        sort_choice = input("Sort by (latest/popular)? (default latest): ").strip().lower()
    except EOFError:
        sort_choice = 'latest'
        
    sort_by = 'popular' if sort_choice.startswith('p') else 'newest'
    
    scraper.run_scrape(channel_url, limit, sort_by)

if __name__ == "__main__":
    main()

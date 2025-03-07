from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import os

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    return None

def get_video_description(api_key, video_url):
    """Fetch video description using YouTube Data API"""
    try:
        # Create YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Get video ID from URL
        video_id = get_video_id(video_url)
        if not video_id:
            return "Invalid YouTube URL"
        
        # Make API request
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        
        # Extract description
        if response['items']:
            return response['items'][0]['snippet']['description']
        return "Video not found"
        
    except Exception as e:
        return f"Error: {str(e)}"

def save_description_to_file(video_id, description):
    """Save the video description to a text file"""
    filename = f"description_{video_id}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(description)
    return filename

def main():
    # Replace with your API key
    API_KEY = os.environ.get('youtube_api_key')
    
    # Example usage
    video_url = input("Enter YouTube video URL: ")
    description = get_video_description(API_KEY, video_url)
    print("\nVideo Description:")
    print(description)
    
    # Save to file
    video_id = get_video_id(video_url)
    if video_id and description != "Video not found" and not description.startswith("Error:"):
        filename = save_description_to_file(video_id, description)
        print(f"\nDescription saved to: {filename}")

if __name__ == "__main__":
    main()

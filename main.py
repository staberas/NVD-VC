import os
import requests
import subprocess
import re

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    """
    Helper function to sort strings containing numbers in a natural way
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]  

def generate_url_sequence(base_url, start_filename, end_filename):
    """
    Generates a sequence of URLs with increasing numbers after the base URL.

    Args:
        base_url: The base URL string.
        start_filename: The filename of the first file in the sequence.
        end_filename: The filename of the last file in the sequence.

    Returns:
        A list of tuples containing the URL and its existence status (True if found, False otherwise).
    """
    urls = []
    
    start_num = int(start_filename.split(".")[0])
    end_num = int(end_filename.split(".")[0])

    # Determine if leading zeros are present in filenames
    num_digits = len(start_filename.split(".")[0])
    has_leading_zeros = start_filename.startswith("0")

    for num in range(start_num, end_num + 1):
        if has_leading_zeros:
            url = f"{base_url}{str(num).zfill(num_digits)}.ts"
        else:
            url = f"{base_url}{num}.ts"

        response = requests.get(url)
        exists = response.status_code == 200
        print("Checking: ",url," Status-",exists)
        urls.append((url, exists))

    return urls

def save_urls_to_file(urls, filename):
    """
    Save list of URLs to a text file.

    Args:
        urls: List of tuples containing URL and existence status.
        filename: Name of the text file to save.
    """
    with open(filename, 'w') as file:
        for url, _ in urls:
            file.write(f"{url}\n")

def download_files(urls, output_folder):
    """
    Download files from URLs to the specified output folder.

    Args: 
        urls: List of tuples containing URL and existence status.
        output_folder: Path to the folder where files will be downloaded.
    """
    os.makedirs(output_folder, exist_ok=True)

    for url, exists in urls:
        if exists:
            print("Downloading: ",url)
            filename = os.path.basename(url)
            output_path = os.path.join(output_folder, filename)
            with open(output_path, 'wb') as file:
                response = requests.get(url)
                file.write(response.content)

def generate_relative_paths(ts_file_paths):
    """
    Generates relative paths for the list of .ts files.

    Args:
        ts_file_paths: List of absolute paths to .ts files.

    Returns:
        List of relative paths.
    """
    relative_paths = []
    for ts_file_path in ts_file_paths:
        relative_path = os.path.basename(ts_file_path)
        relative_paths.append(relative_path)
    return relative_paths

def combine_ts_to_mp4(base_folder, output_file):
    """
    Combine all .ts files in the base folder into a single .mp4 file using FFmpeg.
    Sorts the .ts files numerically.

    Args:
        base_folder: Path to the base folder containing .ts files.
        output_file: Path for the output .mp4 file.
    """
    # Create a list to hold all .ts file paths
    ts_file_paths = []

    # Walk through the base folder
    for filename in os.listdir(base_folder):
        if filename.endswith('.ts'):
            ts_file_path = os.path.join(base_folder, filename)
            ts_file_paths.append(ts_file_path)

    # Sort the file paths using the natural sort key
    ts_file_paths.sort(key=natural_sort_key)

    # Run FFmpeg command to combine .ts files
    ffmpeg_command = [
        'ffmpeg',
        '-i', 'concat:' + '|'.join(ts_file_paths),
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        output_file
    ]

    subprocess.run(ffmpeg_command)

def main():
    """
    Reads base URL, starting and ending filenames from the user,
    generates the sequence, saves it to a text file, downloads the files,
    and combines them into an MP4 file.
    """
    base_url = input("Enter the base URL: ")
    start_filename = input("Enter the filename of the first file in the sequence: ")
    end_filename = input("Enter the filename of the last file in the sequence: ")

    urls = generate_url_sequence(base_url, start_filename, end_filename)

    # Save URLs to a text file
    save_urls_to_file(urls, "DLVIDEO/file_list.txt")

    # Download files
    download_files(urls, "DLVIDEO")

    # Combine .ts files into an MP4 file
    combine_ts_to_mp4("DLVIDEO", "DLVIDEO/output.mp4")

    print("Download and video conversion completed successfully!")

if __name__ == "__main__":
    main()


import os
import traceback
import shutil
from pydub import AudioSegment
import numpy as np
import scipy.signal as signal


import os
import numpy as np
from scipy import signal
from pydub import AudioSegment

def remove_low_frequencies(file_path, cutoff):
    print(f"Processing: {file_path}")

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"Error: File '{file_path}' does not exist or is empty.")
        return

    try:
        audio = AudioSegment.from_file(file_path, format="ogg")
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    sample_rate = audio.frame_rate
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(5, normal_cutoff, btype='high', analog=False)

    filtered_samples = signal.lfilter(b, a, samples)

    filtered_samples = np.clip(filtered_samples, -32768, 32767).astype(np.int16)

    filtered_audio = AudioSegment(
        data=filtered_samples.tobytes(),
        sample_width=2,
        frame_rate=sample_rate,
        channels=audio.channels
    )

    filtered_audio.export(file_path, format="ogg", codec="libvorbis")
    print(f"Processed and saved: {file_path}")

def find_update_folder():
    for root, dirs, files in os.walk("."):
        if "Update" in dirs:
            return os.path.join(root, "Update")
    return None

def sanitize_filename(filename):
    # Remove any characters that are not letters, numbers, underscores, or periods
    return ((''.join(c for c in filename if c.isalnum() or c in ['.'] or c in [' '] or c in ['_'] or c in ['-']))).replace(" ", "_")

def rename_files(folder_path2, prefix):
    folder_path = shutil.copytree("Update", "Output")
    shutil.rmtree("Update")
    os.mkdir("Update")
    for root, dirs, files in os.walk(folder_path):
        for i, file in enumerate(files, start=1):
            filename, file_extension = os.path.splitext(file)
            parts = root.split("/")
            # Ensure there are enough parts in the list to prevent IndexError
            if len(parts) > 1 and file != "pack.json":
                name = parts[2]
                moru = parts[1]
                if name == filename.split("_")[0]:
                    if (file_extension == ".ogg"):
                        print("Removing < 20hz " + filename)
                        remove_low_frequencies(os.path.join(root, file),20)
                else:
                    print("doing " + filename)
                    clicksOrRelease = parts[3]
                    clicksOrRelease2 = parts[3]
                    if clicksOrRelease2 == "Releases":
                        clicksOrRelease2 = "Release"
                    directory_name = os.path.basename(root)
                    ee = parts[2]
                    new_filename = f"{ee}_{clicksOrRelease2}_{moru}_{i}{file_extension}"
                    # Sanitize the new file name
                    new_filename = sanitize_filename(new_filename)
                    root2 = '/'.join(parts[0:4])
                    os.rename(os.path.join(root, file), os.path.join(root2, new_filename))
                    # Convert the renamed file to ogg
                    convert_to_ogg(os.path.join(root, new_filename))
            else:
                if file != "pack.json":
                    print(f"Error: The path '{root}' does not contain enough elements to proceed with renaming.")

def convert_to_ogg(input_file):
    try:
        input_file_extension = os.path.splitext(input_file)[1]
        if input_file_extension.lower() == ".ogg":
            print(f"Skipping conversion for {input_file}. Already in OGG format.")
            return input_file
        
        output_file = os.path.splitext(input_file)[0] + ".ogg"
        
        print(f"Converting {input_file} to OGG format...")
        
        # Convert audio to OGG format using pydub with specified FFmpeg path
        audio = AudioSegment.from_file(input_file, format=input_file_extension[1:], ffmpeg="ffmpeg")
        audio.export(output_file, format="ogg", codec="libvorbis")
        
        print(f"Successfully converted {input_file} to {output_file}")
        remove_low_frequencies(output_file,20)

        os.remove(input_file)
        
        return output_file
    except Exception as e:
        print(f"Error converting {input_file} to OGG format: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    update_folder = find_update_folder()
    if update_folder:
        #prefix = input("Enter the prefix: ")
        prefix = "hi"
        # Set the path to the ffmpeg executable that's in the script directory
        #ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'ffmpeg.exe')
        if os.path.exists("Output"):
            shutil.rmtree("Output")
        rename_files(update_folder, prefix)
        print("Files renamed, converted, and original files removed successfully!")
    else:
        print("Update folder not found in the current directory.")

from mammoth import Mammoth
import signal
from constants import NOGGIN_URL, MAMMOTH_WORKERS
import os
import requests
import subprocess
from tempfile import NamedTemporaryFile
import traceback
from uploader import Uploader

# The following is application specific logic
class Clipper:

    def __init__(self, session, request, job_id):
        self.session = session
        self.request = request
        self.job_id = job_id

        self.input_file = request.request_json.get('input_file')
        self.clips = request.request_json.get('clips')
        self.output_filename = request.request_json.get('output_filename')
        self.output_extension = request.request_json.get('output_extension')
        self.encoding_profile = request.request_json.get('output_profile')
        self.stitched = request.request_json.get('stitched')
        self.rclone_remote_label = request.request_json.get('rclone_remote_label')
        self.bucket_name = request.request_json.get('bucket_name')

        self.b2_base_url = "https://f002.backblazeb2.com/file"
        self.temp_file = NamedTemporaryFile(delete=False)


    def log(self, message):
        print(self.job_id, message)
        mammoth.insert_event(self.session, self.job_id, message)
    
    def construct_b2_url(self, bucket_name, file_path):
        """Constructs a download URL for a file stored in Backblaze B2."""
        return f"{self.b2_base_url}/file/{bucket_name}/{file_path}"

    def download_file(self) -> str:
        try:
            r = requests.get(self.input_file)
            r.raise_for_status()
        except Exception:
            traceback_str = traceback.format_exc()
            self.log(traceback_str)
            return False

        self.temp_file.write(r.content)
        self.temp_file.close()
        return os.path.exists(self.temp_file.name)

    def process_video_clips(self):
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)

        preset_file_path = os.path.join(os.path.dirname(__file__), f'{self.encoding_profile}')

        if not os.path.isfile(preset_file_path):
            self.log(f"Error: Output profile file '{preset_file_path}' not found.")
            return False

        preset_options = []
        try:
            with open(preset_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    option, value = line.split('=', 1)
                    preset_options.extend(['-' + option, value.strip()])
        except Exception:
            traceback_str = traceback.format_exc()
            self.log(traceback_str)

        output_files = []  # For keeping track of all generated clip files
        upload_files = []
        try:
            for clip in self.clips:
                output_clip_name = os.path.join(output_dir, f"{clip.get('title').replace(' ', '_')}{self.output_extension}") if not self.stitched else NamedTemporaryFile(delete=False, dir=output_dir, suffix=self.output_extension).name
                command = ["ffmpeg", "-i", self.temp_file.name, "-ss", str(clip.get('in')), "-t", str(clip.get('out') - clip.get('in')), "-y"] + preset_options + [output_clip_name]
            
                command_string = " ".join(command)
                #print(command_string)
                #input()
                self.log(command_string)

                subprocess.run(command, check=True)
                output_files.append(output_clip_name)

            if self.stitched:
                # If stitched is True, concatenate all the generated clips into a single file
                concat_file_path = NamedTemporaryFile(mode='w+', delete=False, dir=output_dir).name
                with open(concat_file_path, 'w') as f:
                    for output_file in output_files:
                        f.write(f"file '{output_file}'\n")

                final_output_filename = os.path.join(output_dir, self.output_filename + self.output_extension)
                concat_command = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file_path, "-c", "copy", "-y", final_output_filename]

                command_string = " ".join(concat_command)
                #print(command_string)
                #input()

                self.log(command_string)

                subprocess.run(concat_command, check=True)
                # Cleanup temporary files
                for output_file in output_files:
                    os.remove(output_file)
                os.remove(concat_file_path)
                upload_files.append(final_output_filename)
            else:
                for output_file in output_files:
                    upload_files.append(output_file)
        except Exception as ex:
            traceback_str = traceback.format_exc()
            self.log(traceback_str)

        return upload_files

    # The above is application specific logic

def custom_process_function(session, request, job_id):
        clipper = Clipper(session, request, job_id)

        is_downloaded = clipper.download_file()

        if is_downloaded:

            upload_files = clipper.process_video_clips()
            uploaded_file_urls = []
            upload_successes = []

            if upload_files:
                uploader = Uploader(clipper.rclone_remote_label, clipper.bucket_name)

                for file_path in upload_files:
                    # Simulate or perform the upload; the method might just return True/False for success/failure
                    upload_success = uploader.upload_file(file_path, os.path.basename(file_path))
                    upload_successes.append(upload_success)

                    clipper.log(f"Upload result:{upload_success}, file:{file_path}")

                    if upload_success:
                        # Construct the URL after the fact
                        uploaded_url = clipper.construct_b2_url(clipper.bucket_name, os.path.basename(file_path))
                        uploaded_file_urls.append(uploaded_url)
                        clipper.log(f"Upload succeeded:{file_path}, available at:{uploaded_url}")
                    else:
                        clipper.log(f"Upload failed:{file_path}")
                    
                    # Delete the local file
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass

                #return JSONResponse(status_code=200, content={"status": "success", "message": "Video processed and uploaded", "urls": uploaded_file_urls})

                if all(upload_successes):
                    clipper.log("All files processed and uploaded successfully!")

                    # Optional: Send HTTP request to somewhere notifying operation completion...
                    #print(200, f"All files processed and uploaded successfully!")
                    #print(uploaded_file_urls)

                    return True
                else:
                    print("At least 1 or more uploads have failed...")
                    clipper.log("At least 1 or more uploads have failed...")

            return False

# Initialize Mammoth


mammoth = Mammoth(process_request_data=custom_process_function, noggin_url=NOGGIN_URL, workers=MAMMOTH_WORKERS)

def signal_handler(sig, frame):
    print("CTRL+C pressed! Stopping Mammoth...")
    mammoth.stop()

if __name__ == "__main__":
    # Register SIGINT handler
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting Mammoth... Press CTRL+C to stop.")
    mammoth.run()

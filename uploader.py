import os
import argparse
import subprocess
import hashlib

class Uploader:
    def __init__(self, rclone_remote_label, bucket_name):
        self.rclone_remote_label = rclone_remote_label
        self.bucket_name = bucket_name

    def calculate_sha1(self, file_path):
        """
        Calculate the SHA1 checksum of a file.
        """
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)  # Read in 64k chunks
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    def verify_checksum(self, local_path, remote_path):
        """
        Verify the SHA1 checksum of a local file against the remote file.
        """
        local_sha1 = self.calculate_sha1(local_path)
        print(f"Local SHA1 checksum: {local_sha1}")

        full_remote_path = f"{self.rclone_remote_label}:{self.bucket_name}/{os.path.basename(remote_path)}"
        remote_sha1_command = ['rclone', 'hashsum', 'SHA1', full_remote_path]
        result = subprocess.run(remote_sha1_command, check=True, capture_output=True, text=True)

        if result.stdout:
            remote_sha1 = result.stdout.split()[0]
            print(f"Remote SHA1 checksum: {remote_sha1}")

            if local_sha1 == remote_sha1:
                print("SHA1 checksum verification successful.")
                return True
            else:
                print("SHA1 checksum verification failed. File may be corrupted during transfer.")
                return False
        else:
            print(f"No SHA1 checksum received from remote for file: {full_remote_path}")
            return False

    def upload_file(self, file_path, cloud_filename=None):
        if not cloud_filename:
            cloud_filename = os.path.basename(file_path)

        remote_path = f"{self.rclone_remote_label}:{self.bucket_name}/{cloud_filename}"


        print(" ".join(["rclone", "copyto", file_path, remote_path]))

        # Use rclone to copy the file to the specified bucket in remote storage
        subprocess.run(["rclone", "copyto", file_path, remote_path], check=True)
        print(f'File uploaded successfully as {cloud_filename}')

        # Verify checksum
        if self.verify_checksum(file_path, remote_path):
            print("File integrity verified.")
            return True
        else:
            print("Warning: File integrity could not be verified.")
            return False

def main():
    parser = argparse.ArgumentParser(description='Upload files with SHA1 checksum verification.')
    parser.add_argument('file_path', type=str, help='Path to the file to upload')
    parser.add_argument('--cloud_filename', type=str, default=None, help='Custom filename for the file in the cloud')
    parser.add_argument('--rclone_remote_label', type=str, required=True, help='Rclone remote label')
    parser.add_argument('--bucket_name', type=str, required=True, help='Bucket name in cloud storage')

    args = parser.parse_args()

    uploader = Uploader(args.rclone_remote_label, args.bucket_name)
    uploader.upload_file(args.file_path, args.cloud_filename)

if __name__ == '__main__':
    main()

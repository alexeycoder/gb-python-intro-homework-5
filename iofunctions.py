import os


def get_files_paths(directory_path, files_common_name, files_extension):
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return None

    files_list = [os.path.join(directory_path, f) for f in os.listdir(directory_path)
                  if f.startswith(files_common_name) and f.endswith(files_extension)]

    return files_list if len(files_list) > 0 else None

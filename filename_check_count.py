import os

# Define your directories here
dir1 = '../../DATA/videos2'
dir2 = '../../DATA/labels'

# Count and print the number of files in each folder
num_files_dir1 = len(os.listdir(dir1))
num_files_dir2 = len(os.listdir(dir2))

print(f"Number of files in {dir1}: {num_files_dir1}")
print(f"Number of files in {dir2}: {num_files_dir2}")

# List comprehension to get file names without extensions
files1 = {os.path.splitext(file)[0] for file in os.listdir(dir1)}
files2 = {os.path.splitext(file)[0] for file in os.listdir(dir2)}

# Find matches and differences
same_files = files1.intersection(files2)
different_files = files1.symmetric_difference(files2)

# Print counts
print(f"Number of file names that are the same: {len(same_files)}")
print(f"Number of file names that are not the same: {len(different_files)}")

if different_files:
    print("Names of files that are different:")
    for file in different_files:
        print(file)
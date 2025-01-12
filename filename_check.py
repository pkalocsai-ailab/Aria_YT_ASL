import os

# Define your directories here
dir1 = 'G:/A_VSBLTY/MarketSquare/data_v17_32SKU/combined_v17_32SKU/images/train'
dir2 = 'G:/A_VSBLTY/MarketSquare/data_v17_32SKU/combined_v17_32SKU/labels/train'

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
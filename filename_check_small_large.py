import os

# Paths to the two directories
#dir1_path = 'G:/A_VSBLTY/MarketSquare/data4/images'
#dir2_path = 'G:/A_VSBLTY/MarketSquare/data4/negative_images'
dir1_path = 'G:/A_VSBLTY/MarketSquare/data4/images'
dir2_path = 'G:/A_VSBLTY/MarketSquare/data4/extensions/additions/images'

# List of file names in each directory
dir1_files = os.listdir(dir1_path)
dir2_files = os.listdir(dir2_path)

# Determine the smaller and larger directory
smaller_dir_files, larger_dir_files = (dir1_files, dir2_files) if len(dir1_files) < len(dir2_files) else (dir2_files, dir1_files)

# Convert the file list of the larger directory into a set for faster search
larger_dir_files_set = set(larger_dir_files)

# Check for common file names
common_files = [file for file in smaller_dir_files if file in larger_dir_files_set]

# Count the number of common files
number_of_common_files = len(common_files)

# Print the result
if common_files:
    print(f"Common files found: {common_files}")
    print(f"Number of common files found: {number_of_common_files}")
else:
    print("No common files found.")

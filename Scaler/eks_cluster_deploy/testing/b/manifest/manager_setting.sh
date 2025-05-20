#!/bin/bash

# configure min-rep, max-rep, cpu-utilization
# for Microservice Manager

# Ensure correct usage
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <target_dir_or_file> <min_rep> <max_rep> <target_cpu_utilization>"
    exit 1
fi

TARGET=$1
MIN_REP=$2
MAX_REP=$3
CPU_UTIL=$4

# Function to update a single file
update_file() {
    local file="$1"
    echo "Updating $file"
    sed -i -E \
        -e "s/(^\s*--min_reps=)/\1${MIN_REP}/" \
        -e "s/(^\s*--max_reps=)/\1${MAX_REP}/" \
        -e "s/(^\s*--target_cpu_utilization=)/\1${CPU_UTIL}/" "$file"
}

# Check if the target is a directory or a file
if [ -d "$TARGET" ]; then
    for file in "$TARGET"/*; do
        if [ -f "$file" ]; then
            update_file "$file"
        fi
    done
    echo "All files in $TARGET updated successfully."
elif [ -f "$TARGET" ]; then
    update_file "$TARGET"
    echo "File $TARGET updated successfully."
else
    echo "Error: $TARGET is not a valid file or directory."
    exit 1
fi

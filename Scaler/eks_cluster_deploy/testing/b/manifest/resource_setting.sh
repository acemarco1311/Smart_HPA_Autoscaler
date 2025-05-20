#!/bin/bash

# update .yaml file, request cpu/memory, limit cpu/memory
# input: dir/file target, cpu_request, cpu_limit, mem_request, mem_limit

# Ensure correct usage
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <directory_or_file> <cpu_request> <cpu_limit> <mem_request> <mem_limit>"
    exit 1
fi

TARGET=$1
CPU_REQUEST=$2
CPU_LIMIT=$3
MEM_REQUEST=$4
MEM_LIMIT=$5

# Function to update a single file
update_file() {
    local file="$1"
    echo "Updating $file"
    awk -v cr="$CPU_REQUEST" -v cl="$CPU_LIMIT" -v mr="$MEM_REQUEST" -v ml="$MEM_LIMIT" '
    BEGIN {cpu_count=0; mem_count=0;}
    {
        if ($0 ~ /^[[:space:]]+cpu:/) {
            cpu_count++;
            if (cpu_count == 1) { sub(/[0-9]+m/, cr"m"); }
            else if (cpu_count == 2) { sub(/[0-9]+m/, cl"m"); }
        }
        if ($0 ~ /^[[:space:]]+memory:/) {
            mem_count++;
            if (mem_count == 1) { sub(/[0-9]+Mi/, mr"Mi"); }
            else if (mem_count == 2) { sub(/[0-9]+Mi/, ml"Mi"); }
        }
        print;
    }' "$file" > temp_file && mv temp_file "$file"
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

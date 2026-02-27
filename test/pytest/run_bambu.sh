#!/usr/bin/env bash
set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <target-directory>"
    exit 1
fi

TARGET_DIR="$(realpath "$1")"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

CWD="$(dirname $(readlink -e ${BASH_SOURCE[0]:-${(%):-%x}}))"

# Unique screen names based on input directory
BASE_NAME="$(basename "$TARGET_DIR")"
cd "$TARGET_DIR"

# Remove old directories
rm -rf wo_arr_part with_arr_part
mkdir wo_arr_part with_arr_part

cp "$CWD/wo_arr_part.sh" "$TARGET_DIR/wo_arr_part/"
cp "$CWD/with_arr_part.sh" "$TARGET_DIR/with_arr_part/"

source /opt/compilers/settings.sh
source /data2/home/fellegara/opt/panda/settings.sh

screen -S wo_arr_part -dm bash -c "cd $TARGET_DIR/wo_arr_part && ./wo_arr_part.sh"
screen -S with_arr_part -dm bash -c "cd $TARGET_DIR/with_arr_part && ./with_arr_part.sh"

echo "Started screen sessions:"
echo "Check with: screen -ls"
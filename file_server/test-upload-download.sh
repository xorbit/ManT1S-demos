#!/bin/sh
echo "Uploading..."
curl -w "@curl-format.txt" -o /dev/null -s "http://mant1s-file/testfile.bin" --upload-file testfile.bin
echo "Downloading..."
curl -w "@curl-format.txt" -o /dev/null -s "http://mant1s-file/testfile.bin"

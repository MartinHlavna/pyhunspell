#!/bin/bash
VERSION="1.7"

# Paths to the files
DLL_PATH="libhunspell-$VERSION-0.dll"
DEF_PATH="libhunspell-$VERSION-0.def"
LIB_PATH="libhunspell-$VERSION-0.lib"

# Check if files exist
if [ ! -f "$DLL_PATH" ]; then
  echo "Error: $DLL_PATH not found."
  exit 1
fi

gendef -p $DLL_PATH
x86_64-w64-mingw32-dlltool -d $DEF_PATH -l $LIB_PATH -D $DLL_PATH

echo "Created $LIB_PATH from $DLL_PATH"

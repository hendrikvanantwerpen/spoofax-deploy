#! /bin/bash

# Clean up previous results
rm -rf out
mkdir -p out

# Resolve, build and bundle jars
../headless/buckminster --loglevel ERROR -update -data workspace --properties buckminster.properties --script buckminster-resolve.script
../headless/buckminster --loglevel ERROR -update -data workspace --properties buckminster.properties --script buckminster-build.script

# Merge jars
sh mkjar.sh

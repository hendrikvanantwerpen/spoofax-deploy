#! /bin/bash

../headless/buckminster --loglevel INFO -update -data workspace --properties buckminster.properties --script buckminster-resolve.script
../headless/buckminster --loglevel INFO -update -data workspace --properties buckminster.properties --script buckminster-build.script

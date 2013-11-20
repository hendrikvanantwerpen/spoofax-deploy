#!/bin/bash

cd workspace
git clone --depth 1 git@github.com:metaborg/jsglr.git
git clone --depth 1 git@github.com:metaborg/mb-exec.git
git clone --depth 1 git@github.com:metaborg/mb-exec-deps.git
git clone --depth 1 git@github.com:metaborg/mb-rep.git
git clone --depth 1 git@github.com:metaborg/runtime-libraries.git
git clone --depth 1 git@github.com:metaborg/spx.git
cd ..

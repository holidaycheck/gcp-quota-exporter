#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

function cleanup {
  docker rmi "${testImageName}"
}

# Build test image and store its name
testImageName=$(docker build -q -f Dockerfile.test .)
readonly testImageName

trap cleanup EXIT

docker run --rm -v "$(pwd):/usr/src/app/" "${testImageName}"

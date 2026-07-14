#!/usr/bin/env bash
set -euo pipefail

dst="/data/home/shenx/code_repositories/GMR_A3/assets/agibot_a3_racket"
src="/data/home/shenx/code_repositories/GMR/a3_31dof_rev_1_0_bundle/meshes"

mkdir -p "${dst}"
for f in "${src}"/*; do
  ln -sf "${f}" "${dst}/$(basename "${f}")"
done
ln -sfn "${src}" "${dst}/meshes"

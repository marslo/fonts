#!/usr/bin/env bash
# =============================================================================
#      FileName : deploy.sh
#        Author : marslo
#       Created : 2026-08-12
#    LastChange : 2026-08-12 04:24:01
# =============================================================================
#
# Package the latest tag as FontPatcher-<tag>.zip and attach it to the matching GitHub release.
#
#   1. tag    : latest                                                ( git describe --tags --abbrev=0 ), e.g. v3.5.0.1
#   2. package: ~/temp/FontPatcher-<tag>.zip                          ( top dir FontPatcher-<tag>/, no .git )
#   3. upload : gh release upload FontPatcher-<tag> <zip> --clobber   ( repo from origin )
#   4. clean  : remove the temp zip                                   ( trap, on any exit )
#
# Usage: bash deploy.sh [--dryrun]

set -euo pipefail

# shellcheck disable=SC2155
declare -r HERE="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd )"
declare -r OUTDIR="${HOME}/temp"
declare dryRun=false
test '--dryrun' = "${1:-}" && dryRun=true

cd "${HERE}"

# latest tag ( e.g. v3.5.0.1 ) and owner/repo parsed from origin ( works for scp-like git@host:owner/repo.git and https://host/owner/repo.git alike )
declare TAG REPO
TAG="$( git describe --tags --abbrev=0 )"
test -n "${TAG}" || { echo 'ERROR: no git tag found' >&2; exit 1; }
REPO="$( git remote get-url origin | sed -E 's#\.git$##' | awk -F'[/:]' '{ print $(NF-1)"/"$NF }' )"
test -n "${REPO}" || { echo 'ERROR: cannot resolve owner/repo from origin' >&2; exit 1; }

declare -r NAME="FontPatcher-${TAG}"
declare -r ZIP="${OUTDIR}/${NAME}.zip"

mkdir -p "${OUTDIR}"
# always remove the temp zip on exit ( success, error, or interrupt )
# shellcheck disable=SC2064
trap "rm -f $( printf '%q' "${ZIP}" )" EXIT

declare -a zipCmd=( git archive --format=zip --prefix="${NAME}/" -o "${ZIP}" "${TAG}" )
declare -a upCmd=( gh release upload "${NAME}" "${ZIP}" --clobber --repo "${REPO}" )

echo ">> tag=${TAG}  repo=${REPO}"
echo ">> [1/2] package -> ${ZIP}  ( top: ${NAME}/ )"
if "${dryRun}"; then
  echo "   [dry-run] ${zipCmd[*]}"
  echo ">> [2/2] upload  -> ${REPO} release ${TAG}"
  echo "   [dry-run] ${upCmd[*]}"
  exit 0
fi

"${zipCmd[@]}"
echo "   $( du -h "${ZIP}" | awk '{ print $1 }' ) written"

echo ">> [2/2] upload -> ${REPO} release ${TAG}"
"${upCmd[@]}"

echo ">> done. ( temp zip removed on exit )"

# vim:tabstop=2:softtabstop=2:shiftwidth=2:expandtab:filetype=sh:

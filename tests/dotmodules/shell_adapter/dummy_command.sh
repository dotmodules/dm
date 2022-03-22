#!/bin/sh

STATUS='0'

while [ "$#" -gt '0' ]
do
  case "$1" in
    --stdout)
      echo "$2"
      shift
      shift
      ;;
    --stderr)
      echo "$2" >&2
      shift
      shift
      ;;
    --status)
      STATUS="$2"
      shift
      shift
      ;;
    *)
      echo "unexpected parameter '$1'"
      exit 1
      ;;
  esac
done

exit "$STATUS"
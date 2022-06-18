#!/bin/sh

while [ "$#" -gt '0' ]
do
  case "$1" in
    --success)
      echo "$2"
      exit 0
      ;;
    --error)
      exit 1
      ;;
    *)
      echo "unexpected parameter '$1'"
      exit 1
      ;;
  esac
done
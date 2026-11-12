#!/bin/bash
# Runs the four load steps with JMeter in non-GUI mode and builds the HTML dashboard for each.
# Usage: ./run-steps.sh [host] [port]
HOST=${1:-127.0.0.1}; PORT=${2:-8000}
for U in 50 100 200 300; do
  jmeter -n -t shoplite-step-load.jmx -Jhost=$HOST -Jport=$PORT -Jusers=$U -Jduration=60 -Jrampup=$((U/5)) \
    -l results/step-$U.jtl -e -o results/dashboard-$U
done

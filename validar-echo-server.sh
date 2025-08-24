#!/bin/bash

echo "Validando echo server..."

MSG="hola"
NETWORK="tp0_testing_net"

RESPONSE=$(docker run --rm --network=$NETWORK busybox:1.36.1-uclibc sh -c "echo -e '$MSG\n' | nc server 12345")

if [ "$RESPONSE" = "$MSG" ]; then
  echo "action: test_echo_server | result: success"
else
  echo "action: test_echo_server | result: fail"
fi

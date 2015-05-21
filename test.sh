#!/usr/bin/env bash

./env/bin/flake8
LINT_EXIT_CODE=$?

echo
./env/bin/py.test $@
TEST_EXIT_CODE=$?


if [ "$LINT_EXIT_CODE" -ne 0 ]; then
    echo
    echo "Linting failed with exit code ${LINT_EXIT_CODE}!"
fi
if [ "$TEST_EXIT_CODE" -ne 0 ]; then
    echo
    echo "Tests failed with exit code ${TEST_EXIT_CODE}!"
fi
if [ "$LINT_EXIT_CODE" -ne 0 ] || [ "$TEST_EXIT_CODE" -ne 0 ]; then
    exit 1
else
    echo
    echo "Success!"
fi

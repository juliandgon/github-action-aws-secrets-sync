#!/bin/bash
set -e

echo "🔎 The name of your branch is ${{ github.ref }} and your repository is ${{ github.repository }}."
echo "ENV var:"
env
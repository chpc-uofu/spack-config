#!/bin/bash

if [ -d "$HOME/spack/local" ]; then
  echo Directory $HOME/spack/local exists, skipping creation.
else
  echo Creating directory $HOME/spack/local
  mkdir -p $HOME/spack/local
fi

if [ -d "$HOME/.spack" ]; then
  echo Directory $HOME/.spack exists, skipping creation.
else
  echo Creating directory $HOME/.spack
  mkdir -p $HOME/.spack
fi

if [ -f "$HOME/.spack/config.yaml" ]; then
  echo File $HOME/.spack/config.yaml exists, skipping copy.
else
  echo Copying file $HOME/.spack/config.yaml
  cp /uufs/chpc.utah.edu/sys/installdir/spack/user/config.yaml $HOME/.spack
fi

if [ -f "$HOME/.spack/upstreams.yaml" ]; then
  echo File $HOME/.spack/upstreams.yaml exists, skipping copy.
else
  echo Copying file $HOME/.spack/upstreams.yaml
  cp /uufs/chpc.utah.edu/sys/installdir/spack/user/upstreams.yaml $HOME/.spack
fi

if [ -f "$HOME/.spack/modules.yaml" ]; then
  echo File $HOME/.spack/modules.yaml exists, skipping copy.
else
  echo Copying file $HOME/.spack/modules.yaml
  cp /uufs/chpc.utah.edu/sys/installdir/spack/user/modules.yaml $HOME/.spack
fi

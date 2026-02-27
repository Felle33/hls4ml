#!/usr/bin/env bash

bambu --top-fname=myproject \
      -lm \
      -I../firmware/ac_types \
      --generate-tb=../myproject_test.cpp \
      --generate-interface=INFER \
      --compiler=I386_CLANG16 \
      -funroll-loops \
      -v4 \
      --no-clean \
      --simulate ../firmware/myproject.cpp |& tee log
#!/usr/bin/env bash
# -I../firmware/ac_types \

bambu --top-fname=myproject \
      -lm \
      --generate-tb=../myproject_test.cpp \
      --generate-interface=INFER \
      --compiler=I386_CLANG16 \
      -v4 \
      --no-clean \
      --simulate ../firmware/myproject.cpp |& tee log.log
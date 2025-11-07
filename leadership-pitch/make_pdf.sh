#!/bin/bash

pandoc -f markdown+emoji \
  --pdf-engine=lualatex \
  -L emoji-direct.lua \
  -V monofont="DejaVu Sans Mono" \
  -V mainfont="DejaVu Serif" \
  -V geometry:top=0.75in \
  -V geometry:bottom=0.75in \
  -V geometry:left=0.75in \
  -V geometry:right=0.75in \
  LEADERSHIP_BRIEF_ORCHESTRATED_AI.md \
  -o orchestrated_ai_draft.pdf

#  -L emoji-wrap.lua \
#pandoc -f markdown+emoji \
#  --pdf-engine=lualatex \
#  -L emoji-wrap.lua \
#  -V geometry:top=0.75in \
#  -V geometry:bottom=0.75in \
#  -V geometry:left=0.75in \
#  -V geometry:right=0.75in \
#  LEADERSHIP_BRIEF_ORCHESTRATED_AI.md \
#  -o orchestrated_ai_draft.pdf

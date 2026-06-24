.PHONY: setup up down skeleton expand tts transcribe assemble validate map load all clean
setup:      ; pip install -r requirements.txt
up:         ; docker compose up -d postgres minio
down:       ; docker compose down
skeleton:   ; python run.py skeleton
expand:     ; python run.py expand
tts:        ; python run.py tts
transcribe: ; python run.py transcribe
assemble:   ; python run.py assemble
validate:   ; python run.py validate
map:        ; python run.py map
load:       ; python run.py load-postgres && python run.py load-minio
all:        ; python run.py all
clean:      ; rm -rf out

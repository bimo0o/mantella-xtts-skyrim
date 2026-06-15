# Mantella-Sims XTTS server: Mantella xtts-api-server base + Skyrim voice latents.
# The server resolves a voice as latent_speaker_folder/<language>/<name>.json, so
# we duplicate the English latents into the languages we synthesize (ru/pt) - a
# latent is just a voice embedding, language-independent.
FROM artfromthemachine/xtts_api_server:latest
LABEL org.opencontainers.image.description="xtts-api-server-mantella + Skyrim voice latents (en+ru) + per-Sim voice upload sidecar for Mantella Sims"
COPY latent_speaker_folder/en /app/latent_speaker_folder/en
RUN cp -r /app/latent_speaker_folder/en /app/latent_speaker_folder/ru && \
    cp -r /app/latent_speaker_folder/en /app/latent_speaker_folder/pt
# Per-Sim custom voice upload: a tiny stdlib sidecar on 8021 that writes .wav
# samples into the speakers folder at runtime (xtts-api-server has no upload API).
COPY uploader.py /app/uploader.py
EXPOSE 8021
# Start the uploader alongside the server. The xtts command is IDENTICAL to the
# base image's default CMD - we only background the uploader first, so synth
# behaviour is unchanged.
CMD ["bash","-c","python3 /app/uploader.py & python3 -m xtts_api_server --listen -p 8020 -lsf 'latent_speaker_folder' -o 'output' -mf 'xtts_models' -d 'cuda' --deepspeed"]

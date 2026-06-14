# Mantella-Sims XTTS server: Mantella xtts-api-server base + Skyrim voice latents.
# The server resolves a voice as latent_speaker_folder/<language>/<name>.json, so
# we duplicate the English latents into the languages we synthesize (ru/pt) - a
# latent is just a voice embedding, language-independent.
FROM artfromthemachine/xtts_api_server:latest
LABEL org.opencontainers.image.description="xtts-api-server-mantella + Skyrim voice latents (en+ru) for Mantella Sims"
COPY latent_speaker_folder/en /app/latent_speaker_folder/en
RUN cp -r /app/latent_speaker_folder/en /app/latent_speaker_folder/ru && \
    cp -r /app/latent_speaker_folder/en /app/latent_speaker_folder/pt

FROM hashicorp/terraform:1.9

WORKDIR /workspace

# Copia solo los archivos .tf (no tfvars ni state — esos se montan en runtime)
COPY *.tf ./

# Pre-descarga el provider de OCI para no tener que bajarlo cada vez que corres el contenedor
RUN terraform providers lock \
    -platform=linux_amd64 \
    -platform=linux_arm64 \
    oracle/oci

ENTRYPOINT ["terraform"]
CMD ["--help"]

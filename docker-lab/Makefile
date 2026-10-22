IMAGE=ifs-workorder-api:dev

.PHONY: build run stop logs compose down sbom scan multiarch

build:
    docker build -t $(IMAGE) .

run:
    docker run --rm -p 9000:9000 --name ifs-api $(IMAGE)

stop:
    -@docker stop ifs-api

logs:
    docker compose logs -f

compose:
	BUILDX_BAKE_ENTITLEMENTS_FS=0 docker compose up --build

down:
    docker compose down -v

# Optional: SBOM with Syft (requires local install)
sbom:
    syft packages $(IMAGE) -o table || echo "Install syft to use this target"

# Optional: Vulnerability scan with Trivy (requires local install)
scan:
    trivy image --severity HIGH,CRITICAL $(IMAGE) || echo "Install trivy to use this target"

# Optional: multi-arch with Buildx
multiarch:
    docker buildx build --platform linux/amd64,linux/arm64 -t $(IMAGE) --load .

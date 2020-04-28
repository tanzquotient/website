# actually only for debugging the doc build locally
# the production documentation is build automatically at ReadTheDocs.org at each commit
docker-compose run -w /app/docs/sphinx --rm django sphinx-build -v . _build

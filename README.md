# pulumi openrouter provider

Manage openrouter resources via this pulumi provider generated from the [TF](https://github.com/OpenRouterTeam/terraform-provider-openrouter) one.

## Usage

### python

This is a simple exaple with poetry, add the dependency in your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
pulumi-openrouter = { git = "https://github.com/brokenpip3/pulumi-openrouter.git", tag = "v0.2.1", subdirectory = "sdk/python" }
```

### other languages

add it to your language dependency manager (go.mod, npm, etc.) and import it in your code.

## management key

To use it you need a management key from openrouter: create a key on the [Management API Keys](https://openrouter.ai/settings/management-keys)
page and save it as secret in your pulumi stack:

```sh
pulumi config set --secret openrouter:apiKey
```

## local development

From this provider repository you can use nix or mise:

```sh
nix develop # or mise install
git submodule update --init --recursive
make provider_no_deps PROVIDER_VERSION=x.x.x
./bin/pulumi-resource-openrouter
```
Leave the plugin running and note the port it prints, in another terminal replace `41549` with that port:

```sh
PULUMI_DEBUG_PROVIDERS=openrouter:41549 pulumi preview
```

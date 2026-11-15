module github.com/OpenRouterTeam/terraform-provider-openrouter/shim

go 1.26.11

replace github.com/OpenRouterTeam/terraform-provider-openrouter => ../../upstream

require (
	github.com/OpenRouterTeam/terraform-provider-openrouter v0.0.0-00010101000000-000000000000
	github.com/hashicorp/terraform-plugin-framework v1.19.0
)

require (
	github.com/fatih/color v1.18.0 // indirect
	github.com/hashicorp/go-cleanhttp v0.5.2 // indirect
	github.com/hashicorp/go-hclog v1.6.3 // indirect
	github.com/hashicorp/go-uuid v1.0.3 // indirect
	github.com/hashicorp/terraform-plugin-framework-jsontypes v0.2.0 // indirect
	github.com/hashicorp/terraform-plugin-framework-validators v0.19.0 // indirect
	github.com/hashicorp/terraform-plugin-go v0.31.0 // indirect
	github.com/hashicorp/terraform-plugin-log v0.11.0 // indirect
	github.com/mattn/go-colorable v0.1.14 // indirect
	github.com/mattn/go-isatty v0.0.20 // indirect
	github.com/mitchellh/go-testing-interface v1.14.1 // indirect
	github.com/spyzhov/ajson v0.9.0 // indirect
	github.com/vmihailenco/msgpack/v5 v5.4.1 // indirect
	github.com/vmihailenco/tagparser/v2 v2.0.0 // indirect
	golang.org/x/sys v0.49.0 // indirect
)

package shim

import (
	"github.com/hashicorp/terraform-plugin-framework/provider"

	up "github.com/OpenRouterTeam/terraform-provider-openrouter/internal/provider"
)

func OhShinyProvider(v string) provider.Provider { return up.New(v)() }

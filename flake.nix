{
  description = "openrouter pulumi provider";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, nixpkgs-unstable, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          go = nixpkgs-unstable.legacyPackages.${system}.go_1_26;
        in
        {
          default = assert pkgs.lib.versionAtLeast go.version "1.26.11";
            pkgs.mkShellNoCC {
              packages = (with pkgs; [
                bashInteractive
                cacert
                coreutils
                git
                gnumake
                python3
              ]) ++ [ go ];

              GOTOOLCHAIN = "local";
              CGO_ENABLED = "0";

              shellHook = ''
                export PATH="$PWD/bin:$PATH"
                echo "to test the provider: make provider_no_deps PROVIDER_VERSION=x.x.x"
              '';
            };
        });
    };
}

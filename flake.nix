{
  description = "wemod_launcher Flake";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    devenv.url = "github:cachix/devenv";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, devenv, ... }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
        in
        {
          packages = {
            wemod-launcher = mkPoetryApplication {
              projectDir = self;
              python = pkgs.python311Full;
              preferWheels = true;
            };
            default = self.packages.${system}.wemod-launcher;
          };

          devShells.${system} = devenv.lib.mkShell {
            inputsFrom = [ self.packages.${system}.wemod-launcher ];
            modules = [
              ({ inputs, pkgs, self, ... }: {
                imports = [ ./devenv.nix ];
              })
            ];
          };
        }) // {
      overlays.default = final: prev: {
        inherit (self.packages.${final.system}) wemod-launcher;
      };
    };
}

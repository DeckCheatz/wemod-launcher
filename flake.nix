{
  description = "wemod_launcher Flake";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-24.11";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    devenv.url = "github:cachix/devenv";
    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = inputs: let
    inherit (inputs) self;
  in
    inputs.flake-utils.lib.eachDefaultSystem
    (
      system: let
        pkgs = import inputs.nixpkgs {
          inherit system;
        };
      in {
        packages = with pkgs; {
          wemod-launcher = with python3Packages; let
            freesimplegui = let
              pname = "freesimplegui";
              version = "5.2.0.post1";
            in
              buildPythonApplication {
                inherit pname version;
                pyproject = true;
                build-system = [
                  setuptools
                ];
                src = fetchPypi {
                  inherit pname version;
                  hash = "sha256-5YoOZ1jpqehxUiVpEflPzDmYNW0TCZc6n02d8txV+Yo=";
                };
              };
            project = inputs.pyproject-nix.lib.project.loadPyproject {projectRoot = ./.;};
            python = python3Full;
            attrs = project.renderers.buildPythonPackage {inherit python;};
          in
            buildPythonApplication (
              attrs
              // {
                propagatedBuildInputs = [
                  freesimplegui
                  pyinstaller
                  pyxdg
                  requests
                  setuptools
                  tkinter
                ];
                dependencies = lib.singleton freesimplegui;
                doCheck = false;
                pythonImportsCheck = ["wemod_launcher"];
                meta = {
                  mainProgram = "wemod-launcher";
                  maintainers = with lib.maintainers; [shymega];
                };
              }
            );
          default = self.packages.${system}.wemod-launcher;
          devenv-up = self.devShells.${system}.default.config.procfileScript;
          devenv-test = self.devShells.${system}.default.config.test;
        };

        devShells.default = inputs.devenv.lib.mkShell {
          inherit inputs pkgs;
          modules = [
            ./devenv.nix
          ];
        };
      }
    )
    // {
      overlays.default = final: prev: {inherit (self.packages.${final.system}) wemod-launcher;};
    };
}

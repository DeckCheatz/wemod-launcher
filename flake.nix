{
  description = "wemod_launcher Flake";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
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

  outputs =
    { self
    , nixpkgs
    , flake-utils
    , devenv
    , pyproject-nix
    , ...
    }@inputs:
    flake-utils.lib.eachDefaultSystem
      (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          packages = with pkgs; {
            wemod-launcher =
              with python3Packages;
              let
                freesimplegui = buildPythonApplication rec {
                  pname = "freesimplegui";
                  version = "5.1.1";
                  src = fetchPypi {
                    inherit pname version;
                    sha256 = "sha256-LwlGx6wiHJl5KRgcvnUm40L/9fwpGibR1yYoel3ZZPs=";
                  };
                };
                project = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
                python = python3Full;
                attrs = project.renderers.buildPythonPackage { inherit python; };
              in
              buildPythonApplication (
                lib.recursiveUpdate attrs {
                  propagatedBuildInputs = [
                    freesimplegui
                    pyinstaller
                    pyxdg
                    requests
                    setuptools
                    tkinter
                  ];
                  dependencies = [ freesimplegui ];
                  doCheck = false;
                  pythonImportsCheck = [ "wemod_launcher" ];
                  meta = with lib; {
                    mainProgram = "wemod-launcher";
                    maintainers = with maintainers; [ shymega ];
                  };
                }
              );
            default = self.packages.${system}.wemod-launcher;
            devenv-up = self.devShells.${system}.default.config.procfileScript;
            devenv-test = self.devShells.${system}.default.config.test;
          };

          devShells.default = devenv.lib.mkShell {
            inherit inputs pkgs;
            modules = [
              (
                { pkgs
                , config
                , inputs
                , ...
                }:
                {
                  imports = [ ./devenv.nix ];
                }
              )
            ];
          };
        }
      )
    // {
      overlays.default = final: prev: { inherit (self.packages.${final.system}) wemod-launcher; };
    };
}

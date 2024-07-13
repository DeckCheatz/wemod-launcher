{ pkgs, ... }:
{
  packages = [
    pkgs.pyright
    pkgs.poetry
    pkgs.git
  ];

  languages = {
    nix.enable = true;
    python = {
      enable = true;
      package = pkgs.python311Full;
      poetry = {
        enable = true;
        activate.enable = true;
        install = {
          enable = true;
          allExtras = true;
          compile = true;
          quiet = true;
        };
      };
    };
    shell.enable = true;
  };

  difftastic.enable = true;
  devcontainer.enable = true;

  pre-commit.hooks = {
    shellcheck.enable = true;
    shfmt.enable = true;
    # FIXME: Fix Flake8 lints.
    #    flake8.enable = true;
    actionlint.enable = true;
    nixpkgs-fmt.enable = true;
    black = {
      enable = true;
      settings.flags = "-l 78 -t py312";
    };
    # FIXME: Fix Markdown lints.
    #    markdownlint.enable = true;
    statix.enable = true;
  };
}

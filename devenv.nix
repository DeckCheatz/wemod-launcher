{
  pkgs,
  self,
  inputs,
  ...
}: let
  freesimplegui = let
    pname = "freesimplegui";
    version = "5.2.0.post1";
  in
    pkgs.python3Packages.buildPythonApplication {
      inherit pname version;
      pyproject = true;
      build-system = [
        pkgs.python3Packages.setuptools
      ];
      src = pkgs.python3Packages.fetchPypi {
        inherit pname version;
        hash = "sha256-5YoOZ1jpqehxUiVpEflPzDmYNW0TCZc6n02d8txV+Yo=";
      };
    };
in {
  packages = with pkgs;
    [
      git
      pdm
      pyright
    ]
    ++ (with pkgs.python3Packages; [
      requests
      pyxdg
      setuptools
      pyinstaller
      tkinter
    ])
    ++ pkgs.lib.singleton freesimplegui;

  languages = {
    nix.enable = true;
    python = {
      enable = true;
      package = pkgs.python313Full;
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
    alejandra.enable = true;
    black = {
      enable = true;
      settings.flags = "-l 78 -t py312";
    };
    # FIXME: Fix Markdown lints.
    #    markdownlint.enable = true;
    statix.enable = true;
  };

  enterShell = ''
    export TK_LIBRARY="${pkgs.tk.outPath}/lib/${pkgs.tk.libPrefix}"
    export TCL_LIBRARY="${pkgs.tcl.outPath}/lib/${pkgs.tcl.libPrefix}"
  '';
}

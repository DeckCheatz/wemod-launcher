{ pkgs
, self
, inputs
, ...
}:
let
  freesimplegui = pkgs.python3Packages.buildPythonApplication rec {
    pname = "freesimplegui";
    version = "5.1.1";
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-LwlGx6wiHJl5KRgcvnUm40L/9fwpGibR1yYoel3ZZPs=";
    };
  };
in
{
  packages =
    with pkgs;
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
    ]) ++ [ freesimplegui ];

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
    nixpkgs-fmt.enable = true;
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

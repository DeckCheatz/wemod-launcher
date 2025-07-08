{
  description = "wemod_launcher Flake";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-25.05";
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
          wemod-launcher = let
            python = python312;
            pythonPackages = python.pkgs;
            project = inputs.pyproject-nix.lib.project.loadPyproject {projectRoot = ./.;};
            attrs = project.renderers.buildPythonPackage {inherit python;};
          in
            pythonPackages.buildPythonApplication (
              attrs
              // {
                propagatedBuildInputs = with pythonPackages; [
                  # Qt6 GUI dependencies - pin to avoid version conflicts
                  pyqt6
                  # Core dependencies
                  requests
                  pyxdg
                  click
                  # Build dependencies
                  setuptools
                  pyinstaller
                ];
                # Set Qt plugin paths and library paths for proper Qt operation
                makeWrapperArgs = [
                  "--set QT_QPA_PLATFORM_PLUGIN_PATH ${qt6.qtbase}/lib/qt-6/plugins/platforms"
                  "--set QT_PLUGIN_PATH ${qt6.qtbase}/lib/qt-6/plugins"
                  "--prefix LD_LIBRARY_PATH : ${lib.makeLibraryPath [qt6.qtbase qt6.qtwayland]}"
                ];
                doCheck = false;
                pythonImportsCheck = ["wemod_launcher"];
                meta = {
                  description = "Tool to launch WeMod with games on Steam Deck/Linux";
                  homepage = "https://github.com/DeckCheatz/wemod-launcher";
                  license = lib.licenses.mit;
                  mainProgram = "wemod-launcher";
                  maintainers = with lib.maintainers; [shymega];
                  platforms = lib.platforms.linux;
                };
              }
            );
          # Development version with extra tools
          wemod-launcher-dev = let
            python = python312;
            pythonPackages = python.pkgs;
            project = inputs.pyproject-nix.lib.project.loadPyproject {projectRoot = ./.;};
            attrs = project.renderers.buildPythonPackage {inherit python;};
          in
            pythonPackages.buildPythonApplication (
              attrs
              // {
                propagatedBuildInputs = with pythonPackages; [
                  # Qt6 GUI dependencies - pin to avoid version conflicts
                  pyqt6
                  # Core dependencies
                  requests
                  pyxdg
                  setuptools
                  pyinstaller
                  click
                  # Development dependencies
                  pytest
                  black
                  flake8
                  mypy
                ];
                # Set Qt plugin paths and library paths for proper Qt operation
                makeWrapperArgs = [
                  "--set QT_QPA_PLATFORM_PLUGIN_PATH ${qt6.qtbase}/lib/qt-6/plugins/platforms"
                  "--set QT_PLUGIN_PATH ${qt6.qtbase}/lib/qt-6/plugins"
                  "--prefix LD_LIBRARY_PATH : ${lib.makeLibraryPath [qt6.qtbase qt6.qtwayland]}"
                ];
                doCheck = true;
                checkInputs = with pythonPackages; [pytest];
                pythonImportsCheck = ["wemod_launcher"];
                meta = {
                  description = "Tool to launch WeMod with games on Steam Deck/Linux (development version)";
                  homepage = "https://github.com/DeckCheatz/wemod-launcher";
                  license = lib.licenses.mit;
                  mainProgram = "wemod-launcher";
                  maintainers = with lib.maintainers; [shymega];
                  platforms = lib.platforms.linux;
                };
              }
            );

          # Real AppImage build - creates a proper .AppImage file
          wemod-launcher-appimage = let
            wrapped = self.packages.${system}.wemod-launcher;

            # Get AppImage runtime from a known, deterministic source
            appimage-runtime = pkgs.fetchurl {
              url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/runtime-x86_64";
              sha256 = "sha256-q01r9vJbvLD6kkkelQBz/UqeTuoa8PugzJ5TtmtYExI="; # Current hash
              executable = true;
            };

            # Create AppDir structure
            appDir =
              pkgs.runCommand "wemod-launcher-appdir" {
                nativeBuildInputs = with pkgs; [
                  imagemagick
                  coreutils
                  findutils
                  bash
                  desktop-file-utils
                ];
              } ''
                              set -e
                              echo "Creating AppDir structure for AppImage..."

                              # Create AppDir structure
                              mkdir -p $out/usr/bin
                              mkdir -p $out/usr/lib
                              mkdir -p $out/usr/share/applications
                              mkdir -p $out/usr/share/icons/hicolor/256x256/apps

                              # Copy the main executable
                              echo "Copying main executable..."
                              cp ${wrapped}/bin/wemod-launcher $out/usr/bin/
                              chmod +x $out/usr/bin/wemod-launcher

                              # Copy Python and its dependencies
                              echo "Copying Python runtime and dependencies..."
                              cp -L ${python312}/bin/python* $out/usr/bin/ || true

                              # Copy the Python site-packages from our wrapped application
                              if [ -d "${wrapped}/lib" ]; then
                                cp -r ${wrapped}/lib/* $out/usr/lib/ || true
                              fi

                              # Copy Qt6 plugins directory
                              echo "Copying Qt6 plugins..."
                              mkdir -p $out/usr/lib/qt6
                              if [ -d "${qt6.qtbase}/lib/qt-6/plugins" ]; then
                                cp -r "${qt6.qtbase}/lib/qt-6/plugins" $out/usr/lib/qt6/
                              fi

                              # Copy essential Qt6 libraries
                              echo "Copying Qt6 libraries..."
                              mkdir -p $out/usr/lib
                              for lib in libQt6Core.so.6 libQt6Gui.so.6 libQt6Widgets.so.6; do
                                if [ -f "${qt6.qtbase}/lib/$lib" ]; then
                                  cp -L "${qt6.qtbase}/lib/$lib" $out/usr/lib/ || echo "Warning: Failed to copy $lib"
                                fi
                              done

                              # Copy Wayland support if available
                              if [ -f "${qt6.qtwayland}/lib/libQt6WaylandClient.so.6" ]; then
                                cp -L "${qt6.qtwayland}/lib/libQt6WaylandClient.so.6" $out/usr/lib/ || true
                              fi

                              # Copy other essential libraries
                              echo "Copying other essential libraries..."
                              for lib in "${lib.makeLibraryPath [qt6.qtbase qt6.qtwayland]}"; do
                                if [ -d "$lib" ]; then
                                  cp -L $lib/*.so* $out/usr/lib/ 2>/dev/null || true
                                fi
                              done

                              # Create desktop entry (required by AppImage spec)
                              echo "Creating desktop entry..."
                              cat > $out/wemod-launcher.desktop << 'EOF'
                [Desktop Entry]
                Type=Application
                Name=WeMod Launcher
                Comment=Tool to launch WeMod with games on Steam Deck/Linux
                Exec=wemod-launcher
                Icon=wemod-launcher
                Categories=Game;Utility;
                Keywords=gaming;steam-deck;wine;cheats;wemod;
                StartupNotify=true
                EOF

                              # Validate desktop file
                              desktop-file-validate $out/wemod-launcher.desktop || echo "Warning: Desktop file validation failed"

                              # Copy to standard location (AppImage spec requirement)
                              cp $out/wemod-launcher.desktop $out/usr/share/applications/

                              # Create icon (required by AppImage spec)
                              echo "Creating icon..."
                              convert -size 256x256 xc:"#4A90E2" \
                                -pointsize 48 -fill white -gravity center \
                                -annotate +0+0 "WM" \
                                $out/wemod-launcher.png || echo "Warning: Icon creation failed"

                              # Copy icon to proper location
                              if [ -f "$out/wemod-launcher.png" ]; then
                                cp $out/wemod-launcher.png $out/usr/share/icons/hicolor/256x256/apps/
                              fi

                              # Create AppRun script (required by AppImage spec)
                              echo "Creating AppRun script..."
                              cat > $out/AppRun << 'APPRUN_EOF'
                #!/bin/bash
                HERE="$(dirname "$(readlink -f "$0")")"
                export QT_QPA_PLATFORM_PLUGIN_PATH="$HERE/usr/lib/qt6/plugins/platforms"
                export QT_PLUGIN_PATH="$HERE/usr/lib/qt6/plugins"
                export LD_LIBRARY_PATH="$HERE/usr/lib:$LD_LIBRARY_PATH"
                export PYTHONPATH="$HERE/usr/lib:$PYTHONPATH"
                exec "$HERE/usr/bin/wemod-launcher" "$@"
                APPRUN_EOF

                              chmod +x $out/AppRun

                              echo "AppDir creation completed successfully!"
                              ls -la $out/
              '';
          in
            # Create a real AppImage using deterministic tools
            pkgs.runCommand "wemod-launcher.AppImage" {
              nativeBuildInputs = with pkgs; [
                squashfsTools
                file
                coreutils
              ];
            } ''
              set -e
              echo "Creating AppImage from AppDir..."

              # Copy the AppDir to a writable location
              cp -r ${appDir} ./AppDir
              chmod -R u+w ./AppDir

              # Ensure AppRun is at the root of AppDir
              if [ ! -f ./AppDir/AppRun ]; then
                echo "Error: AppRun not found!"
                exit 1
              fi

              # Create squashfs filesystem from AppDir
              echo "Creating squashfs filesystem..."
              mksquashfs ./AppDir filesystem.squashfs -root-owned -noappend -no-exports -comp gzip

              # Combine runtime and squashfs to create AppImage
              echo "Combining runtime and squashfs..."
              cat ${appimage-runtime} filesystem.squashfs > $out
              chmod +x $out

              # Verify the AppImage
              echo "AppImage created successfully!"
              echo "File info:"
              file $out
              echo "Size: $(du -h $out | cut -f1)"

              # Test that it's executable
              if [ -x "$out" ]; then
                echo "AppImage is executable ✓"
              else
                echo "Error: AppImage is not executable!"
                exit 1
              fi
            '';

          # Development environment for PyInstaller builds
          wemod-launcher-build-env = writeShellScriptBin "wemod-launcher-build-env" ''
            echo "WeMod Launcher Build Environment"
            echo "Available commands:"
            echo "  pyinstaller wemod-launcher.spec  # Build executable"
            echo "  python -m wemod_launcher.cli     # Run from source"
            echo ""
            echo "Current directory: $(pwd)"
            echo "Python path: ${python312}/bin/python"
            echo "PyInstaller path: ${python312.pkgs.pyinstaller}/bin/pyinstaller"

            # Launch shell with proper environment
            exec ${pkgs.bash}/bin/bash
          '';
          default = self.packages.${system}.wemod-launcher;
          devenv-up = self.devShells.${system}.default.config.procfileScript;
          devenv-test = self.devShells.${system}.default.config.test;
        };

        # Apps for easy execution
        apps = {
          wemod-launcher = {
            type = "app";
            program = "${self.packages.${system}.wemod-launcher}/bin/wemod-launcher";
          };
          appimage = {
            type = "app";
            program = "${self.packages.${system}.wemod-launcher-appimage}";
          };
          build-env = {
            type = "app";
            program = "${self.packages.${system}.wemod-launcher-build-env}/bin/wemod-launcher-build-env";
          };
          default = self.apps.${system}.wemod-launcher;
        };

        devShells.default = inputs.devenv.lib.mkShell {
          inherit inputs pkgs;
          modules = [
            ({
              pkgs,
              inputs,
              ...
            }: {
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
                  pyqt6
                  click
                ]);

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
            })
          ];
        };
      }
    )
    // {
      overlays.default = final: prev: {
        inherit
          (self.packages.${final.system})
          wemod-launcher
          wemod-launcher-dev
          wemod-launcher-appimage
          wemod-launcher-build-env
          ;
      };
    };
}

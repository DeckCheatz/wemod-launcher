# SPDX-FileCopyrightText: 2023 Dom Rodriguez <shymega@shymega.org.uk>
# SPDX-License-Identifier: AGPL-3.0-only

(import
  (
    let
      lock = builtins.fromJSON (builtins.readFile ./tools/nix/flake.lock);
    in
    fetchTarball {
      url = "https://github.com/edolstra/flake-compat/archive/${lock.nodes.flake-compat.locked.rev}.tar.gz";
      sha256 = lock.nodes.flake-compat.locked.narHash;
    }
  )
  { src = ./.; }).shellNix

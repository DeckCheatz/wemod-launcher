# SPDX-FileCopyrightText: 2024 The DeckCheatz Developers
#
# SPDX-License-Identifier: Apache-2.0
(
  import
  (
    let
      lock = builtins.fromJSON (builtins.readFile ./flake.lock);
    in
<<<<<<< HEAD
      fetchTarball {
        url = "https://github.com/edolstra/flake-compat/archive/${lock.nodes.flake-compat.locked.rev}.tar.gz";
        sha256 = lock.nodes.flake-compat.locked.narHash;
      }
  )
  {src = ./.;}
)
.defaultNix
=======
    fetchTarball {
      url = "https://github.com/edolstra/flake-compat/archive/${lock.nodes.flake-compat.locked.rev}.tar.gz";
      sha256 = lock.nodes.flake-compat.locked.narHash;
    }
  )
  { src = ./.; }).defaultNix
>>>>>>> 6e7adfa (chore: Run lints on Nix files)

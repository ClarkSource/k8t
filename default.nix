with import <nixpkgs> {};

pkgs.mkShell {
  buildInputs = [
    pre-commit
  ];

  shellHook = ''
    export PATH="$PATH:$HOME/.yarn/bin"
  '';
}

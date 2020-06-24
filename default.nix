with import <nixpkgs> {};

let
  pythonEnv = python38.withPackages (ps: [
    ps.nodeenv
  ]);
in pkgs.mkShell {
  buildInputs = [
    pre-commit
    pythonEnv
  ];

  shellHook = ''
    export PATH="$PATH:$HOME/.yarn/bin"
  '';
}

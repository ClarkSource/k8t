{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.pre-commit
    pkgs.python3.pkgs.virtualenv
  ];
}

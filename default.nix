let
  unstable = import (fetchTarball https://nixos.org/channels/nixos-unstable/nixexprs.tar.xz) {};
in
{ pkgs ? import <nixpkgs> {} }:

  let
    simple_tools = pkgs.python3.pkgs.buildPythonPackage rec {
      pname = "simple_tools";
      version = "0.2.0.post2";

      src = pkgs.python3.pkgs.fetchPypi {
        inherit pname version;
        sha256 = "16xxpsngv76fzsxji1714m7b6b74wk459sjs8p15nj8h4xy0b7b9";
      };

      doCheck = false;

      meta = {
        homepage = "https://github.com/afriemann/simple_tools/";
        description = "A collection of various snippets and tools that come up regularly.";
      };
    };

    k8t = pkgs.python3.pkgs.buildPythonApplication rec {
      pname = "k8t";
      version = "dev";

      src = ./.;

      # No tests included
      doCheck = false;

      nativeBuildInputs = with pkgs; [
        git
      ];

      propagatedBuildInputs = with pkgs.python3.pkgs; [
        jinja2
        coloredlogs
        boto3
        pyyaml
        click
        simple_tools
        ujson
        setuptools
      ];

      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/clarksource/k8t";
        license = licenses.isc;
      };
    };
  in
    pkgs.mkShell {
      buildInputs = [
        k8t
        unstable.pre-commit
        unstable.python3.pkgs.tox
      ];
    }

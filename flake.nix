{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-20.09";

  outputs = {
    self,
    nixpkgs,
    ...
    } @ inputs:
  let
    systems = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f {
      inherit system;
      pkgs = nixpkgs.legacyPackages.${system};
    });
    mkPythonEnv = pkgs: extraPackages: with pkgs; python.withPackages (ps: with ps; [
      pygame
      #numpy
      (buildPythonPackage {
        # pkgs.cwiid is built with mkDerivation and --without-python
        inherit (cwiid) name src NIX_LDFLAGS meta;
        preBuild = "cd python";
        buildInputs = cwiid.buildInputs ++ [ cwiid ];
        nativeBuildInputs = cwiid.nativeBuildInputs ++ cwiid.buildInputs;
        doCheck = false;
      })
    ] ++ extraPackages);
  in {
    inherit inputs;

    packages = forAllSystems ({ pkgs, ... }: rec {
      wiiteboard = pkgs.writeScriptBin "wiiteboard" ''
        #!${pkgs.bash}/bin/bash
        cd ${./.}
        exec ${mkPythonEnv pkgs []}/bin/python main.py
      '';
      default = wiiteboard;
    });

    apps = forAllSystems ({ system, ... }: rec {
      wiiteboard.type = "app";
      wiiteboard.program = "${self.packages.${system}.wiiteboard}/bin/wiiteboard";
      default = wiiteboard;
    });

    devShells = forAllSystems ({ pkgs, ... }: {
      default = pkgs.mkShell {
        buildInputs = [ (mkPythonEnv pkgs [ pkgs.pythonPackages.pillow ]) ];
      };
    });

  };
}

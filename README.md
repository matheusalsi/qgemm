# Set Chipyard Conda env
```bash
source ./env.sh
```

# Functional Simulation

Navigate to the desired simulator directory (`verilator`, `vcs`, or `xcelium`):

```bash
cd chipyard/sims/<simulator>
make CONFIG=GemminiINT4RocketConfig 
```

```bash
cd chipyard/sims/<simulator>
make CONFIG=GemminiINT4RocketConfig run-binary BINARY=../../generators/gemmini/software/gemmini-rocc-tests/build/imagenet/resnet50-baremetal TIMEOUT_CYCLES=0 LOADMEM=1
```

# VLSI FLOW
## Enviroment Setup
Substitua <pdk> por sky130 ou asap7

```bash
cd chipyard/scripts
./init-vlsi.sh <pdk>
```
## VLSI Flow Setup
In ``chipyard/vlsi/``, edit the ``env.yml`` to setup commercial tools.
```yml
# Base path to where Mentor tools are installed
mentor.mentor_home: ""
# Mentor license server/file
mentor.MGLS_LICENSE_FILE: ""
# Base path to where Cadence tools are installed
cadence.cadence_home: "/tools/cadence"
# Cadence license server/file
cadence.CDS_LIC_FILE: "5280@pgmicro01.ufrgs.br:27010@pgmicro01.ufrgs.br"
# Base path to where Synopsys tools are installed
synopsys.synopsys_home: ""
# Synopsys license server/files
synopsys.SNPSLMD_LICENSE_FILE: ""
synopsys.MGLS_LICENSE_FILE: ""
```

### Tools YML Examples
- OpenRoad in ``example-openroad.yml``
```yml
synthesis.yosys.yosys_bin: /home/inf01185/matheus.almeida/.conda-yosys/bin/yosys
par.openroad.openroad_bin: /home/inf01185/matheus.almeida/.conda-openroad/bin/openroad
par.openroad.klayout_bin: /home/inf01185/matheus.almeida/.conda-klayout/bin/klayout  
drc.klayout.klayout_bin: /home/inf01185/matheus.almeida/.conda-klayout/bin/klayout  
drc.magic.magic_bin: /home/inf01185/matheus.almeida/.conda-signoff/bin/magic
lvs.netgen.netgen_bin: /home/inf01185/matheus.almeida/.conda-signoff/bin/netgen
```

- Cadence Tools in ``example-tools.yml``
```yml
synthesis.yosys.yosys_bin: /home/inf01185/matheus.almeida/.conda-yosys/bin/yosys
par.openroad.openroad_bin: /home/inf01185/matheus.almeida/.conda-openroad/bin/openroad
par.openroad.klayout_bin: /home/inf01185/matheus.almeida/.conda-klayout/bin/klayout  
drc.klayout.klayout_bin: /home/inf01185/matheus.almeida/.conda-klayout/bin/klayout  
drc.magic.magic_bin: /home/inf01185/matheus.almeida/.conda-signoff/bin/magic
lvs.netgen.netgen_bin: /home/inf01185/matheus.almeida/.conda-signoff/bin/netgen
```
### PDK YML Example
To setup SKY130 PDK, go to ``example-sky130.yml`` and add the PDK paths.
```yml
# Technology paths
technology.sky130:
  sky130A: "/pdk/skywater/sky130/sky130A/"
  sram22_sky130_macros: "/home/inf01185/matheus.almeida/sram22_sky130_macros"
```

## VLSI Flow Run
```bash
make buildfile tutorial=sky130-commercial tech_name=sky130
make syn tutorial=sky130-commercial tech_name=sky130
make par tutorial=sky130-commercial tech_name=sky130

```

